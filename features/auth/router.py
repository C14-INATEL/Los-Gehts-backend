from fastapi import APIRouter, HTTPException, status

from features.auth.service import AuthService
from features.auth.squema import UserCreate, UserLogin
from features.core.database import db
from features.core.jwt_handler import JWTHandler

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService(db, JWTHandler())


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: UserCreate):
    # register
    return auth_service.register()
