from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI
from datetime import timedelta, datetime
from jose import JWTError, jwt
from pydantic import BaseModel

secret_key = "your_secret_key"
ALGORITHM = "HS256"
access_token_expire_minutes = 300
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password=str):
    return pwd.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd.verify(plain_password, hashed_password)

def create_access_token(data=dict, expires_delta=timedelta):
    to_encode = data.copy()
    expires_delta = datetime.utcnow() + expires_delta if expires_delta else datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expires_delta})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt

def  decode_access_token(token=str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return payload if payload.get("sub") else None
    except JWTError:
        return None
    
    
    