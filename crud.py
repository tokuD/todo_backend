from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from pydantic import EmailStr
from hash import hash_password


def get_user_by_id(db: Session, user_id: int) -> schemas.UserOut:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"The user with id {user_id} is not found.",
        )
    return user


def get_user_by_email(db: Session, email: EmailStr) -> schemas.UserOutServer:
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"The user with email {email} is not found.",
        )
    return user


def get_users(
    db: Session, offset: int = 0, limit: int = 10, order: list[str] | None = None
) -> list[schemas.UserOut]:
    if order is None:
        return db.query(models.User).offset(offset).limit(limit).all()
    return db.query(models.User).order_by(*order).offset(offset).limit(limit).all()


def create_user(db: Session, user: schemas.UserIn) -> schemas.UserOut:
    hashed_password = hash_password(user.row_password)
    db_user = models.User(
        **user.dict(exclude={"row_password"}), hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: schemas.UserIn) -> schemas.UserOut:
    db_user = db.query(models.User).filter(models.User.email == user.email)
    if db_user.first() is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"The user with email {user.email} is not found.",
        )
    hashed_password = hash_password(user.row_password)
    new_user = user.dict(exclude={"row_password"})
    new_user.update({"hashed_password": hashed_password})
    db_user.update(new_user)
    db.commit()
    return get_user_by_email(db, user.email)


def deactivate_user(db: Session, email: EmailStr) -> schemas.UserOut:
    db_user = db.query(models.User).filter(models.User.email == email)
    if db_user.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with email {email} is not found.",
        )
    db_user.update({models.User.is_active: False})
    return db_user.first()


def delete_user(db: Session, email: EmailStr):
    db_user = db.query(models.User).filter(models.User.email == email)
    if db_user.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The user with email {email} is not found.",
        )
    db_user.delete()
    return {"message": "deleted"}
