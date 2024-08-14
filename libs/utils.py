import bcrypt

from jwcrypto import jwk, jwt
from sqlalchemy import inspect

from uuid import uuid4
from datetime import datetime

from config import config


def now():
    return datetime.now()


def generate_id():
    id = str(uuid4())
    return id

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}


def create_password(password):
    password = bytes(password, "utf-8")
    password = bcrypt.hashpw(password, config["salt"])
    password = password.decode("utf-8")
    return password


def get_token(user_id, email):
    claims = {"id": user_id, "email": email, "time": str(now())}

    # Create a signed token with the generated key
    key = jwk.JWK(**config["jwt_key"])
    Token = jwt.JWT(header={"alg": "HS256"}, claims=claims)
    Token.make_signed_token(key)

    # Further encrypt the token with the same key
    encrypted_token = jwt.JWT(
        header={"alg": "A256KW", "enc": "A256CBC-HS512"}, claims=Token.serialize()
    )
    encrypted_token.make_encrypted_token(key)
    token = encrypted_token.serialize()
    return token

