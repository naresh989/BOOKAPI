from passlib.context import CryptContext
import jwt
from datetime import timedelta,datetime
from src.config import Config
from fastapi.exceptions import HTTPException
from fastapi import Depends, Request, status
import uuid
import logging
passwd_context = CryptContext(
    schemes = ['bcrypt']
)

ACCESS_TOKEN_EXPIRY=36000

def generate_passwd_hash(password : str)->str:
    hash=passwd_context.hash(password)
    return hash
def verify_password(password:str , hash :str) -> bool:
    return passwd_context.verify(password,hash)


def create_access_token(user_data: dict , expiry :timedelta = None ,refresh: bool =False) -> str:
    
    payload = {
        'user':user_data,
        'exp': datetime.utcnow() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY)),
        'jti': str(uuid.uuid4()),
        'refresh' : refresh
    }
    token=jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )

    return token

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.ExpiredSignatureError:
        logging.error("Token has expired")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token has expired. Please login again."
        )
    except jwt.InvalidTokenError:
        logging.error("Invalid token provided")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token"
        )
    except jwt.PyJWTError as e:
        logging.exception(f"Error decoding token: {e}")
        return None


