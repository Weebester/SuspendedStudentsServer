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

            return {"Token": token, "success": True, "college": user.college}
        else:
            return {"success": False, "message": "Invalid password", "status_code": 401}

    else:
        return {"success": False, "message": "User not found", "status_code": 456}



async def get_users_admin():
    return await UsersList.all().values()


async def delete_user(user_id: int):
    user = await users.get(id=user_id)
    if user:
        await user.delete()
        return {"success": True,"status_code": 200, "message": "User deleted successfully"}
    else:
        return {"success": False, "status_code": 404, "message": "User not found"}


async def add_user(cred: str, password: str, college: str):
    existing_user = await users.get_or_none(cred=cred)
    if existing_user:
        return {"success": False, "status_code": 400, "message": "User already exists"}
    cid = await Colleges.get(college=college)
    print(cid)
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = await users.create(cred=cred, password=hashed_password, college=cid.id)
    return {"success": True, "status_code": 200, "message": "User added successfully"}

async def toggle_user(user_id: int, enable: bool):
    user = await users.get(id=user_id)
    if user:
        await user.update(enabled=Flag.Yes if enable else Flag.No)
        return {"success": True, "status_code": 200, "message": "User status updated successfully"}
    else:
        return {"success": False, "status_code": 404, "message": "User not found"}

async def toggle_all_users(enable: bool):
    new_status = Flag.Yes if enable else Flag.No
    await users.filter(id__not=1).update(enabled=new_status)
    return {"success": True, "status_code": 200, "message": "All user statuses updated successfully"}


    
async def get_users_admin():
    return await UsersList.all().values()


async def delete_user(user_id: int):
    user = await users.get(id=user_id)
    if user:
        await user.delete()
        return {"success": True,"status_code": 200, "message": "User deleted successfully"}
    else:
        return {"success": False, "status_code": 404, "message": "User not found"}


async def add_user(cred: str, password: str, college: str):
    existing_user = await users.get_or_none(cred=cred)
    if existing_user:
        return {"success": False, "status_code": 400, "message": "User already exists"}
    cid = await Colleges.get(college=college)
    print(cid)
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    new_user = await users.create(cred=cred, password=hashed_password, college=cid.id)
    return {"success": True, "status_code": 200, "message": "User added successfully"}



#####################################################################################################################

async def get_data_for_excel(year: int=None):
    if not year:
        current_year = await RequestYear.get(current=Flag.Yes)
        year = current_year.Startyear
    data = await excel.filter(RequestYear=year).values()
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
    page: int = None, status: str = None, year: int = None, college: str = None
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

    if page is not None:
        page_size = 4
        offset = page * page_size
        result = result.offset(offset).limit(page_size)

    return await result.values()


async def get_colleges_admin():
    CollegesList = await Colleges.filter(id__not=1).values("id","college")
    if not CollegesList:
        raise HTTPException(status_code=404, detail="No colleges found")
    return CollegesList