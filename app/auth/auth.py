from fastapi import HTTPException, Header, status
from jose import jwt, JWTError

from ..config import settings


def get_current_user_id(token: str = Header(..., alias="Authorization")):
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing Authorization header")
    try:
        payload = jwt.decode(token[len("Bearer "):], settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload.get('id')
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")