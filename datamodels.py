from enum import Enum
from tortoise import fields, Model, fields

class Flag(Enum):
    Yes = "yes"
    No = "no"

class RequestStatus(Enum):
    ACCEPTED = "Accepted"
    DENIED = "Denied"
    PENDING = "Pending"

class EducationalYear(Model):
    id = fields.IntField(pk=True)
    start_year = fields.CharField(max_length=50)
    enabled = fields.CharEnumField(Flag, default=Flag.No)

    class Meta:
        table = "educational_year"

class RequestYear(Model):
    id = fields.IntField(pk=True)
    start_year = fields.CharField(max_length=50)
    current = fields.CharEnumField(Flag, default=Flag.No)

    class Meta:
        table = "request_year"

class JobStatus(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=50)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "job_status"

class JobStatusSub(Model):
    id = fields.IntField(pk=True)
    status = fields.IntField()
    sub = fields.CharField(max_length=50)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "job_status_sub"

class Users(Model):
    id = fields.IntField(pk=True)
    cred = fields.CharField(max_length=50)
    password = fields.CharField(max_length=128)
    college = fields.CharField(max_length=100)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "users"

class Colleges(Model):
    id = fields.IntField(pk=True)
    college = fields.CharField(max_length=100)

    class Meta:
        table = "colleges"

class Departments(Model):
    id = fields.IntField(pk=True)
    college = fields.IntField()
    department = fields.CharField(max_length=100)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "departments"

class Status(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=100)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "status"

class Study(Model):
    id = fields.IntField(pk=True)
    study = fields.CharField(max_length=50)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "study"

class StudySub(Model):
    id = fields.IntField(pk=True)
    study = fields.IntField()
    Sub = fields.CharField(max_length=50)
    enabled = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "study_sub"

class Requests(Model):
    id = fields.IntField(pk=True)
    student_name = fields.CharField(max_length=100)
    college = fields.IntField()
    speciality = fields.CharField(max_length=100)
    birth_date = fields.DateField()
    
    acception_year =  fields.CharField(max_length=50)
    suspension_year =  fields.CharField(max_length=50)
    suspension_reason =  fields.CharField(max_length=512)
    request_year =  fields.CharField(max_length=50)
    
    job_status =  fields.CharField(max_length=100)
    request_status = fields.CharEnumField(RequestStatus, default=RequestStatus.PENDING)
    status = fields.CharField(max_length=100,default="~")
    benefactor = fields.CharEnumField(Flag)
    study = fields.CharField(max_length=100)
   

    class Meta:
        table = "requests"

#######################################Views##################################

class Excel(Model):
    id = fields.IntField(pk=True)
    college_id = fields.IntField()
    student_name = fields.CharField(max_length=100)
    birth_date = fields.DateField()

    college = fields.CharField(max_length=100)
    department = fields.CharField(max_length=100)
    speciality = fields.CharField(max_length=100)
    study = fields.CharField(max_length=100)
    
    acception_year =  fields.CharField(max_length=50)
    suspension_year =  fields.CharField(max_length=50)
    suspension_reason =  fields.CharField(max_length=512)
    
    job_status =  fields.CharField(max_length=100)
    request_status = fields.CharEnumField(RequestStatus, default=RequestStatus.PENDING)
    status = fields.CharField(max_length=100,default="~")

    benefactor = fields.CharEnumField(Flag)
    request_year =  fields.CharField(max_length=50)
    
    class Meta:
        table = "excel"
        managed= False

class RequestsCount(Model):
    id = fields.IntField(pk=True)

    ACcount = fields.IntField()
    DNcount = fields.IntField()
    PNcount = fields.IntField()

    class Meta:
        table = "requests_count"
        managed = False




class RequestsShort(Model):
    
    id = fields.IntField(pk=True)
    college_id = fields.IntField()
    student_name = fields.CharField(max_length=100)
    speciality = fields.CharField(max_length=100)
    college = fields.CharField(max_length=100)
    request_status = fields.CharEnumField(RequestStatus)
    study = fields.CharField(max_length=100)
    status= fields.CharField(max_length=100)
    request_year = fields.CharField(max_length=50 )

    class Meta:
        table = "requests_short"
        managed = False

class UsersList(Model):
    
    id = fields.IntField(pk=True)
    cred = fields.CharField(max_length=50)
    college = fields.CharField(max_length=100)
    enabled = fields.CharEnumField(Flag)

    class Meta:
        table = "users_list"
        managed = False

