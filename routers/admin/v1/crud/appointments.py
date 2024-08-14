from datetime import datetime

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from libs.utils import generate_id, now, object_as_dict
from routers.admin.v1.crud.doctors import get_doctor, get_doctor_by_id
from routers.admin.v1.crud.patients import get_patient, get_patient_by_id
from models import AppointmentModel, StatusEnum
from routers.admin.v1.schemas import AppointmentAdd, AppointmentUpdate


def get_appointment_by_id(db: Session, id: str):
    return db.query(AppointmentModel).filter(AppointmentModel.is_deleted == False).first()


def check_doctor_availibility(db: Session, from_time: str, to_time: str, doctor_id: str):
    from_time = from_time.replace(tzinfo=None, microsecond=0)
    to_time = to_time.replace(tzinfo=None, microsecond=0)
    db_appointment = (
        db.query(AppointmentModel)
        .filter(
            AppointmentModel.is_deleted == False,
            AppointmentModel.status.in_(['Created', 'Rescheduled']),
            AppointmentModel.doctor_id == doctor_id,
            and_(
                AppointmentModel.from_time <= to_time,
                AppointmentModel.to_time >= from_time
            )
        )
        .all()
    )
    return db_appointment


def get_appointment_list(
    db: Session,
    start: int,
    limit: int,
    search: str,
    sort_by: str,
    order: str,
    status: StatusEnum,
    patient_id: str,
    doctor_id: str,
):
    query = db.query(AppointmentModel).filter(AppointmentModel.is_deleted == False)

    if status:
        query = query.filter(AppointmentModel.status == status.value)

    if patient_id != "all":
        query = query.filter(AppointmentModel.patient_id == patient_id)
    
    if doctor_id != "all":
        query = query.filter(AppointmentModel.doctor_id == doctor_id)

    if search != "all":
        text = f"""%{search}%"""
        query = query.filter(
            AppointmentModel.description.like(text)
        )
    
    if sort_by == "from_time":
        if order == "desc":
            query = query.order_by(AppointmentModel.from_time.desc())
        else:
            query = query.order_by(AppointmentModel.from_time)
    
    elif sort_by == "to_time":
        if order == "desc":
            query = query.order_by(AppointmentModel.to_time.desc())
        else:
            query = query.order_by(AppointmentModel.to_time)
    
    elif sort_by == "status":
        if order == "desc":
            query = query.order_by(AppointmentModel.status.desc())
        else:
            query = query.order_by(AppointmentModel.status)
    
    else:
        query = query.order_by(AppointmentModel.created_at.desc())
    

    count = query.count()
    results = query.offset(start).limit(limit).all()
    for result in results:
        if result.canceller_id:
            if db_patient := get_patient_by_id(db=db, id=result.canceller_id):
                result.canceller = db_patient
            else:
                result.canceller = get_doctor_by_id(db=db, id=result.canceller_id)

    data = {"count": count, "list": results}
    return data


def add_appointment(db: Session, appointment: AppointmentAdd):
    get_patient(db=db, patient_id=appointment.patient_id)
    get_doctor(db=db, doctor_id=appointment.doctor_id)

    if appointment.from_time >= appointment.to_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="from time is greater than to time")

    is_appointment = check_doctor_availibility(
        db=db,
        from_time=appointment.from_time,
        to_time=appointment.to_time,
        doctor_id=appointment.doctor_id
    )
    if is_appointment:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Appointment already booked on this time")
    
    db_appointment = AppointmentModel(
        id=generate_id(),
        status = StatusEnum.Created,
        **appointment.dict()
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment



def check_appointment(db: Session, from_time: datetime, to_time: datetime, doctor_id: str):
    db_appointment = check_doctor_availibility(db, from_time=from_time, to_time=to_time, doctor_id=doctor_id)
    if db_appointment:
        records = ""
        for no, record in enumerate(db_appointment, start=1):
            records += f"{no}. {record.from_time} To {record.to_time} | " 
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail=f"already booked sloats: {records}")
    return True


def get_appintment(db: Session, appointment_id: str):
    db_appointment = get_appointment_by_id(db=db, id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment is not found")
    
    if db_appointment.canceller_id:
        if db_patient := get_patient_by_id(db=db, id=db_appointment.canceller_id):
            db_appointment.canceller = db_patient
        else:
            db_appointment.canceller = get_doctor_by_id(db=db, id=db_appointment.canceller_id)
    return db_appointment


def update_appointment(db: Session, appointment: AppointmentUpdate, appointment_id: str):
    db_appointment = get_appointment_by_id(db=db, id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment is not found")
    
    if db_appointment.status == StatusEnum.Canceled or db_appointment.status == StatusEnum.Complete:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This Appoointment is closed please book new appointment")
    
    get_doctor(db=db, doctor_id=appointment.doctor_id)
    
    is_appointment = check_doctor_availibility(
        db=db,
        from_time=appointment.from_time,
        to_time=appointment.to_time,
        doctor_id=appointment.doctor_id
    )
    if is_appointment:
        raise HTTPException(status_code=status.HTTP_208_ALREADY_REPORTED, detail="Appointment already booked on this time")

    db_appointment.doctor_id = appointment.doctor_id
    db_appointment.from_time = appointment.from_time
    db_appointment.to_time = appointment.to_time
    db_appointment.description = appointment.description
    db_appointment.updated_at = now()
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


def update_appointment_status(db: Session, appointment_id: str, appointment_status: StatusEnum, user_id: str):
    db_appointment = get_appointment_by_id(db=db, id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment is not found")
    
    if appointment_status == StatusEnum.Canceled:
        db_appointment.canceller_id = user_id
    
    db_appointment.status = appointment_status
    db_appointment.updated_at = now()
    db.commit()
    db.refresh(db_appointment)
    return get_appintment(db=db, appointment_id=appointment_id)


def delete_appointment(db: Session, appointment_id: str):
    db_appointment = get_appointment_by_id(db=db, id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment is not found")
    
    db_appointment.is_deleted = True
    db_appointment.updated_at = now()
    db.commit()
    return
