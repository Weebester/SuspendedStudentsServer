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
    Startyear = fields.CharField(max_length=50)

    class Meta:
        table = "educationalyear"

class RequestYear(Model):
    id = fields.IntField(pk=True)
    Startyear = fields.CharField(max_length=50)
    current = fields.CharEnumField(Flag, default=Flag.No)

    class Meta:
        table = "requestyear"

class JobStatus(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=50)

    class Meta:
        table = "jobstatus"

class users(Model):
    id = fields.IntField(pk=True)
    cred = fields.CharField(max_length=50)
    password = fields.CharField(max_length=128)
    college = fields.CharField(max_length=100)

    class Meta:
        table = "users"

class Colleges(Model):
    id = fields.IntField(pk=True)
    college = fields.CharField(max_length=100)
    Active = fields.CharEnumField(Flag, default=Flag.Yes)

    class Meta:
        table = "colleges"

class Departments(Model):
    id = fields.IntField(pk=True)
    college = fields.IntField()
    department = fields.CharField(max_length=100)

    class Meta:
        table = "departments"

class Status(Model):
    id = fields.IntField(pk=True)
    status = fields.CharField(max_length=100)

    class Meta:
        table = "status"

class Study(Model):
    id = fields.IntField(pk=True)
    study = fields.CharField(max_length=50)
    Sub = fields.CharField(max_length=50)

    class Meta:
        table = "study"

class requests(Model):
    id = fields.IntField(pk=True)
    StudentName = fields.CharField(max_length=100)
    college = fields.IntField()
    speciality = fields.CharField(max_length=100)
    BirthDate = fields.DateField()
    
    AcceptionYear =  fields.CharField(max_length=50)
    SuspensionYear =  fields.CharField(max_length=50)
    SuspensionReason =  fields.CharField(max_length=512)
    RequestYear =  fields.CharField(max_length=50)
    
    jobstatus =  fields.CharField(max_length=100)
    RequestStatus = fields.CharEnumField(RequestStatus, default=RequestStatus.PENDING)
    status = fields.CharField(max_length=100,default="~")
    benefactor = fields.CharEnumField(Flag)
    study = fields.CharField(max_length=100)
   

    class Meta:
        table = "requests"

#######################################Views##################################

class excel(Model):
    id = fields.IntField(pk=True)
    StudentName = fields.CharField(max_length=100)
    BirthDate = fields.DateField()

    college = fields.CharField(max_length=100)
    department = fields.CharField(max_length=100)
    speciality = fields.CharField(max_length=100)
    study = fields.CharField(max_length=100)
    
    AcceptionYear =  fields.CharField(max_length=50)
    SuspensionYear =  fields.CharField(max_length=50)
    
    jobstatus =  fields.CharField(max_length=100)
    RequestStatus = fields.CharEnumField(RequestStatus, default=RequestStatus.PENDING)
    status = fields.CharField(max_length=100,default="~")

    SuspensionReason =  fields.CharField(max_length=512)
    benefactor = fields.CharEnumField(Flag)
    RequestYear =  fields.CharField(max_length=50)
    
    
   

    class Meta:
        table = "excel"
        managed= False

class requestscount(Model):
    id = fields.IntField(pk=True)

    ACcount = fields.IntField()
    DNcount = fields.IntField()
    PNcount = fields.IntField()

    class Meta:
        table = "requestscount"
        managed = False


from tortoise import fields, models

class RequestsAdmin(models.Model):
    
    id = fields.IntField(pk=True)
    StudentName = fields.CharField(max_length=100)
    Speciality = fields.CharField(max_length=100)
    college = fields.CharField(max_length=100)
    RequestStatus = fields.CharEnumField(RequestStatus)
    study = fields.CharField(max_length=100)
    RequestYear = fields.CharField(max_length=50 )

    class Meta:
        table = "requests_admin"
        managed = False

class UsersList(models.Model):
    
    id = fields.IntField(pk=True)
    cred = fields.CharField(max_length=50)
    college = fields.CharField(max_length=100)

    class Meta:
        table = "userslist"
        managed = False