from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel, Field, validator
from email_validator import EmailNotValidError, validate_email

from datetime import datetime

from models import GenderEnum, StatusEnum


# Admin Users

class UserSignUp(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=3, max_length=50)

    @validator("email")
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )
    

class UserUpdate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)


class UserLoginResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email:str
    token: str

    class Config:
        orm_mode = True


class User(BaseModel):
    id: str
    first_name: str
    last_name: str
    email:str

    class Config:
        orm_mode = True


# Patients

class PatientsAdd(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=50)
    number: str = Field(min_length=10, max_length=10, regex="^[0-9]*$")
    password: str = Field(min_length=3, max_length=50)
    gender: GenderEnum = Field(...)
    height: float
    weight: float

    @validator("email")
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )


class PatientLoginResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    gender: GenderEnum
    height: float
    weight: float
    email: str
    number: str
    token: str

    class Config:
        orm_mode = True


class PatientUpdate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)
    number: str = Field(min_length=10, max_length=10, regex="^[0-9]*$")
    gender: GenderEnum = Field(...)
    height: float
    weight: float


class Patient(BaseModel):
    id: str
    first_name: str
    last_name: str
    gender: GenderEnum
    height: float
    weight: float
    email: str
    number: str

    class Config:
        orm_mode = True


class PatientList(BaseModel):
    count: int
    list: List[Patient] = []

    class Config:
        orm_mode = True


class SignIn(BaseModel):
    email: str = Field(min_length=5, max_length=50)
    password: str = Field(min_length=3, max_length=50)

    @validator("email")
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )


class ChangePassword(BaseModel):
    old_password: str = Field(min_length=3, max_length=50)
    new_password: str = Field(min_length=3, max_length=50)


# End Patients

# Specialization

class SpecializationAdd(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    description: str = Field(None)


class Specialization(BaseModel):
    id: str
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class SpecializationList(BaseModel):
    count: int
    list: List[Specialization] = []

    class Config:
        orm_mode = True


# End Specialzation


# Doctors

class DoctorAdd(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)
    email: str = Field(min_length=5, max_length=50)
    number: str = Field(min_length=10, max_length=10, regex="^[0-9]*$")
    password: str = Field(min_length=3, max_length=50)
    specialization_id: str = Field(..., min_length=36, max_length=36)

    @validator("email")
    def valid_email(cls, email):
        try:
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)
            )


class DoctorLoginResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    number: str
    token: str

    class Config:
        orm_mode = True


class DoctorUpdate(BaseModel):
    first_name: str = Field(..., min_length=2, max_length=60)
    last_name : str = Field(..., min_length=2, max_length=60)
    number: str = Field(min_length=10, max_length=10, regex="^[0-9]*$")


class DoctorResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    number: str

    class Config:
        orm_mode = True


class DoctorSpecialization(BaseModel):
    id: str
    doctor: DoctorResponse
    specialization: Specialization

    class Config:
        orm_mode = True

class Doctor(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    number: str
    doctor_specializations: List[DoctorSpecialization] = []

    class Config:
        orm_mode = True


class DoctorList(BaseModel):
    count: int
    list: List[Doctor] = []

    class Config:
        orm_mode = True


# End Doctors


# Appointments


class AppointmentAdd(BaseModel):
    patient_id: str = Field(..., min_length=36, max_length=36)
    doctor_id: str = Field(..., min_length=36, max_length=36)
    from_time: datetime
    to_time: datetime
    description: str = Field(None)


class Appointment(BaseModel):
    id: str
    patient: Patient
    doctor: DoctorResponse
    from_time: datetime
    to_time: datetime
    status: StatusEnum
    canceller: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class AppointmentList(BaseModel):
    count: int
    list: List[Appointment] = []

    class Config:
        orm_mode = True


class AppointmentUpdate(BaseModel):
    doctor_id: str = Field(..., min_length=36, max_length=36)
    from_time: datetime
    to_time: datetime
    description: str = Field(None)
