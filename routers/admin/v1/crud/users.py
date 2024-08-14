import json
import traceback
import bcrypt

from sqlalchemy import or_
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jwcrypto import jwk, jwt

from libs.utils import create_password, generate_id, get_token, now
from models import AdminUserModel
from config import config
from routers.admin.v1.schemas import ChangePassword, SignIn, UserSignUp, UserUpdate


def get_user_by_id(db: Session, id: str):
    return db.query(AdminUserModel).filter(AdminUserModel.id == id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(AdminUserModel).filter(AdminUserModel.email == email).first()


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
            db_patient = get_user_by_id(db, claims["id"])
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


def add_user(db: Session, user: UserSignUp):
    id = generate_id()
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exist."
        )
    user.password = create_password(user.password)
    db_user = AdminUserModel(id=id, **user.dict)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return user


def sign_in(db: Session, user: SignIn):
    db_user = get_user_by_email(db, email=user.email)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    hashed = db_user.password
    hashed = bytes(hashed, "utf-8")
    password = bytes(user.password, "utf-8")
    if not bcrypt.checkpw(password, hashed):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    db_user.token = get_token(db_user.id, db_user.email)
    get_token(db_user.id, db_user.email)
    return db_user


def change_password(db: Session, user: ChangePassword, token: str):
    db_user = verify_token(db, token=token)
    try:
        hashed = bytes(db_user.password, "utf-8")
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
        db_user.password = password
        db_user.updated_at = now()
        db.commit()


def get_users(
    db: Session, start: int, limit: int, sort_by: str, order: str, search: str
):
    query = db.query(AdminUserModel).filter(AdminUserModel.is_deleted == False)

    if search != "all":
        text = f"""%{search}%"""
        query = query.filter(
            or_(
                AdminUserModel.first_name.like(text),
                AdminUserModel.last_name.like(text),
                AdminUserModel.email.like(text),
            )
        )

    if sort_by == "first_name":
        if order == "desc":
            query = query.order_by(AdminUserModel.first_name.desc())
        else:
            query = query.order_by(AdminUserModel.first_name)
    elif sort_by == "last_name":
        if order == "desc":
            query = query.order_by(AdminUserModel.last_name.desc())
        else:
            query = query.order_by(AdminUserModel.last_name)
    elif sort_by == "email":
        if order == "desc":
            query = query.order_by(AdminUserModel.email.desc())
        else:
            query = query.order_by(AdminUserModel.email)
    else:
        query = query.order_by(AdminUserModel.created_at.desc())

    count = query.count()
    results = query.offset(start).limit(limit).all()
    data = {"count": count, "list": results}
    return data


def get_user_profile(db: Session, user_id: str):
    db_user = get_user_by_id(db, id=user_id)
    return db_user


def update_user_profile(db: Session, user_id: str, user: UserUpdate):
    db_user = get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    db_user.first_name = user.first_name
    db_user.last_name = user.last_name
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: str):
    db_user = get_user_by_id(db, id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    db_user.is_deleted = True
    db_user.updated_at = now()
    db.commit()
    return
