from typing import List, Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from tortoise.contrib.fastapi import register_tortoise
from Logic import *
from fastapi import Response, HTTPException
import pandas as pd
import io
from fastapi.responses import StreamingResponse

DBurl = "mysql://root:K423@localhost:3306/suspendedstudents?minsize=5&maxsize=10"
app = FastAPI()

# Replace your lifespan/manual init with this
register_tortoise(
    app,
    db_url=DBurl,
    modules={"models": ["datamodels"]},
    generate_schemas=False,
    add_exception_handlers=True,
)

app.mount("/static", StaticFiles(directory="statics"), name="statics")

templates = Jinja2Templates(directory="templates")

######################################-Pages-########################################


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/Admin/{page}", response_class=HTMLResponse)
async def MainA(page: str, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        #raise
        return templates.TemplateResponse(request=request, name="index.html")
    if payload.get("id") != 1:
        #raise HTTPException(status_code=403, detail="Forbidden: Admins only")
        return templates.TemplateResponse(request=request, name="index.html")
    return templates.TemplateResponse(request=request, name=f"Admin/{page}.html")


@app.get("/User/{page}", response_class=HTMLResponse)
async def MainU(request: Request, page: str):
    token = request.cookies.get("Token")
    if not token:
        #raise HTTPException(status_code=401, detail="Not authenticated")
        return templates.TemplateResponse(request=request, name="index.html")
    try:
        tokenCheck(token)
        return templates.TemplateResponse(request=request, name=f"User/{page}.html")
    except HTTPException:
        #raise
        return templates.TemplateResponse(request=request, name="index.html")


####################################-Account-Ops-########################################


class LoginRequest(BaseModel):
    cred: str
    password: str


class Password(BaseModel):
    password: str


@app.post("/login")
async def login(body: LoginRequest, response: Response):
    try:
        result = await login_process(cred=body.cred, password=body.password)
        response.set_cookie(
            key="Token",
            value=result["Token"],
            httponly=True,
            samesite="lax",
            secure=False,
        )
        return {"college": result["college"]}
    except HTTPException:
        raise

@app.get("/get_users")
async def getUsersList(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    try:
        return await get_users_admin()
    except HTTPException:
        raise


@app.delete("/delete_user/{account_id}")
async def deleteUser(account_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_user(account_id, body.password)
    except HTTPException:
        raise


class AddUserRequest(BaseModel):
    cred: str
    password: str
    college: str


@app.post("/add_user")
async def addUser(body: AddUserRequest, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    try:
        await add_user(cred=body.cred, password=body.password, college=body.college)
    except HTTPException:
        raise


@app.patch("/change_pass_user/{account_id}")
async def changePassword(account_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await change_user_password(account_id, body.password)
    except HTTPException:
        raise

####to be done###
@app.patch("/toggle_user/{account_id}")
async def toggleUser(account_id: int, request: Request, enable: bool):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await toggle_user(account_id, enable)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])

####to be done###
@app.patch("/toggle_all_users")
async def toggleAllUsers(request: Request, enable: bool):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await toggle_all_users(enable)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])


#################################################-Files-##################################################


@app.get("/download_excel")
async def downloadExcel(request: Request, year: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        records = []
    else:
        records = await get_data_for_excel(year=year)

    if not records or len(records) == 0:
        raise HTTPException(status_code=404, detail="No records found")

    df = pd.DataFrame(records)
    if "id" in df.columns:
        df = df.drop(columns=["id"])

    if "AcceptionYear" in df.columns:
        df["AcceptionYear"] = df["AcceptionYear"].apply(lambda y: f"{y}-{y+1}")
    if "SuspensionYear" in df.columns:
        df["SuspensionYear"] = df["SuspensionYear"].apply(lambda y: f"{y}-{y+1}")

    if "RequestYear" in df.columns:
        df["RequestYear"] = df["RequestYear"].apply(lambda y: f"{y}-{y+1}")

    benefactor_map = {Flag.Yes: "نعم", Flag.No: "لا"}

    if "benefactor" in df.columns:
        df["benefactor"] = df["benefactor"].apply(lambda x: benefactor_map.get(x, x))

    RequestStatus_map = {
        RequestStatus.PENDING: "قيد الانتظار",
        RequestStatus.ACCEPTED: "مقبول",
        RequestStatus.DENIED: "مرفوض",
    }

    if "RequestStatus" in df.columns:
        df["RequestStatus"] = df["RequestStatus"].apply(
            lambda x: RequestStatus_map.get(x, x)
        )

    header_map = {
        "StudentName": "اسم الطالب",
        "BirthDate": "التولد",
        "college": "الكلية",
        "department": "القسم",
        "speciality": "التخصص",
        "study": "المرحلة الدراسية",
        "AcceptionYear": "سنة القبول",
        "SuspensionYear": "سنة الترقين",
        "SuspensionReason": "سبب لبترقين",
        "jobstatus": "الموقف الوظيفي",
        "RequestStatus": "حالة الطلب",
        "status": "موقف الطلب",
        "benefactor": "مستفيد سابقا",
        "RequestYear": "العام الدراسي الحالي",
    }

    df.rename(columns=header_map, inplace=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Students")

    output.seek(0)

    # 5. Return as a downloadable file
    headers = {"Content-Disposition": 'attachment; filename="student_records.xlsx"'}
    return StreamingResponse(
        output,
        headers=headers,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


##############################################-filters-Items-#######################################################


@app.get("/get_colleges_list")
async def get_colleges_list(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)
    except HTTPException:
        raise

    return await get_colleges()


@app.get("/get_years_list")
async def get_years_list(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)

    except HTTPException:
        raise

    return await get_years()


#######################################################-Admin-OPs-################################################################


@app.get("/get_requests_admin")
async def getRequestsAdmin(
    request: Request,
    status: Optional[str] = None,
    year: Optional[int] = None,
    college: Optional[str] = None,
):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_requests_admin(status=status, year=year, college=college)
    except HTTPException:
        raise


#######################################################colleges-ops############################################

@app.get("/get_colleges_admin")
async def getCollegesAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        return await get_colleges_admin()
    except HTTPException:
        raise

class AddCollegeRequest(BaseModel):
    name: str   

@app.post("/add_college_admin")
async def addCollegeAdmin(request: Request, body: AddCollegeRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        await add_college_admin(name=body.name)
    except HTTPException:
        raise

@app.delete("/delete_college_admin/{college_id}")
async def deleteCollegeAdmin(college_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        await delete_college_admin(college_id=college_id, password=body.password)
    except HTTPException:
        raise

######################################################department-op#####################################

@app.get("/get_departments_admin")
async def getDepartmentsAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        return await get_departments_admin()
    except HTTPException:
        raise

class AddDepartmentRequest(BaseModel):
    name: str
    college: int    

@app.post("/add_department_admin")
async def addDepartmentAdmin(request: Request, body: AddDepartmentRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        await add_department_admin(name=body.name, college_id=body.college)
    except HTTPException:
        raise

@app.delete("/delete_department_admin/{department_id}")
async def deleteDepartmentAdmin(department_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    
    try:
        await delete_department_admin(department_id=department_id, password=body.password)
    except HTTPException:
        raise


######################################-Non-Admin-OPs-################################


######################################################################


@app.get("/stats")
async def getStats(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") == 1:
        return await get_stats()
    return {"message": "tbd"}


@app.get("/logo")
async def getLogo():
    return FileResponse("Logo.png", media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)
