import uuid

import jwt
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories import user_repository


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais.",
    )
    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_error

    try:
        user_id = decode_access_token(token)
    except jwt.PyJWTError:
        raise credentials_error

    user = user_repository.get_by_id(db, uuid.UUID(user_id))
    if user is None:
        raise credentials_error
    return user
