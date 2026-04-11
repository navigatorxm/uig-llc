from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from app.config import settings
from app.auth.jwt import create_access_token, verify_token, security

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    email_match = request.email.lower() == settings.admin_email.lower()
    password_match = (
        settings.admin_password_hash
        and _pwd_context.verify(request.password, settings.admin_password_hash)
    )
    if not (email_match and password_match):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    access_token = create_access_token(
        data={"sub": request.email},
        expires_delta=timedelta(hours=24),
    )
    return TokenResponse(access_token=access_token)


@router.post("/logout")
async def logout(credentials=Depends(security)):
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_me(credentials=Depends(security)):
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"email": token_data.sub}
