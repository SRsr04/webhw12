from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt import PyJWTError
from pydantic import ValidationError
from datetime import datetime, timedelta

from crud import get_user_by_email
from database import SessionLocal
from models import User
from schemas import VerifyEmailToken

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme), db: SessionLocal = Depends()) -> User: # type: ignore
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    db_user = get_user_by_email(db, email=email)
    if db_user is None:
        raise credentials_exception
    return db_user


def verify_email_token(token: str) -> VerifyEmailToken:
    try:
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return VerifyEmailToken(**payload)
    except (PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate email token",
        )


def rate_limit_user(rate: int = 1):
    counter = {}

    async def _rate_limit_user(email: str):
        now = datetime.now().timestamp()
        if email in counter:
            if counter[email][0] + 60 < now:
                counter[email] = (now, 1)
            elif counter[email][1] < rate:
                counter[email] = (counter[email][0], counter[email][1] + 1)
            else:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests",
                )
        else:
            counter[email] = (now, 1)
    return _rate_limit_user
