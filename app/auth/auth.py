from fastapi import HTTPException, Header, status
from jose import jwt, JWTError

import httpx

from ..config import settings


def get_current_user_id(token: str = Header(..., alias="Authorization")):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Authorization header")
    try:
        payload = jwt.decode(token[len("Bearer "):], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get('id')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")


def user_is_admin(user_id: int) -> bool:
    try:
        if httpx.get(f'{settings.auth_service_address}/{user_id}/is_admin').status_code == status.HTTP_200_OK:
            return True
        return False
    except:
        return False
