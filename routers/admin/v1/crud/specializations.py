from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from libs.utils import generate_id, now
from models import SpecializationModel, DoctorSpecializationModel
from routers.admin.v1.schemas import SpecializationAdd

def get_specialization_by_name(db: Session, name:str):
    db_spec = db.query(SpecializationModel).filter(SpecializationModel.name == name, SpecializationModel.is_deleted == False).first()
    return db_spec

def get_specialization_by_id(db: Session, id:str):
    db_spec = db.query(SpecializationModel).filter(SpecializationModel.id == id, SpecializationModel.is_deleted == False).first()
    return db_spec


def get_specialization_list(
    db: Session,
    start: int,
    limit: int,
    search: str,
    sort_by: str,
    order: str
):
    query = db.query(SpecializationModel).filter(SpecializationModel.is_deleted == False)

    if search != "all":
        text = f"""%{search}%"""
        query = query.filter(
            or_(
                SpecializationModel.name.like(text),
                SpecializationModel.description.like(text),
            )
        )

        if sort_by == "name":
            if order == "desc":
                query = query.order_by(SpecializationModel.first_name.desc())
            else:
                query = query.order_by(SpecializationModel.first_name)
        elif sort_by == "deacription":
            if order == "desc":
                query = query.order_by(SpecializationModel.last_name.desc())
            else:
                query = query.order_by(SpecializationModel.last_name)
        else:
            query = query.order_by(SpecializationModel.created_at.desc())

    count = query.count()
    results = query.offset(start).limit(limit).all()
    data = {"count": count, "list": results}
    return data


def add_specialization(db: Session, specialization: SpecializationAdd):
    db_spec = get_specialization_by_name(db=db, name=specialization.name)
    if db_spec:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Specialization already addded")
    
    db_spec = SpecializationModel(
        id= generate_id(),
        **specialization.dict())
    db.add(db_spec)
    db.commit()
    db.refresh(db_spec)
    return db_spec


def get_specialization(db: Session, specialization_id: str):
    db_spec = get_specialization_by_id(db=db, id=specialization_id)
    if db_spec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="specialization is not found")
    return db_spec


def get_specialization_doctors(db: Session, specialization_id: str):
    db_spec_doctors = db.query(DoctorSpecializationModel).filter(DoctorSpecializationModel.specialization_id == specialization_id).all()
    return db_spec_doctors


def get_all_specialization(db: Session):
    db_spec = db.query(SpecializationModel).filter(SpecializationModel.is_deleted == False).all()
    return db_spec


def update_specialization(db: Session, specialization_id: str, specialization: SpecializationAdd):
    db_spec = get_specialization_by_id(db=db, id=specialization_id)
    if db_spec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="specialization is not found")
    
    db_spec_name = get_specialization_by_name(db=db, name=specialization.name)
    if db_spec_name:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Specialization already addded")
    
    db_spec.name = specialization.name
    db_spec.description = specialization.description
    db_spec.updated_at = now()
    db.commit()
    db.refresh(db_spec)
    return db_spec


def delete_specialization(db: Session,  specialization_id: str):
    db_spec = get_specialization_by_id(db=db, id=specialization_id)
    if db_spec is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="specialization is not found")
    
    db_spec.is_deleted = True
    db_spec.updated_at = now()
    db.commit()
    db.refresh(db_spec)
    return
