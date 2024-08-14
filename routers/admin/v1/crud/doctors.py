import json
import bcrypt
import traceback

from sqlalchemy import or_
from jwcrypto import jwk, jwt
from sqlalchemy.orm import Session 
from fastapi import HTTPException, status

from config import config
from models import DoctorSpecializationModel, DoctorModel, DoctorSpecializationModel
from routers.admin.v1.crud.specializations import get_specialization
from routers.admin.v1.schemas import ChangePassword, DoctorAdd, DoctorUpdate, SignIn
from libs.utils import create_password, generate_id, get_token, now



def get_doctor_by_id(db: Session, id: str):
    return db.query(DoctorModel).filter(DoctorModel.id == id, DoctorModel.is_deleted == False).first()

def get_doctor_by_email(db: Session, email: str):
    return db.query(DoctorModel).filter(DoctorModel.email == email, DoctorModel.is_deleted == False).first()

def get_doctor_specialization(db: Session, doctor_id: str, specialization_id: str):
    db_doctor_spec = db.query(DoctorSpecializationModel).filter(DoctorSpecializationModel.doctor_id == doctor_id, DoctorSpecializationModel.specialization_id == specialization_id).first()
    return  db_doctor_spec


def get_doctors_list(
    db: Session,
    start: int,
    limit: int,
    search: str,
    sort_by: str,
    order: str
):
    query = db.query(DoctorModel).filter(DoctorModel.is_deleted == False)

    if search != "all":
        text = f"""%{search}%"""
        query = query.filter(
            or_(
                DoctorModel.first_name.like(text),
                DoctorModel.last_name.like(text),
                DoctorModel.email.like(text),
                DoctorModel.number.like(text),
            )
        )
    
    if sort_by == "first_name":
        if order == "desc":
            query = query.order_by(DoctorModel.first_name.desc())
        else:
            query = query.order_by(DoctorModel.first_name)
    elif sort_by == "last_name":
        if order == "desc":
            query = query.order_by(DoctorModel.last_name.desc())
        else:
            query = query.order_by(DoctorModel.last_name)
    elif sort_by == "eamil":
        if order == "desc":
            query = query.order_by(DoctorModel.email.desc())
        else:
            query = query.order_by(DoctorModel.email)
    elif sort_by == "created_at":
        if order == "desc":
            query = query.order_by(DoctorModel.created_at.desc())
        else:
            query = query.order_by(DoctorModel.created_at)
    else:
        query = query.order_by(DoctorModel.created_at.desc())
    
    count = query.count()
    results = query.offset(start).limit(limit).all()

    data = {"count": count, "list": results}
    return data


def add_doctor(db: Session, doctor:DoctorAdd):
    db_doctor = get_doctor_by_email(db=db, email=doctor.email)
    if db_doctor:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="doctor already exist"
        )
    specialization_id = doctor.specialization_id
    del doctor.specialization_id
    doctor.password = create_password(doctor.password)
    db_doctor = DoctorModel(
        id=generate_id(),
        **doctor.dict()
    )
    db.add(db_doctor)

    get_specialization(db=db, specialization_id=specialization_id)
    db_doctor_spec = get_doctor_specialization(db=db, doctor_id=db_doctor.id, specialization_id=specialization_id)
    if db_doctor_spec:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Already added")
    
    db_doctor_spec = DoctorSpecializationModel(
        id=generate_id(),
        doctor_id=db_doctor.id,
        specialization_id=specialization_id
    )
    db.add(db_doctor_spec)
    db.commit()
    db.refresh(db_doctor)
    db_doctor.token = get_token(db_doctor.id, db_doctor.email)
    return db_doctor


def add_doctor_specialization(db: Session, doctor_id: str, specialization_id: str):
    get_doctor(db=db, doctor_id=doctor_id)
    get_specialization(db=db, specialization_id=specialization_id)

    db_doctor_spec = DoctorSpecializationModel(
        id=generate_id(),
        doctor_id=doctor_id,
        specialization_id=specialization_id
    )
    db.add(db_doctor_spec)
    db.commit()
    db.refresh(db_doctor_spec)
    return db_doctor_spec


def delete_doctor_specialization(db: Session, doctor_id: str, specialization_id: str):
    record = db.query(DoctorSpecializationModel).filter(DoctorSpecializationModel.doctor_id == doctor_id, DoctorSpecializationModel.specialization_id==specialization_id).first()

    if record:
        db.delete(record)
        db.commit()
    return


def sign_in(db: Session, doctor: SignIn):
    db_doctor = get_doctor_by_email(db=db, email=doctor.email)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    hashed = db_doctor.password
    hashed = bytes(hashed, "utf-8")
    password = bytes(doctor.password, "utf-8")
    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    db_doctor.token = get_token(db_doctor.id, db_doctor.email)
    return db_doctor


def change_password(db: Session, user: ChangePassword, token: str):
    db_doctor = verify_token(db, token=token)
    try:
        hashed = bytes(db_doctor.password, "utf-8")
        password = bytes(user.old_password, "utf-8")
        result = bcrypt.checkpw(password, hashed)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect old password"
        )
    else:
        password = create_password(user.new_password)
        db_doctor.password = password
        db_doctor.updated_at = now()
        db.commit()


def get_doctor(db: Session, doctor_id: str):
    db_doctor = get_doctor_by_id(db=db, id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="doctor is not found")
    return db_doctor


def get_all_doctors(db: Session):
    db_doctor = db.query(DoctorModel).filter(DoctorModel.is_deleted == False).all()
    return db_doctor


def update_doctor(db: Session, doctor_id:str, doctor: DoctorUpdate):
    db_doctor = get_doctor_by_id(db=db, id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="doctor is not found")
    
    db_doctor.first_name = doctor.first_name
    db_doctor.last_name = doctor.last_name
    db_doctor.number = doctor.number
    db_doctor.updated_at = now()
    db.commit()
    db.refresh(db_doctor)
    return db_doctor


def delete_doctor(db: Session, doctor_id:str):
    db_doctor = get_doctor_by_id(db=db, id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="doctor is not found")

    db_doctor.is_deleted = True
    db_doctor.updated_at = now()
    db.commit()
    return db_doctor


def verify_token(db: Session, token: str):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token."
        )
    else:
        try:
            key = jwk.JWK(**config["jwt_key"])
            ET = jwt.JWT(key=key, jwt=token)
            ST = jwt.JWT(key=key, jwt=ET.claims)
            claims = ST.claims
            claims = json.loads(claims)
            db_doctor = get_doctor_by_id(db, claims["id"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if db_doctor is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return db_doctor