from typing import Union
from fastapi import APIRouter
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from pydantic import EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
import crud
from fastapi import Depends, HTTPException, status
import schemas
from hash import verify_password, hash_password
from database import get_db
from schemas import TokenData
from config import settings

router = APIRouter(tags=["Authentication"], prefix="/auth")


# openssl rand -hex 32
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

oauth2_schema = OAuth2PasswordBearer(tokenUrl="/auth/token")


def authenticate_user(db: Session, email: EmailStr, row_password: str):
    user = crud.get_user_by_email(db, email)
    if not verify_password(row_password, user.hashed_password):
        return False
    return user


def create_access_token(payload: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = payload.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_schema)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentails",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("email")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    return user


async def get_current_active_user(
    current_user: schemas.UserOutServer = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = authenticate_user(
        db=db, email=form_data.username, row_password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        payload={"email": user.email}, expires_delta=access_token_expires
    )
    return schemas.Token(access_token=access_token, token_type="bearer").dict()
