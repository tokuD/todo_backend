from typing import Union
from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Union[EmailStr, None] = None

class UserBase(BaseModel):
    email: EmailStr
    name: Union[str, None]

    class Config:
        orm_mode = True

class UserOutServer(UserBase):
    hashed_password: str
    is_active: bool

class UserOut(UserBase):
    pass

class UserIn(UserBase):
    row_password: str
