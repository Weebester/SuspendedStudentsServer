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


@app.get("/MainAdmin", response_class=HTMLResponse)
async def MainA(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return templates.TemplateResponse(request=request, name="MainAdmin.html")


@app.get("/OptionsAdmin", response_class=HTMLResponse)
async def OptionsA(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return templates.TemplateResponse(request=request, name="OptionsAdmin.html")


@app.get("/RequestsAdmin", response_class=HTMLResponse)
async def RequestsA(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return templates.TemplateResponse(request=request, name="RequestsAdmin.html")


@app.get("/AccountsAdmin", response_class=HTMLResponse)
async def AccountsA(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return templates.TemplateResponse(request=request, name="AccountsAdmin.html")

@app.get("/OptionsAdmin/College", response_class=HTMLResponse)
async def OptionsCollege(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return templates.TemplateResponse(request=request, name="CollegesOptions.html")


#############################################################################


@app.get("/MainUser", response_class=HTMLResponse)
async def MainU(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)
        return templates.TemplateResponse(request=request, name="MainUser.html")
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")


####################################-Account-Ops-########################################


class LoginRequest(BaseModel):
    cred: str
    password: str


@app.post("/Login")
async def login_route(body: LoginRequest, response: Response):
    result = await Login(cred=body.cred, password=body.password)
    if result["success"]:

        response.set_cookie(
            key="Token",
            value=result["Token"],
            httponly=True,
            samesite="lax",
            secure=False,
        )
        return {"college": result["college"]}
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])


@app.delete("/delete_user/{account_id}")
async def delete_account(account_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await delete_user(account_id)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])


class AddUserRequest(BaseModel):
    cred: str
    password: str
    college: str


@app.post("/add_user")
async def add_account(body: AddUserRequest, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await add_user(
        cred=body.cred, password=body.password, college=body.college
    )

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])

@app.patch  ("/toggle_user/{account_id}")
async def toggle_user(account_id: int, request: Request, enable: bool):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await toggle_user_status(account_id, enable)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])

@app.patch("/toggle_all_users")
async def toggle_all_users(request: Request, enable: bool):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    result = await toggle_all_users_status(enable)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=result["status_code"], detail=result["message"])
#################################################-Files-##################################################


@app.get("/download-excel")
async def download_excel(request: Request, year: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        records = []
    else:
        records = await get_data_for_excel(year=year)

    if not records or len(records) == 0:
        raise HTTPException(status_code=404, detail="No records found")

    # 2. Convert to DataFrame and drop 'id'
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
        raise HTTPException(status_code=401, detail="Invalid token")

    return await get_colleges()


@app.get("/get_years_list")
async def get_years_list(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    return await get_years()


@app.get("/get_colleges_list")
async def get_colleges_list(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    return await get_colleges()


#######################################################-Admin-OPs-################################################################


@app.get("/requestsAdmin")
async def requests(
    request: Request,
    page: Optional[int] = None,
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
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return await get_requests_Admin(
        page=page, status=status, year=year, college=college
    )


@app.get("/get_users_list")
async def get_users_list(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("id") != 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    return await get_users()



######################################-Non-Admin-OPs-################################


######################################################################

@app.get("/Stats")
async def MainU(request: Request):
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
async def get_logo():
    return FileResponse("Logo.png", media_type="image/png")


if __name__ == "__main__":
    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)
