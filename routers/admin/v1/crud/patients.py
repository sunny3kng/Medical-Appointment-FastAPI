import json
import traceback

import bcrypt
from sqlalchemy import or_
from jwcrypto import jwk, jwt
from sqlalchemy.orm import Session 
from fastapi import HTTPException, status

from config import config
from models import GenderEnum, PatientModel
from routers.admin.v1.schemas import ChangePassword, PatientsAdd, PatientUpdate, SignIn
from libs.utils import create_password, generate_id, get_token, now


def get_patient_by_id(db: Session, id: str):
    return db.query(PatientModel).filter(PatientModel.id == id).first()

def get_patient_by_email(db: Session, email: str):
    return db.query(PatientModel).filter(PatientModel.email == email).first()


def get_patients_list(
    db: Session,
    start: int,
    limit: int,
    search: str,
    sort_by: str,
    order: str,
    gender: GenderEnum
):
    query = db.query(PatientModel)

    if gender:
        query = query.filter(PatientModel.gender == gender.value)
    
    if search != "all":
        text = f"""%{search}%"""
        query = query.filter(
            or_(
                PatientModel.first_name.like(text),
                PatientModel.last_name.like(text),
                PatientModel.email.like(text),
                PatientModel.number.like(text),
            )
        )
    
    if sort_by == "first_name":
        if order == "desc":
            query = query.order_by(PatientModel.first_name.desc())
        else:
            query = query.order_by(PatientModel.first_name)
    elif sort_by == "last_name":
        if order == "desc":
            query = query.order_by(PatientModel.last_name.desc())
        else:
            query = query.order_by(PatientModel.last_name)
    elif sort_by == "eamil":
        if order == "desc":
            query = query.order_by(PatientModel.email.desc())
        else:
            query = query.order_by(PatientModel.email)
    elif sort_by == "gender":
        if order == "desc":
            query = query.order_by(PatientModel.gender.desc())
        else:
            query = query.order_by(PatientModel.gender)
    elif sort_by == "height":
        if order == "desc":
            query = query.order_by(PatientModel.height.desc())
        else:
            query = query.order_by(PatientModel.height)
    elif sort_by == "weight":
        if order == "desc":
            query = query.order_by(PatientModel.weight.desc())
        else:
            query = query.order_by(PatientModel.weight)
    elif sort_by == "created_at":
        if order == "desc":
            query = query.order_by(PatientModel.created_at.desc())
        else:
            query = query.order_by(PatientModel.created_at)
    else:
        query = query.order_by(PatientModel.created_at.desc())
    
    count = query.count()
    results = query.offset(start).limit(limit).all()
    data = {"count": count, "list": results}
    return data


def add_patient(db: Session, patient:PatientsAdd):
    db_patient = get_patient_by_email(db=db, email=patient.email)
    if db_patient:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="patient already exist"
        )
    patient.password = create_password(patient.password)
    db_patient = PatientModel(
        id=generate_id(),
        **patient.dict()
    )
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    db_patient.token = get_token(db_patient.id, db_patient.email)
    return db_patient


def sign_in(db: Session, patient: SignIn):
    db_patient = get_patient_by_email(db=db, email=patient.email)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    hashed = db_patient.password
    hashed = bytes(hashed, "utf-8")
    password = bytes(patient.password, "utf-8")
    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    db_patient.token = get_token(db_patient.id, db_patient.email)
    return db_patient


def change_password(db: Session, user: ChangePassword, token: str):
    db_patient = verify_token(db, token=token)
    try:
        hashed = bytes(db_patient.password, "utf-8")
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
        db_patient.password = password
        db_patient.updated_at = now()
        db.commit()


def get_patient(db: Session, patient_id: str):
    db_patient = get_patient_by_id(db=db, id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patirnt is not found")
    return db_patient


def get_all_patients(db: Session):
    db_patient = db.query(PatientModel).all()
    return db_patient


def update_patient(db: Session, patient_id:str, patient: PatientUpdate):
    db_patient = get_patient_by_id(db=db, id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="patirnt is not found")
    
    db_patient.first_name = patient.first_name
    db_patient.last_name = patient.last_name
    db_patient.number = patient.number
    db_patient.gender = patient.gender
    db_patient.height = patient.height
    db_patient.weight = patient.weight
    db_patient.updated_at = now()
    db.commit()
    return db_patient


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
            db_patient = get_patient_by_id(db, claims["id"])
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token."
            )
        except Exception as e:
            print(e)
            print(traceback.format_exc())
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        if db_patient is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return db_patient

