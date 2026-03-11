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


#####################################################################################################
##############################################-Pages-################################################
#####################################################################################################


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
        return templates.TemplateResponse(request=request, name="index.html")
    if payload.get("college_id") > 1:
        return templates.TemplateResponse(request=request, name="index.html")
    return templates.TemplateResponse(request=request, name=f"Admin/{page}.html")


@app.get("/User/{page}", response_class=HTMLResponse)
async def MainU(request: Request, page: str):
    token = request.cookies.get("Token")
    if not token:
        # raise HTTPException(status_code=401, detail="Not authenticated")
        return templates.TemplateResponse(request=request, name="index.html")
    try:
        tokenCheck(token)
        return templates.TemplateResponse(request=request, name=f"User/{page}.html")
    except HTTPException:
        # raise
        return templates.TemplateResponse(request=request, name="index.html")


#####################################################################################################
####################################-Accounts-Ops-###################################################
#####################################################################################################


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
        return {"college_id": result["college_id"]}
    except HTTPException:
        raise


@app.get("/get_users")
async def getUsersList(request: Request, college_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    try:
        return await get_users(college_id=college_id)
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

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_user(account_id, body.password)
    except HTTPException:
        raise


class AddUserRequest(BaseModel):
    cred: str
    password: str
    college_id: int


@app.post("/add_user")
async def addUser(body: AddUserRequest, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")
    try:
        await add_user(
            cred=body.cred, password=body.password, college_id=body.college_id
        )
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

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await change_user_password(account_id, body.password)
    except HTTPException:
        raise


@app.patch("/toggle_user/{account_id}")
async def toggleUser(account_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_user(account_id)
    except HTTPException:
        raise


@app.patch("/toggle_all_users")
async def toggleAllUsers(request: Request, enable: bool):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_all_users(enable)
    except HTTPException:
        raise


#####################################################################################################
####################################-UNcatogerized-##################################################
#####################################################################################################


@app.get("/get_years_admin")
async def getYearsAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        tokenCheck(token)

    except HTTPException:
        raise

    return await get_years()


#######################################################################################################################


@app.get("/get_requests")
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

    try:
        if payload.get("college_id") < 2:
            return await get_requests(status=status, year=year, college_id=college)
        else:
            return await get_requests(status=status, college_id=payload.get("id"))
    except HTTPException:
        raise


#####################################################################################################
#############################################colleges-ops############################################
#####################################################################################################


@app.get("/get_colleges_admin")
async def getCollegesAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
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

    if payload.get("college_id") > 1:
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

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_college_admin(college_id=college_id, password=body.password)
    except HTTPException:
        raise


class Rename(BaseModel):
    new_name: str


@app.patch("/rename_college_admin/{college_id}")
async def renameCollegeAdmin(college_id: int, request: Request, body: Rename):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await rename_college_admin(college_id=college_id, new_name=body.new_name)
    except HTTPException:
        raise


#####################################################################################################
########################################-department-ops-#############################################
#####################################################################################################


@app.get("/get_departments_admin")
async def getDepartmentsAdmin(request: Request, college_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_departments_admin(college_id=college_id)
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

    if payload.get("college_id") > 1:
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

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_department_admin(
            department_id=department_id, password=body.password
        )
    except HTTPException:
        raise


@app.patch("/toggle_department_admin/{department_id}")
async def toggleDepartmentAdmin(department_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_department_admin(department_id)
    except HTTPException:
        raise


#####################################################################################################
###########################################-Study-ops-############################################
#####################################################################################################


@app.get("/get_study_admin")
async def getStudyAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_study_admin()
    except HTTPException:
        raise


class AddStudyRequest(BaseModel):
    name: str


@app.post("/add_study_admin")
async def addStudyAdmin(request: Request, body: AddStudyRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_study_admin(name=body.name)
    except HTTPException:
        raise


@app.delete("/delete_study_admin/{study_id}")
async def deleteStudyAdmin(study_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_study_admin(study_id=study_id, password=body.password)
    except HTTPException:
        raise


@app.patch("/toggle_study_admin/{study_id}")
async def toggleStudyAdmin(study_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_study_admin(study_id)
    except HTTPException:
        raise


#####################################################################################################
########################################-Sub-Study-ops-#############################################
#####################################################################################################


@app.get("/get_sub_study_admin")
async def getSubStudyAdmin(request: Request, study_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_sub_study_admin(study_id=study_id)
    except HTTPException:
        raise


class AddSubStudyRequest(BaseModel):
    name: str
    study: int


@app.post("/add_sub_study_admin")
async def addSubStudyAdmin(request: Request, body: AddSubStudyRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_sub_study_admin(name=body.name, study_id=body.study)
    except HTTPException:
        raise


@app.delete("/delete_sub_study_admin/{sub_study_id}")
async def deleteSubStudyAdmin(sub_study_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_sub_study_admin(sub_study_id=sub_study_id, password=body.password)
    except HTTPException:
        raise


@app.patch("/toggle_sub_study_admin/{sub_study_id}")
async def toggleSubStudyAdmin(sub_study_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_sub_study_admin(sub_study_id)
    except HTTPException:
        raise


#####################################################################################################
###########################################-Job-ops-#################################################
#####################################################################################################


@app.get("/get_job_status_admin")
async def getJobStatusAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_job_status_admin()
    except HTTPException:
        raise


class AddJobStatusRequest(BaseModel):
    name: str


@app.post("/add_job_status_admin")
async def addJobStatusAdmin(request: Request, body: AddJobStatusRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_job_status_admin(name=body.name)
    except HTTPException:
        raise


@app.delete("/delete_job_status_admin/{job_status_id}")
async def deleteJobStatusAdmin(job_status_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_job_status_admin(
            job_status_id=job_status_id, password=body.password
        )
    except HTTPException:
        raise


@app.patch("/toggle_job_status_admin/{job_status_id}")
async def toggleJobStatusAdmin(job_status_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_job_status_admin(job_status_id)
    except HTTPException:
        raise


#####################################################################################################
########################################-Sub-Job-ops-################################################
#####################################################################################################


@app.get("/get_sub_job_status_admin")
async def getSubJobStatusAdmin(request: Request, job_status_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_sub_job_status_admin(job_status_id=job_status_id)
    except HTTPException:
        raise


class AddSubJobStatusRequest(BaseModel):
    name: str
    job_status : int


@app.post("/add_sub_job_status_admin")
async def addSubJobStatusAdmin(request: Request, body: AddSubJobStatusRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_sub_job_status_admin(name=body.name, job_status_id=body.job_status)
    except HTTPException:
        raise


@app.delete("/delete_sub_job_status_admin/{sub_job_status_id}")
async def deleteSubJobSatatusAdmin(
    sub_job_status_id: int, request: Request, body: Password
):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_sub_job_status_admin(
            sub_job_status_id=sub_job_status_id, password=body.password
        )
    except HTTPException:
        raise


@app.patch("/toggle_sub_job_status_admin/{sub_job_status_id}")
async def toggleSubJobStatusAdmin(sub_job_status_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)
    except HTTPException:
        raise

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_sub_job_status_admin(sub_job_status_id)
    except HTTPException:
        raise


#####################################################################################################
############################################-Misc-###################################################
#####################################################################################################


@app.get("/download_excel")
async def downloadExcel(
    request: Request,
    year: Optional[int] = None,
    college: Optional[int] = None,
    status: Optional[str] = None,
):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise

    if payload.get("college_id") < 2:
        records = await get_data_for_excel(year=year, college_id=college, status=status)
    else:
        records = await get_data_for_excel(college_id=payload.get("id"), status=status)

    if not records or len(records) == 0:
        raise HTTPException(status_code=404, detail="No records found")

    df = pd.DataFrame(records)
    if "id" in df.columns:
        df = df.drop(columns=["id"])
    if "college_id" in df.columns:
        df = df.drop(columns=["college_id"])

    if "acception_year" in df.columns:
        df["acception_year"] = df["acception_year"].apply(lambda y: f"{y}-{y+1}")
    if "suspension_year" in df.columns:
        df["suspension_year"] = df["suspension_year"].apply(lambda y: f"{y}-{y+1}")

    if "request_year" in df.columns:
        df["request_year"] = df["request_year"].apply(lambda y: f"{y}-{y+1}")

    benefactor_map = {Flag.Yes: "نعم", Flag.No: "لا"}

    if "benefactor" in df.columns:
        df["benefactor"] = df["benefactor"].apply(lambda x: benefactor_map.get(x, x))

    RequestStatus_map = {
        RequestStatus.PENDING: "قيد الانتظار",
        RequestStatus.ACCEPTED: "مقبول",
        RequestStatus.DENIED: "مرفوض",
    }

    if "request_status" in df.columns:
        df["request_status"] = df["request_status"].apply(
            lambda x: RequestStatus_map.get(x, x)
        )

    header_map = {
        "student_name": "اسم الطالب",
        "birth_date": "التولد",
        "college": "الكلية",
        "department": "القسم",
        "speciality": "التخصص",
        "study": "المرحلة الدراسية",
        "acception_year": "سنة القبول",
        "suspension_year": "سنة الترقين",
        "suspension_reason": "سبب لبترقين",
        "job_status": "الموقف الوظيفي",
        "request_status": "حالة الطلب",
        "status": "موقف الطلب",
        "benefactor": "مستفيد سابقا",
        "request_year": "العام الدراسي الحالي",
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


@app.get("/stats")
async def getStats(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = tokenCheck(token)

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("college_id") < 2:
        return await get_stats()
    return {"message": "tbd"}


if __name__ == "__main__":
    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)
