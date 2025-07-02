from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from app.schemas.user import UserCreate, UserOut, UserLogin, UserUpdate
from app.services.user_service import create_user, authenticate_user, get_password_hash
from app.api.deps import get_db, require_admin, get_current_user
from jose import jwt
from datetime import timedelta, datetime
from app.core.config import settings
from app.models.user import User
from app.db.session import SessionLocal
from pydantic import BaseModel

router = APIRouter(prefix="/users", tags=["users"])

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserUpdateResponse(BaseModel):
    access_token: str
    user: UserOut

@router.post("/register", response_model=UserOut)
def register_user(user_in: UserCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    # Super admin can create any user for any tenant
    # Tenant admin can only create tenant_admin or tenant_user for their own tenant
    if current_user.role == "tenant_admin":
        if user_in.role == "super_admin":
            raise HTTPException(status_code=403, detail="Tenant admin cannot create super admins")
        # Force tenant_id to current user's tenant
        user_in.tenant_id = current_user.tenant_id
    user = create_user(db, user_in)
    return user

@router.post("/login")
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_in.username, user_in.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token = jwt.encode({
        "sub": user.username,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role == "super_admin":
        # Super admin can see all users with tenant names
        users = db.query(User).options(joinedload(User.tenant)).filter(User.deleted == False).all()
        # Add tenant_name to each user object
        for user in users:
            user.tenant_name = user.tenant.name if user.tenant else None
        return users
    else:
        # Tenant admin: only see users in their own tenant
        users = db.query(User).options(joinedload(User.tenant)).filter(
            User.tenant_id == current_user.tenant_id,
            User.deleted == False
        ).all()
        # Add tenant_name to each user object for consistency
        for user in users:
            user.tenant_name = user.tenant.name if user.tenant else None
        return users

@router.put("/me", response_model=UserUpdateResponse)
def update_me(user_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    user = db.query(User).filter(User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    allowed_fields = {"first_name", "last_name", "email", "status", "password"}
    for key, value in user_in.dict(exclude_unset=True).items():
        if key not in allowed_fields:
            continue
        if key == "password":
            setattr(user, "password_hash", get_password_hash(value))
        elif key != "password_hash":
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    access_token = jwt.encode({
        "sub": user.username,
        "role": user.role,
        "tenant_id": user.tenant_id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": access_token, "user": UserOut.model_validate(user)}

@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, user_in: UserUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == "tenant_admin":
        if user.role == "super_admin":
            raise HTTPException(status_code=403, detail="Tenant admin cannot update super admins")
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Cannot update users from another tenant")
        user_in.tenant_id = current_user.tenant_id
    for key, value in user_in.dict(exclude_unset=True).items():
        if key == "password":
            setattr(user, "password_hash", get_password_hash(value))
        elif key != "password_hash":
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user

@router.put("/{user_id}/disable", response_model=UserOut)
def disable_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == "tenant_admin":
        if user.role == "super_admin":
            raise HTTPException(status_code=403, detail="Tenant admin cannot disable super admins")
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Cannot disable users from another tenant")
    setattr(user, "deleted", True)
    db.commit()
    db.refresh(user)
    return user 