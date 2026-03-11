from turtle import pd

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
import datetime
import secrets
from datamodels import *

secret_key = secrets.token_hex(32)


# token check
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def tokenCheck(token: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


#####################################################################################################
#####################################S####-Accounts-OPs-##############################################
#####################################################################################################


async def login_process(cred: str, password: str) -> dict:
    #  print("request received")
    #  print(cred)
    user = await Users.get(cred=cred)
    if user:
        if bcrypt.checkpw(password.encode(), user.password.encode()):
            payload = {"id": user.id}
            try:
                token = jwt.encode(payload, secret_key, algorithm="HS256")
            except jwt.PyJWTError as e:
                raise RuntimeError(f"Token generation failed: {e}")

            return {"Token": token, "college": user.college}
        else:
            raise HTTPException(status_code=401, detail="Invalid password")
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def change_user_password(user_id: int, new_password: str):
    try:
        hashed_password = bcrypt.hashpw(
            new_password.encode(), bcrypt.gensalt()
        ).decode()
        await Users.get(id=user_id).update(password=hashed_password)
    except:
        raise HTTPException(status_code=404, detail="faild to update password")


async def get_users(college_id: int = None):
    if college_id is not None:
        return await UsersList.filter(college_id=college_id).values()
    return await UsersList.all().values()


async def delete_user(user_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    user = await Users.get(id=user_id)
    if user:
        await user.delete()
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def add_user(cred: str, password: str, college_id: int):
    existing_user = await Users.get_or_none(cred=cred)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    await Users.create(cred=cred, password=hashed_password, college=college_id)


async def toggle_user(user_id: int):
    user = await Users.get(id=user_id)
    if user:
        user.enabled = Flag.No if user.enabled == Flag.Yes else Flag.Yes
        await user.save()
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def toggle_all_users(enable: bool):
    new_status = Flag.Yes if enable else Flag.No
    await Users.filter(id__not=1).update(enabled=new_status)


#####################################################################################################
############################################Misc#####################################################
#####################################################################################################


async def get_data_for_excel(
    year: int = None, college_id: str = None, status: str = None
):
    if year is None:
        current_year = await RequestYear.get(current=Flag.Yes)
        year = current_year.start_year
    data = Excel.filter(request_year=year)

    if college_id is not None:
        data = data.filter(college_id=college_id)

    if status is not None:
        data = data.filter(request_status=status)

    print(year, status, college_id)

    data = await data.values()

    if not data:
        raise HTTPException(status_code=404, detail="No data found")
    return data


async def get_stats():
    stats = await RequestsCount.get(id=1)

    print(stats.ACcount, stats.DNcount, stats.PNcount)
    return {
        "Accepted": stats.ACcount,
        "Denied": stats.DNcount,
        "Pending": stats.PNcount,
    }


async def get_years():
    years = await RequestYear.all().values()
    return years


async def get_requests(status: str = None, year: int = None, college_id: int = None):
    result = RequestsShort.all()
    if status is not None:
        print(status)
        result = result.filter(request_status=status)

    if college_id is not None:
        result = result.filter(college_id=college_id)

    if not year:
        current_year = await RequestYear.get(current=Flag.Yes)
        year = current_year.start_year

    print(year, status, college_id)

    result = result.filter(request_year=year)

    result = await result.values()
    return result


#####################################################################################################
############################################-Colleges-OPs-###########################################
#####################################################################################################


async def get_colleges_admin():
    List = await Colleges.filter(id__not=1).values("id", "college")
    return List


async def add_college_admin(name: str):
    existing_college = await Colleges.get_or_none(college=name)
    if existing_college:
        raise HTTPException(status_code=400, detail="College already exists")
    await Colleges.create(college=name)


async def rename_college_admin(college_id=int, new_name=str):
    await Colleges.get(id=college_id).update(college=new_name)


async def delete_college_admin(college_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    college = await Colleges.get(id=college_id)
    if college:
        await college.delete()
    else:
        raise HTTPException(status_code=404, detail="College not found")


#####################################################################################################
######################################-Departments-OPs-##############################################
#####################################################################################################


async def get_departments_admin(college_id: int = None):
    if college_id is not None:
        List = await DepartmentsList.filter(college_id=college_id).values()
    else:
        List = await DepartmentsList.all().values()
    return List


async def add_department_admin(name: str, college_id: int):
    existing_department = await Departments.get_or_none(department=name)
    if existing_department:
        raise HTTPException(status_code=400, detail="Department already exists")

    await Departments.create(department=name, college=college_id)


async def delete_department_admin(department_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    department = await Departments.get(id=department_id)
    if department:
        await department.delete()
    else:
        raise HTTPException(status_code=404, detail="Department not found")


async def toggle_department_admin(department_id: int):
    department = await Departments.get(id=department_id)
    if department:
        department.enabled = Flag.No if department.enabled == Flag.Yes else Flag.Yes
        await department.save()
    else:
        raise HTTPException(status_code=404, detail="Department not found")


#####################################################################################################
############################################-Study-OPs-##############################################
#####################################################################################################


async def get_study_admin():
    List = await Study.all().values()
    return List


async def add_study_admin(name: str):
    existing_study = await Study.get_or_none(study=name)
    if existing_study:
        raise HTTPException(status_code=400, detail="Study already exists")
    await Study.create(study=name)


async def delete_study_admin(study_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    study = await Study.get(id=study_id)
    if study:
        await study.delete()
    else:
        raise HTTPException(status_code=404, detail="study not found")
    

async def toggle_study_admin(study_id: int):
    study = await Study.get(id=study_id)
    if study:
        study.enabled = Flag.No if study.enabled == Flag.Yes else Flag.Yes
        await study.save()
    else:
        raise HTTPException(status_code=404, detail="Study not found")


####################################################################################################################################
#############################################################-Sub-Study-OPs-########################################################
####################################################################################################################################


async def get_sub_study_admin(study_id: int = None):
    if study_id is not None:
        List = await SubStudyList.filter(study_id=study_id).values()
    else:
        List = await SubStudyList.all().values()
    return List


async def add_sub_study_admin(name: str, study_id: int):
    await StudySub.create(sub=name, study=study_id)


async def delete_sub_study_admin(sub_study_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    sub_study = await StudySub.get(id=sub_study_id)
    if sub_study:
        await sub_study.delete()
    else:
        raise HTTPException(status_code=404, detail="SubStudy not found")


async def toggle_sub_study_admin(sub_study_id: int):
    sub_study = await StudySub.get(id=sub_study_id)
    if sub_study:
        sub_study.enabled = Flag.No if sub_study.enabled == Flag.Yes else Flag.Yes
        await sub_study.save()
    else:
        raise HTTPException(status_code=404, detail="SubStudy not found")


#####################################################################################################
############################################-Job-OPs-##############################################
#####################################################################################################


async def get_job_status_admin():
    List = await JobStatus.all().values()
    return List


async def add_job_status_admin(name: str):
    existing_status = await JobStatus.get_or_none(status=name)
    if existing_status:
        raise HTTPException(status_code=400, detail="Job status already exists")
    await JobStatus.create(status=name)


async def delete_job_status_admin(job_status_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    job_status = await JobStatus.get(id=job_status_id)
    if job_status:
        await job_status.delete()
    else:
        raise HTTPException(status_code=404, detail="job status not found")
    

async def toggle_job_status_admin(job_status_id: int):
    job_status = await JobStatus.get(id=job_status_id)
    if job_status:
        job_status.enabled = Flag.No if job_status.enabled == Flag.Yes else Flag.Yes
        await job_status.save()
    else:
        raise HTTPException(status_code=404, detail="Study not found")


####################################################################################################################################
#############################################################-Sub-jobs-OPs-########################################################
####################################################################################################################################


async def get_sub_job_status_admin(job_status_id: int = None):
    if job_status_id is not None:
        List = await SubJobStatusList.filter(status_id=job_status_id).values()
    else:
        List = await SubJobStatusList.all().values()
    return List


async def add_sub_job_status_admin(name: str, job_status_id: int):
    await JobStatusSub.create(sub=name, status=job_status_id)


async def delete_sub_job_status_admin(sub_job_status_id: int, password: str):
    user = await Users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    sub_job_status = await JobStatusSub.get(id=sub_job_status_id)
    if sub_job_status:
        await sub_job_status.delete()
    else:
        raise HTTPException(status_code=404, detail="sub job status not found")


async def toggle_sub_job_status_admin(sub_job_status_id: int):
    sub_job_status = await JobStatusSub.get(id=sub_job_status_id)
    if sub_job_status:
        sub_job_status.enabled = Flag.No if sub_job_status.enabled == Flag.Yes else Flag.Yes
        await sub_job_status.save()
    else:
        raise HTTPException(status_code=404, detail="Sub job status not found")
