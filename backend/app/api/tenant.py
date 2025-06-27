from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.tenant import Tenant
from app.api.deps import get_db, get_current_user
from app.schemas.tenant import TenantRead, TenantCreate

router = APIRouter(prefix="/tenants", tags=["tenants"])

@router.get("/", response_model=list[TenantRead])
def list_tenants(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db.query(Tenant).all()

@router.post("/", response_model=TenantRead)
def create_tenant(data: TenantCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tenant = Tenant(**data.dict())
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant

@router.put("/{tenant_id}", response_model=TenantRead)
def update_tenant(tenant_id: int, data: TenantCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    for key, value in data.dict().items():
        setattr(tenant, key, value)
    db.commit()
    db.refresh(tenant)
    return tenant 