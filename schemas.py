from pydantic import BaseModel
from datetime import date


class ContactCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: str
    birthday: date
    additional_data: str = None

class ContactUpdate(ContactCreate):
    pass

class ContactResponse(ContactCreate):
    id: int

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class VerifyEmailToken(BaseModel):
    sub: str  

class ResetPasswordToken(BaseModel):
    sub: str 

class User(UserBase):
    id: int
    avatar_url: str = None

    class Config:
        orm_mode = True