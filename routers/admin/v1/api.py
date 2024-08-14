
from datetime import datetime
from fastapi import APIRouter, Header, Response
from fastapi import HTTPException, status, Depends, Path, Query
from sqlalchemy.orm import Session
from typing import List

from libs.utils import object_as_dict
from models import GenderEnum, StatusEnum
from routers.admin.v1 import schemas
from dependencies import get_db
from routers.admin.v1.crud import appointments, doctors, patients, specializations, users

router = APIRouter()


# Users

@router.post(
    "/sign-in",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UserLoginResponse,
    tags=["Admin - Users"],
)
def sign_in(user: schemas.SignIn, db: Session = Depends(get_db)):
    db_user = users.sign_in(db, user)
    return db_user

@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    tags=["Admin - Users"]
)
def add_user(
    user: schemas.UserSignUp,
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token=token)
    user_id = users.add_user(db, user=user)
    return user_id


@router.get(
    "/users/{user_id}",
    response_model=schemas.User,
    tags=["Admin - Users"]
)
def get_my_profile(
    token: str = Header(None),
    user_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token=token)
    db_user = users.get_user_profile(db, user_id=user_id)
    return db_user


@router.put(
    "/users/{user_id}",
    response_model=schemas.User,
    tags=["Admin - Users"]
)
def update_profile(
    user: schemas.UserUpdate,
    token: str = Header(None),
    user_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db),
):
    users.verify_token(db, token=token)
    db_user = users.update_user_profile(db, user=user, user_id=user_id)
    return db_user


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    tags=["Admin - Users"]
)
def delete_user(
    token: str = Header(None),
    user_id: str = Path(..., title="User ID", min_length=36, max_length=36),
    db: Session = Depends(get_db),
):
    users.verify_token(db, token=token)
    users.delete_user(db, user_id=user_id)
    return Response(status_code=status.HTTP_200_OK)

# End Users

# Patients

@router.get(
    "/patients",
    response_model=schemas.PatientList,
    tags=["Patients"]
)
def get_patient_list(
    token: str = Header(None),
    start: int = 0,
    limit: int = 10,
    search: str = Query("all", min_length=1, max_length=50),
    sort_by: str = Query("all", min_length=3, max_length=50),
    order: str = Query("all", min_length=3, max_length=7),
    gender: GenderEnum = Query(None),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = patients.get_patients_list(db, start, limit, search, sort_by, order, gender)
    return data
    

@router.post(
    "/patients/sign-up",
    response_model=schemas.PatientLoginResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Patients"]
)
def add_patient(
    patient: schemas.PatientsAdd,
    db: Session =  Depends(get_db)
):
    data = patients.add_patient(db=db, patient=patient)
    return data


@router.post(
    "/patients/sign-in",
    response_model=schemas.PatientLoginResponse,
    status_code=status.HTTP_200_OK,
    tags=["Patients"]
)
def sign_in(user: schemas.SignIn, db: Session = Depends(get_db)):
    data = patients.sign_in(db, user)
    return data


@router.post(
    "/patients/change-password",
    status_code=status.HTTP_200_OK,
    tags=["Patients"]
)
def change_password(
    user: schemas.ChangePassword,
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    patients.change_password(db, user=user, token=token)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/patients/all",
    response_model=List[schemas.Patient],
    tags=["Patients"]
)
def get_all_patients(
    db: Session = Depends(get_db)
):
    data = patients.get_all_patients(db)
    return data


@router.get(
    "/patients/{patient_id}",
    response_model=schemas.Patient,
    tags=["Patients"]
)
def get_patient_by_id(
    token: str = Header(None),
    patient_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = patients.get_patient(db, patient_id)
    return data


@router.put(
    "/patients/{patient_id}",
    response_model=schemas.Patient,
    tags=["Patients"]
)
def update_patient(
    patient: schemas.PatientUpdate,
    token: str = Header(None),
    patient_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = patients.update_patient(db, patient_id, patient)
    return data


# End Patients

# Specialization


@router.get(
    "/specializations",
    response_model=schemas.SpecializationList,
    tags=["Specializations"]
)
def get_specialization_list(
    token: str = Header(None),
    start: int = 0,
    limit: int = 10,
    search: str = Query("all", min_length=1, max_length=50),
    sort_by: str = Query("all", min_length=3, max_length=50),
    order: str = Query("all", min_length=3, max_length=7),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    data = specializations.get_specialization_list(db, start, limit, search, sort_by, order)
    return data


@router.post(
    "/specializations",
    response_model=schemas.Specialization,
    status_code=status.HTTP_201_CREATED,
    tags=["Specializations"]
)
def add_specialization(
    specialization: schemas.SpecializationAdd,
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    data = specializations.add_specialization(db=db, specialization=specialization)
    return data


@router.get(
    "/specializations/all",
    response_model=List[schemas.Specialization],
    tags=["Specializations"]
)
def get_all_specializations(
    db: Session = Depends(get_db)
):
    data = specializations.get_all_specialization(db=db)
    return data


@router.get(
    "/specializations/{specialization_id}",
    response_model=schemas.Specialization,
    tags=["Specializations"]
)
def get_specialization(
    token: str = Header(None),
    specialization_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    data = specializations.get_specialization(db=db, specialization_id=specialization_id)
    return data


@router.get(
    "/specializations/{specialization_id}/doctors",
    response_model=List[schemas.DoctorSpecialization],
    tags=["Specializations"]
)
def get_specialization_doctors(
    specialization_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    data = specializations.get_specialization_doctors(db=db, specialization_id=specialization_id)
    return data


@router.put(
    "/specializations/{specialization_id}",
    response_model=schemas.Specialization,
    tags=["Specializations"]
)
def update_specialization(
    specialization: schemas.SpecializationAdd,
    specialization_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    data = specializations.update_specialization(db=db, specialization_id=specialization_id, specialization=specialization)
    return data


@router.delete(
    "/specializations/{specialization_id}",
    status_code=status.HTTP_200_OK,
    tags=["Specializations"]
)
def delete_specialization(
    specialization_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    specializations.delete_specialization(db=db, specialization_id=specialization_id)
    return Response(status_code=status.HTTP_200_OK)


# End Specialization 


# Doctor

@router.get(
    "/doctors",
    response_model=schemas.DoctorList,
    tags=["Doctors"]
)
def get_doctor_list(
    token: str = Header(None),
    start: int = 0,
    limit: int = 10,
    search: str = Query("all", min_length=1, max_length=50),
    sort_by: str = Query("all", min_length=3, max_length=50),
    order: str = Query("all", min_length=3, max_length=7),
    db: Session = Depends(get_db)
):
    users.verify_token(db, token)
    data = doctors.get_doctors_list(db, start, limit, search, sort_by, order)
    return data


@router.post(
    "/doctors/sign-up",
    response_model=schemas.DoctorLoginResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Doctors"]
)
def add_doctor(
    doctor: schemas.DoctorAdd,
    db: Session =  Depends(get_db)
):
    data = doctors.add_doctor(db=db, doctor=doctor)
    return data


@router.post(
    "/doctors/sign-in",
    response_model=schemas.DoctorLoginResponse,
    status_code=status.HTTP_200_OK,
    tags=["Doctors"]
)
def sign_in(user: schemas.SignIn, db: Session = Depends(get_db)):
    data = doctors.sign_in(db, user)
    return data


@router.post(
    "/doctors/change-password",
    status_code=status.HTTP_200_OK,
    tags=["Doctors"]
)
def change_password(
    user: schemas.ChangePassword,
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    doctors.change_password(db, user=user, token=token)
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/doctors/all",
    response_model=List[schemas.Doctor],
    tags=["Doctors"]
)
def get_all_doctors(
    db: Session = Depends(get_db)
):
    data = doctors.get_all_doctors(db)
    return data


@router.get(
    "/doctors/{doctor_id}",
    response_model=schemas.Doctor,
    tags=["Doctors"]
)
def get_doctor_by_id(
    token: str = Header(None),
    doctor_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    doctors.verify_token(db, token)
    data = doctors.get_doctor(db, doctor_id)
    return data


@router.put(
    "/doctors/{doctor_id}",
    response_model=schemas.Doctor,
    tags=["Doctors"]
)
def update_doctor(
    patient: schemas.DoctorUpdate,
    token: str = Header(None),
    doctor_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    doctors.verify_token(db, token)
    data = doctors.update_doctor(db, doctor_id, patient)
    return data


@router.delete(
    "/doctors/{doctor_id}",
    status_code=status.HTTP_200_OK,
    tags=["Doctors"]
)
def delete_doctor(
    token: str = Header(None),
    doctor_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    doctors.verify_token(db, token)
    data = doctors.delete_doctor(db=db, doctor_id=doctor_id)
    return data


@router.post(
    "/doctors/{doctor_id}/specializations/{specialization_id}",
    response_model= schemas.DoctorSpecialization,
    status_code=status.HTTP_200_OK,
    tags=["Doctors"]
)
def add_doctor_specialization(
    token: str = Header(None),
    doctor_id: str = Path(..., min_length=36, max_length=36),
    specialization_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    doctors.verify_token(db, token)
    data = doctors.add_doctor_specialization(db=db, doctor_id=doctor_id, specialization_id=specialization_id)
    return data


@router.delete(
    "/doctors/{doctor_id}/specializations/{specialization_id}",
    status_code=status.HTTP_200_OK,
    tags=["Doctors"]
)
def delete_doctor_specialization(
    token: str = Header(None),
    doctor_id: str = Path(..., min_length=36, max_length=36),
    specialization_id: str = Path(..., min_length=36, max_length=36),
    db: Session = Depends(get_db)
):
    doctors.verify_token(db, token)
    doctors.delete_doctor_specialization(db=db, doctor_id=doctor_id, specialization_id=specialization_id)
    return Response(status_code=status.HTTP_200_OK)


# End Doctors


# Appointments


@router.get(
    "/appointments",
    response_model=schemas.AppointmentList,
    tags=["Appointments"]
)
def get_appointment_list(
    start: int = 0,
    limit: int = 10,
    search: str = Query("all", min_length=3, max_length=60),
    sort_by: str = Query("all", min_length=3, max_length=20),
    order: str = Query("all", min_length=3, max_length=4),
    patient_id: str = Query("all", min_length=3, max_length=36),
    doctor_id: str = Query("all", min_length=3, max_length=36),
    status: StatusEnum = Query(None),
    is_doctor: bool = True,
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    if is_doctor:
        doctors.verify_token(db, token)
    else:
        patients.verify_token(db, token)
    
    data = appointments.get_appointment_list(
        db=db,
        start=start,
        limit=limit,
        search=search,
        sort_by=sort_by,
        order=order,
        status=status,
        patient_id=patient_id,
        doctor_id=doctor_id
    )
    return data


@router.post(
    "/appointments",
    response_model=schemas.Appointment,
    status_code=status.HTTP_201_CREATED,
    tags=["Appointments"]
)
def add_appointment(
    appointment: schemas.AppointmentAdd,
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = appointments.add_appointment(db=db, appointment=appointment)
    return data


@router.get(
    "/appointments/availibility",
    tags=["Appointments"]
)
def check_appointment(
    from_time: datetime,
    to_time: datetime,
    doctor_id: str = Query(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = appointments.check_appointment(db, from_time, to_time, doctor_id)
    return data


@router.get(
    "/appointments/{appointment_id}",
    response_model=schemas.Appointment,
    tags=["Appointments"]
)
def get_appointment(
    appointment_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db),
    is_doctor: bool = True
):
    if is_doctor:
        doctors.verify_token(db, token)
    else:
        patients.verify_token(db, token)

    data = appointments.get_appintment(db=db, appointment_id=appointment_id)
    return data


@router.put(
    "/appointments/{appointment_id}",
    response_model=schemas.Appointment,
    tags=["Appointments"]
)
def update_appointment(
    appointment: schemas.AppointmentUpdate,
    appointment_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db)
):
    patients.verify_token(db, token)
    data = appointments.update_appointment(db=db, appointment=appointment, appointment_id=appointment_id)
    return data


@router.put(
    "/appointments/{appointment_id}/status",
    response_model=schemas.Appointment,
    tags=["Appointments"]
)
def update_appointment_status(
    status: StatusEnum,
    appointment_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db),
    is_doctor: bool = True
):
    if is_doctor:
        db_user = doctors.verify_token(db, token)
    else:
        db_user = patients.verify_token(db, token)
    
    data = appointments.update_appointment_status(db, appointment_id, status, db_user.id)
    return data


@router.delete(
    "/appointments/{appointment_id}",
    status_code=status.HTTP_200_OK,
    tags=["Appointments"]
)
def delete_appointment(
    appointment_id: str = Path(..., min_length=36, max_length=36),
    token: str = Header(None),
    db: Session = Depends(get_db),
):
    patients.verify_token(db, token)
    appointments.delete_appointment(db=db, appointment_id=appointment_id)
    return Response(status_code=status.HTTP_200_OK)
