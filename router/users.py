from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import schemas, models, auth, crud
from database import get_db


router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/create", response_model=schemas.UserOut)
def create_user(*, db: Session = Depends(get_db), user: schemas.UserIn):
    return crud.create_user(db, user)


@router.get("/", response_model=list[schemas.UserOut])
def get_users(db: Session = Depends(get_db)):
    return crud.get_users(db)


@router.get("/me", response_model=schemas.UserOut)
def read_users_me(
    current_user: schemas.UserOut = Depends(auth.get_current_active_user),
):
    return current_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user_by_id(*, db: Session = Depends(get_db), id: int):
    return crud.get_user_by_id(db, id)


@router.put("/update", response_model=schemas.UserOut)
def update_user(
    *,
    db: Session = Depends(get_db),
    user: schemas.UserIn,
    current_user: schemas.UserIn = Depends(auth.get_current_active_user)
):
    user.email = current_user.email
    return crud.update_user(db, user)


@router.put("/deactivate", response_model=schemas.UserOut)
def deactivate_user(
    *,
    db: Session = Depends(get_db),
    current_user: schemas.UserIn = Depends(auth.get_current_active_user)
):
    return crud.deactivate_user(db, current_user.email)


@router.delete("/delete")
def delete_user(
    *,
    db: Session = Depends(get_db),
    current_user: schemas.UserIn = Depends(auth.get_current_active_user)
):
    return crud.delete_user(db, current_user.email)
