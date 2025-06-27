from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.user_service import get_user_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"

# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency to get current user from JWT

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

# Dependency to enforce admin roles

def require_admin(current_user = Depends(get_current_user)):
    if current_user.role not in ["super_admin", "tenant_admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    return current_user 