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


########################################################AccountsOPs################################################################


async def login_process(cred: str, password: str) -> dict:
    #  print("request received")
    #  print(cred)
    user = await users.get(cred=cred)
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
        await users.get(id=user_id).update(password=hashed_password)
    except:
        raise HTTPException(status_code=404, detail="faild to update password")



async def get_users_admin():
    return await UsersList.all().values()


async def delete_user(user_id: int, password: str):
    user = await users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    user = await users.get(id=user_id)
    if user:
        await user.delete()
    else:
        raise HTTPException(status_code=404, detail="User not found")


async def add_user(cred: str, password: str, college: str):
    existing_user = await users.get_or_none(cred=cred)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    cid = await Colleges.get(college=college)
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    await users.create(cred=cred, password=hashed_password, college=cid.id)
   


async def toggle_user(user_id: int, enable: bool):
    user = await users.get(id=user_id)
    if user:
        await user.update(enabled=Flag.Yes if enable else Flag.No)
        return {
            "success": True,
            "status_code": 200,
            "message": "User status updated successfully",
        }
    else:
        return {"success": False, "status_code": 404, "message": "User not found"}


async def toggle_all_users(enable: bool):
    new_status = Flag.Yes if enable else Flag.No
    await users.filter(id__not=1).update(enabled=new_status)
    return {
        "success": True,
        "status_code": 200,
        "message": "All user statuses updated successfully",
    }


#####################################################################################################################


async def get_data_for_excel(year: int = None):
    if not year:
        current_year = await RequestYear.get(current=Flag.Yes)
        year = current_year.Startyear
    data = await excel.filter(RequestYear=year).values()

    if not data:
        raise HTTPException(status_code=404, detail="No data found for the specified year")
    return data


async def get_stats():
    stats = await requestscount.get(id=1)

    print(stats.ACcount, stats.DNcount, stats.PNcount)
    return {
        "Accepted": stats.ACcount,
        "Denied": stats.DNcount,
        "Pending": stats.PNcount,
    }


async def get_colleges():

    colleges = await Colleges.filter(id__not=1).values_list("college", flat=True)
    print(colleges)
    return colleges


async def get_years():
    years = await RequestYear.all().values_list("Startyear", flat=True)
    return years


async def get_requests_admin(
    status: str = None, year: int = None, college: str = None
):
    result = RequestsAdmin.all()
    if status is not None:
        print(status)
        result = result.filter(RequestStatus=status)

    if college is not None:
        result = result.filter(college=college)

    if not year:
        current_year = await RequestYear.get(current=Flag.Yes)
        year = current_year.Startyear

    result = result.filter(RequestYear=year)

    
    result = await result.values()
    return result

#########################################################-Colleges-OPs-########################################################
async def get_colleges_admin():
    CollegesList = await Colleges.filter(id__not=1).values("id", "college")
    if not CollegesList:
        raise HTTPException(status_code=404, detail="No colleges found")
    return CollegesList

async def add_college_admin(name: str):
    existing_college = await Colleges.get_or_none(college=name)
    if existing_college:
        raise HTTPException(status_code=400, detail="College already exists")
    await Colleges.create(college=name)
    

async def delete_college_admin(college_id: int, password: str):
    user = await users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    college = await Colleges.get(id=college_id)
    if college:
        await college.delete()
    else:
        raise HTTPException(status_code=404, detail="College not found")
    
#############################################################-Departments-OPs-########################################################
async def get_departments_admin():
    DepartmentsList = await Departments.all().values("id", "department", "college")
    if not DepartmentsList:
        raise HTTPException(status_code=404, detail="No departments found")
    return DepartmentsList

async def add_department_admin(name: str, college_id: int):
    existing_department = await Departments.get_or_none(department=name)
    if existing_department:
        raise HTTPException(status_code=400, detail="Department already exists")

    await Departments.create(department=name, college=college_id)
    

async def delete_department_admin(department_id: int, password: str):
    user = await users.get(id=1)
    if not bcrypt.checkpw(password.encode(), user.password.encode()):
        raise HTTPException(status_code=401, detail="Invalid password")
    department = await Departments.get(id=department_id)
    if department:
        await department.delete()
    else:
        raise HTTPException(status_code=404, detail="Department not found")
    
