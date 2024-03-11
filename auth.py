from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt import encode
from datetime import datetime, timedelta

from database import SessionLocal
from crud import create_user, get_user_by_email, verify_password
from dependencies import get_current_user
from schemas import User

router = APIRouter()


@router.post("/register/", response_model=User)
def register_user(user: User, db: SessionLocal = Depends()): # type: ignore
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    db_user = create_user(db, user)
    return db_user


@router.post("/token/")
def generate_token(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends()): # type: ignore
    user = get_user_by_email(db, email=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=15)
    access_token_payload = {"sub": user.email, "exp": datetime.utcnow() + access_token_expires}
    access_token = encode(access_token_payload, "secret_key", algorithm="HS256")

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user