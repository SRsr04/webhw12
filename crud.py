# crud.py
from sqlalchemy.orm import Session
from datetime import date, timedelta
from fastapi import Depends, HTTPException
from models import User
from schemas import UserCreate


from database import SessionLocal
from models import Contact
from schemas import ContactCreate, ContactResponse

def create_contact(contact: ContactCreate, db: Session = Depends(SessionLocal)):
    db_contact = Contact(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact

def read_contacts(query: str = None, db: Session = Depends(SessionLocal)):
    contacts = db.query(Contact)
    if query:
        contacts = contacts.filter(
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
    return contacts.all()

def read_contact(contact_id: int, db: Session = Depends(SessionLocal)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

def update_contact(contact_id: int, contact: ContactCreate, db: Session = Depends(SessionLocal)):
    db_contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact.dict().items():
        setattr(db_contact, key, value)

    db.commit()
    db.refresh(db_contact)
    return db_contact

def delete_contact(contact_id: int, db: Session = Depends(SessionLocal)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact

def upcoming_birthdays(db: Session = Depends(SessionLocal)):
    end_date = date.today() + timedelta(days=7)
    contacts = db.query(Contact).filter(
        (Contact.birthday >= date.today()) & (Contact.birthday <= end_date)
    ).all()
    return contacts

def update_user_avatar(db: Session, user_id: int, avatar_url: str):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()

def update_user_password(db: Session, user_id: int, new_password: str):
    """
    Update the user's password.

    Parameters:
    - db (Session): Database session.
    - user_id (int): User ID.
    - new_password (str): New password.

    Returns:
    - None
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.password = new_password
        db.commit()