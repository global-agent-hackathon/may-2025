from typing import Optional

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: str


class User(BaseModel):
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    google_id: str
    is_active: bool = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    email: Optional[str] = None
    sub: Optional[str] = None


class GoogleToken(BaseModel):
    access_token: str
    expires_in: int
    token_type: str
    scope: str
    id_token: str


class GoogleUserInfo(BaseModel):
    id: str
    email: EmailStr
    verified_email: bool
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None
    locale: Optional[str] = None
