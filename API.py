import os
import shutil
from typing import Optional
from fastapi import Depends, FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
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
from fastapi import Request, UploadFile, File, Form
from typing import Optional

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


@app.get("/User/reivew_request/{request_id}", response_class=HTMLResponse)
async def ReivewRequestU(request: Request, request_id: int):
    token = request.cookies.get("Token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    try:
        payload = tokenCheck(token)
        req_data = await review_request(request_id)

        study_parts = req_data.get("study", "").split("-")
        study_main = study_parts[0] if len(study_parts) > 0 else None
        study_sub = study_parts[1] if len(study_parts) > 1 else None

        job_parts = req_data.get("job_status", "").split("-")
        job_main = job_parts[0] if len(job_parts) > 0 else None
        job_sub = job_parts[1] if len(job_parts) > 1 else None

        return templates.TemplateResponse(
            request=request,
            name="User/RequestReview.html",
            context={
                "role": payload.get("college"),
                "request_id": request_id,
                "request_status": req_data.get("request_status").value,
                "student_name": req_data.get("student_name"),
                "status": req_data.get("status"),
                "birth_date": req_data.get("birth_date"),
                "department": req_data.get("department"),
                "speciality": req_data.get("speciality"),
                "study": study_main,
                "study_sub": study_sub,
                "job_status": job_main,
                "job_status_sub": job_sub,
                "acception_year": f"{req_data.get("acception_year")}-{req_data.get("acception_year")+1}",
                "suspension_year": f"{req_data.get("suspension_year")}-{req_data.get("suspension_year")}",
                "suspension_reason": req_data.get("suspension_reason"),
                "benefactor": "كلا" if req_data.get("benefactor") == Flag.No else "نعم",
                "has_non_objection_file": req_data.get("non_objection").value,
            },
        )

    except HTTPException:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="Token", path="/")
        return response


@app.get("/Admin/reivew_request/{request_id}", response_class=HTMLResponse)
async def ReviewRequestA(request: Request, request_id: int):
    token = request.cookies.get("Token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    try:
        payload = tokenCheck(token)
        if payload.get("college_id") > 1:
            raise HTTPException(status_code=403, detail="not allowed")

        req_data = await review_request(request_id)
        College = await get_college_name(req_data.get("college"))
        print(College.get("college"))

        study_parts = req_data.get("study", "").split("-")
        study_main = study_parts[0] if len(study_parts) > 0 else None
        study_sub = study_parts[1] if len(study_parts) > 1 else None

        job_parts = req_data.get("job_status", "").split("-")
        job_main = job_parts[0] if len(job_parts) > 0 else None
        job_sub = job_parts[1] if len(job_parts) > 1 else None

        return templates.TemplateResponse(
            request=request,
            name="Admin/RequestReview.html",
            context={
                "role": payload.get("college"),
                "college": College.get("college"),
                "college_id": req_data.get("college"),
                "admin": True if payload.get("college_id") == 0 else False,
                "request_id": request_id,
                "request_status": req_data.get("request_status").value,
                "student_name": req_data.get("student_name"),
                "status": req_data.get("status"),
                "birth_date": req_data.get("birth_date"),
                "department": req_data.get("department"),
                "speciality": req_data.get("speciality"),
                "study": study_main,
                "study_sub": study_sub,
                "job_status": job_main,
                "job_status_sub": job_sub,
                "acception_year": f"{req_data.get("acception_year")}-{req_data.get("acception_year")+1}",
                "suspension_year": f"{req_data.get("suspension_year")}-{req_data.get("suspension_year")}",
                "suspension_reason": req_data.get("suspension_reason"),
                "benefactor": "كلا" if req_data.get("benefactor") == Flag.No else "نعم",
                "has_non_objection_file": req_data.get("non_objection").value,
            },
        )

    except HTTPException:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="Token", path="/")
        return response


class AdminPages(str, Enum):
    Main = "Main"
    Requests = "Requests"
    Accounts = "Accounts"
    CollegesOptions = "CollegesOptions"
    StudyOptions = "StudyOptions"
    JobOptions = "JobOptions"
    StatusOptions = "StatusOptions"
    EduYearOptions = "EduYearOptions"
    ReqYearOptions = "ReqYearOptions"
    GuideLinesOptions="GuideLinesOptions"


class UserPages(str, Enum):
    Main = "Main"
    Requests = "Requests"
    NewRequest = "NewRequest"


@app.get("/Admin/{page}", response_class=HTMLResponse)
async def MainA(
    page: AdminPages, request: Request
):  # Changed page: str to page: AdminPages
    token = request.cookies.get("Token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    try:
        payload = tokenCheck(token)
    except HTTPException:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="Token", path="/")
        return response

    if payload.get("college_id") > 1:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="Token", path="/")
        return response

    if payload.get("college_id") !=0 and page in [
        AdminPages.Accounts,
        AdminPages.CollegesOptions,
        AdminPages.StudyOptions,
        AdminPages.JobOptions,
        AdminPages.StatusOptions,
        AdminPages.EduYearOptions,
        AdminPages.ReqYearOptions,
    ]:
        response = RedirectResponse(url="/", status_code=302)
        response.delete_cookie(key="Token", path="/")
        return response

    return templates.TemplateResponse(
        request=request,
        name=f"Admin/{page.value}.html",
        context={
            "role": payload.get("college"),
            "admin": True if payload.get("college_id") == 0 else False,
        },
    )


@app.get("/User/{page}", response_class=HTMLResponse)
async def MainU(request: Request, page: UserPages):
    token = request.cookies.get("Token")
    if not token:
        return RedirectResponse(url="/", status_code=302)

    try:
        payload = tokenCheck(token)
        return templates.TemplateResponse(
            request=request,
            name=f"User/{page.value}.html",
            context={
                "role": payload.get("college"),
                "enabled": True if payload.get("enabled") == "yes" else False,
            },
        )

    except HTTPException:
        return RedirectResponse(url="/", status_code=302)


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


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="Token", path="/")
    return response


@app.get("/get_users")
async def getUsersList(request: Request, college_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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

    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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

    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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

    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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

    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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

    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_all_users(enable)
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

    payload = tokenCheck(token)

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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_sub_job_status_admin(job_status_id=job_status_id)
    except HTTPException:
        raise


class AddSubJobStatusRequest(BaseModel):
    name: str
    job_status: int


@app.post("/add_sub_job_status_admin")
async def addSubJobStatusAdmin(request: Request, body: AddSubJobStatusRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
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
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_sub_job_status_admin(sub_job_status_id)
    except HTTPException:
        raise


#####################################################################################################
###########################################-Status-ops-#################################################
#####################################################################################################


@app.get("/get_status_admin")
async def getStatusAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_status_admin()
    except HTTPException:
        raise


class AddStatusRequest(BaseModel):
    name: str


@app.post("/add_status_admin")
async def addJobStatusAdmin(request: Request, body: AddStatusRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_status_admin(name=body.name)
    except HTTPException:
        raise


@app.delete("/delete_status_admin/{status_id}")
async def deleteJobStatusAdmin(status_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_status_admin(status_id=status_id, password=body.password)
    except HTTPException:
        raise


@app.patch("/toggle_status_admin/{status_id}")
async def toggleStatusAdmin(status_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_status_admin(status_id)
    except HTTPException:
        raise


#####################################################################################################
###########################################-Edu-Years-ops-#################################################
#####################################################################################################


@app.get("/get_edu_years_admin")
async def getEduYearsAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_edu_years_admin()
    except HTTPException:
        raise


class AddYearRequest(BaseModel):
    year: int


@app.post("/add_edu_year_admin")
async def addEduYearAdmin(request: Request, body: AddYearRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_edu_year_admin(year=body.year)
    except HTTPException:
        raise


@app.delete("/delete_edu_year_admin/{year_id}")
async def deleteEduYearsAdmin(year_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_edu_year_admin(year_id=year_id, password=body.password)
    except HTTPException:
        raise


@app.patch("/toggle_edu_year_admin/{year_id}")
async def toggleEduYearsAdmin(year_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_edu_year_admin(year_id)
    except HTTPException:
        raise


#####################################################################################################
###########################################-Rew-Years-ops-#################################################
#####################################################################################################


@app.get("/get_req_years_admin")
async def getReqYearsAdmin(request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        return await get_req_years_admin()
    except HTTPException:
        raise


class AddYearRequest(BaseModel):
    year: int


@app.post("/add_req_year_admin")
async def addReqYearAdmin(request: Request, body: AddYearRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await add_req_year_admin(year=body.year)
    except HTTPException:
        raise


@app.delete("/delete_req_year_admin/{year_id}")
async def deleteReqYearsAdmin(year_id: int, request: Request, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_req_year_admin(year_id=year_id, password=body.password)
    except HTTPException:
        raise


@app.patch("/toggle_req_year_admin/{year_id}")
async def toggleReqYearsAdmin(year_id: int, request: Request):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await toggle_req_year_admin(year_id)
    except HTTPException:
        raise


#####################################################################################################
#########################################-Requests-##################################################
#####################################################################################################


@app.get("/get_notes/{request_id}")
async def getNotes(request: Request, request_id: int):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)
    try:
        return await get_messages(request_id=request_id)
    except HTTPException:
        raise


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
    payload = tokenCheck(token)

    try:
        if payload.get("college_id") < 2:
            return await get_requests(status=status, year=year, college_id=college)
        else:
            return await get_requests(
                status=status, college_id=payload.get("college_id")
            )
    except HTTPException:
        raise


@app.get("/feed_form")
async def FeedForm(request: Request, college_id: Optional[int] = None):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)
    try:
        if payload.get("college_id") < 2:
            return await feed_form(college_id)
        else:
            return await feed_form(payload.get("college_id"))
    except HTTPException:
        raise


class RequestForm:
    def __init__(
        self,
        student_name: str = Form(...),
        birth_date: str = Form(...),
        department: str = Form(...),
        speciality: str = Form(...),
        study: str = Form(...),
        job_status: str = Form(...),
        acception_year: int = Form(...),
        suspension_year: int = Form(...),
        suspension_reason: str = Form(...),
        benefactor: str = Form(...),
        notes: str = Form(...),
    ):
        self.data = {
            "student_name": student_name,
            "department": department,
            "speciality": speciality,
            "birth_date": birth_date,
            "acception_year": acception_year,
            "suspension_year": suspension_year,
            "suspension_reason": suspension_reason,
            "job_status": job_status,
            "benefactor": benefactor,
            "study": study,
        }
        self.notes = notes


@app.post("/submit_request")
async def SubmitRequest(
    request: Request,
    form: RequestForm = Depends(),
    file_academic: UploadFile = File(...),
    file_pledge: UploadFile = File(...),
    file_non_objection: UploadFile = File(None),
):

    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = tokenCheck(token)
    if payload.get("enabled") == "no":
        raise HTTPException(status_code=403, detail="Forbbiden")

    form.data["college"] = payload.get("college_id")
    if file_non_objection is not None:
        form.data["non_objection"] = Flag.Yes
    new_record = await create_request(form.data)

    for f in [file_academic, file_pledge]:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        for file_obj, folder in [
            (file_academic, "academic"),
            (file_pledge, "pledge"),
            (file_non_objection, "non_objection"),
        ]:
            filename = f"{new_record.id}.pdf"
            full_path = os.path.join("statics", folder, filename)

            with open(full_path, "wb") as buffer:
                shutil.copyfileobj(file_obj.file, buffer)

    except:
        raise

    await create_attached_message(notes=form.notes, request_id=new_record.id)


class UpdateRequestForm:
    def __init__(
        self,
        student_name: Optional[str] = Form(None),
        birth_date: Optional[str] = Form(None),
        department: Optional[str] = Form(None),
        speciality: Optional[str] = Form(None),
        study: Optional[str] = Form(None),
        job_status: Optional[str] = Form(None),
        acception_year: Optional[int] = Form(None),
        suspension_year: Optional[int] = Form(None),
        suspension_reason: Optional[str] = Form(None),
        benefactor: Optional[str] = Form(None),
        notes: Optional[str] = Form(None),
    ):
        self.raw_data = {
            "student_name": student_name,
            "department": department,
            "speciality": speciality,
            "birth_date": birth_date,
            "acception_year": acception_year,
            "suspension_year": suspension_year,
            "suspension_reason": suspension_reason,
            "job_status": job_status,
            "benefactor": benefactor,
            "study": study,
        }
        self.data = {k: v for k, v in self.raw_data.items() if v is not None}
        self.notes = notes


@app.post("/update_request/{request_id}")
async def UpdateRequest(
    request_id: int,
    request: Request,
    form: UpdateRequestForm = Depends(),
    file_academic: Optional[UploadFile] = File(None),
    file_pledge: Optional[UploadFile] = File(None),
    file_non_objection: UploadFile = File(None),
):

    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = tokenCheck(token)

    if file_non_objection is not None:
        form.data["non_objection"] = Flag.Yes

    await update_request_logic(request_id, form.data, payload.get("college_id"))

    files_to_process = [
        (file_academic, "academic"),
        (file_pledge, "pledge"),
        (file_non_objection, "non_objection"),
    ]

    for file_obj, folder in files_to_process:
        if file_obj and file_obj.filename:

            if not file_obj.filename.lower().endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files allowed")
            try:
                full_path = os.path.join("statics", folder, f"{request_id}.pdf")

                with open(full_path, "wb") as buffer:
                    shutil.copyfileobj(file_obj.file, buffer)
            except:
                raise

    if form.notes is not None:
        await create_attached_message(notes=form.notes, request_id=request_id)


@app.post("/upload_non_objection/{request_id}")
async def UploadNonObjection(
    request: Request, request_id: int, file_non_objection: UploadFile = File(...)
):

    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = tokenCheck(token)

    try:

        filename = f"{request_id}.pdf"
        full_path = os.path.join("statics", "non_objection", filename)

        with open(full_path, "wb") as buffer:
            shutil.copyfileobj(file_non_objection.file, buffer)

        await non_objection_add(
            request_id=request_id, college_id=payload.get("college_id")
        )
    except:
        raise

    await create_attached_message(
        notes="تم اضافة/تحديث ملف عدم الممانعة", request_id=request_id
    )


class acceptDenyRequest(BaseModel):
    new_status: str
    note: str


@app.patch("/change_status/{request_id}")
async def ChangeStatus(request: Request, request_id: int, body: acceptDenyRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await change_request_status(request_id=request_id, status=body.new_status)
        await create_attached_message(notes=body.note, request_id=request_id)
    except HTTPException:
        raise


class acceptDenyRequest(BaseModel):
    state: str
    note: str


@app.patch("/accept_deny/{request_id}")
async def acceptDeny(request: Request, request_id: int, body: acceptDenyRequest):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") > 1:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await accept_deny_request(request_id=request_id, state=body.state)
        await create_attached_message(
            notes=body.note, request_id=request_id, state=body.state
        )
    except HTTPException:
        raise


@app.delete("/delete_request/{request_id}")
async def deleteRequest(request: Request, request_id: int, body: Password):
    token = request.cookies.get("Token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = tokenCheck(token)

    if payload.get("college_id") !=0:
        raise HTTPException(status_code=403, detail="Forbidden: Admins only")

    try:
        await delete_request(request_id=request_id, password=body.password)

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
    payload = tokenCheck(token)

    if payload.get("college_id") < 2:
        records = await get_data_for_excel(year=year, college_id=college, status=status)
    else:
        records = await get_data_for_excel(
            college_id=payload.get("college_id"), status=status
        )

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

    flag_map = {Flag.Yes: "نعم", Flag.No: "لا"}

    if "benefactor" in df.columns:
        df["benefactor"] = df["benefactor"].apply(lambda x: flag_map.get(x, x))

    if "non_objection" in df.columns:
        df["non_objection"] = df["non_objection"].apply(lambda x: flag_map.get(x, x))

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
        "non_objection": "عدم ممانعة",
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

    payload = tokenCheck(token)

    if payload.get("college_id") < 2:
        return await get_stats()
    return await get_stats(payload.get("college_id"))


if __name__ == "__main__":
    for folder in ["academic", "pledge", "non_objection", "rules"]:
        os.makedirs(os.path.join("statics", folder), exist_ok=True)
    uvicorn.run("API:app", host="0.0.0.0", port=8000, reload=True)
