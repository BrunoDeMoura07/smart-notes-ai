from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories import user_repository


def register(db: Session, *, email: str, password: str, full_name: str | None) -> User:
    if user_repository.get_by_email(db, email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email já cadastrado.")
    return user_repository.create(
        db, email=email, hashed_password=hash_password(password), full_name=full_name
    )


def authenticate(db: Session, *, email: str, password: str) -> str:
    user = user_repository.get_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    return create_access_token(subject=str(user.id))
