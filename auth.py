from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jwt import encode, decode, PyJWTError
from datetime import datetime, timedelta

from pydantic import ValidationError

from database import SessionLocal
from crud import create_user, get_user_by_email, verify_password, update_user_avatar, update_user_password
from dependencies import get_current_user, verify_email_token
from schemas import UserCreate, User, VerifyEmailToken, ResetPasswordToken
from settings import Settings


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

@router.post("/verify-email/")
def verify_email(token: str = Depends(verify_email_token), db: SessionLocal = Depends()): # type: ignore
    user = get_user_by_email(db, email=token.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    user.is_verified = True
    db.commit()
    return {"message": "Email verified successfully"}


@router.put("/update-avatar/")
def update_avatar(avatar_url: str, current_user: User = Depends(get_current_user), db: SessionLocal = Depends()): # type: ignore
    update_user_avatar(db, user_id=current_user.id, avatar_url=avatar_url)
    return {"message": "Avatar updated successfully"}

@router.post("/reset-password/")
def reset_password(token: str, new_password: str, db: SessionLocal = Depends()): # type: ignore
    try:
        payload = decode(token, Settings.secret_key, algorithms=["HS256"])
        token_data = ResetPasswordToken(**payload)
    except (PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate reset password token",
        )

    user = get_user_by_email(db, email=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    hashed_password = "hash_new_password_here"  # Use a proper password hashing library
    update_user_password(db, user_id=user.id, new_password=hashed_password)
    return {"message": "Password reset successful"}