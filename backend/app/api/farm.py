from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.farm import Farm
from app.schemas.farm import FarmCreate, FarmUpdate, FarmOut
from app.api.deps import get_db, get_current_user, require_admin
from app.models.tenant import Tenant
from sqlalchemy.orm import joinedload
from app.models.section import Section
from app.models.peripheral import PeripheralMapping
from app.models.schedule import Schedule

router = APIRouter(prefix="/farms", tags=["farms"])

@router.get("/", response_model=list[FarmOut])
def list_farms(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if current_user.role == "super_admin":
        # Super admin can see all farms with tenant names
        farms = db.query(Farm).options(joinedload(Farm.tenant)).filter(Farm.deleted == False).all()
        # Add tenant_name to each farm object
        for farm in farms:
            farm.tenant_name = farm.tenant.name if farm.tenant else None
        print(f"Super admin farms data: {[{'id': f.id, 'name': f.name, 'tenant_name': f.tenant_name} for f in farms]}")  # Debug log
        return farms
    else:
        # Tenant admin can only see farms in their tenant, but still load tenant info for consistency
        farms = db.query(Farm).options(joinedload(Farm.tenant)).filter(
            Farm.tenant_id == current_user.tenant_id,
            Farm.deleted == False
        ).all()
        # Add tenant_name to each farm object
        for farm in farms:
            farm.tenant_name = farm.tenant.name if farm.tenant else None
        print(f"Tenant admin farms data: {[{'id': f.id, 'name': f.name, 'tenant_name': f.tenant_name} for f in farms]}")  # Debug log
        return farms

@router.post("/", response_model=FarmOut)
def create_farm(farm_in: FarmCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Set tenant_id based on user role
    if current_user.role == "super_admin":
        if not farm_in.tenant_id:
            raise HTTPException(status_code=400, detail="Tenant ID is required for super admin")
        tenant_id = farm_in.tenant_id
    else:
        # Tenant admin can only create farms in their own tenant
        tenant_id = current_user.tenant_id
    
    # Check if tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    
    # Check if farm_code is unique within the tenant (excluding deleted farms)
    existing_farm = db.query(Farm).filter(
        Farm.tenant_id == tenant_id,
        Farm.farm_code == farm_in.farm_code,
        Farm.deleted == False
    ).first()
    if existing_farm:
        raise HTTPException(status_code=400, detail="Farm code must be unique within the tenant")
    
    farm = Farm(
        tenant_id=tenant_id,
        name=farm_in.name,
        farm_code=farm_in.farm_code,
        description=farm_in.description,
        location=farm_in.location,
        total_area=farm_in.total_area,
        farm_owner_name=farm_in.farm_owner_name
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)
    return farm

@router.get("/{farm_id}", response_model=FarmOut)
def get_farm(farm_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role == "tenant_admin" and farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return farm

@router.put("/{farm_id}", response_model=FarmOut)
def update_farm(farm_id: int, farm_in: FarmUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role == "tenant_admin" and farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if farm_code is unique within the tenant (excluding deleted farms)
    if farm_in.farm_code and farm_in.farm_code != farm.farm_code:
        existing_farm = db.query(Farm).filter(
            Farm.tenant_id == farm.tenant_id,
            Farm.farm_code == farm_in.farm_code,
            Farm.deleted == False,
            Farm.id != farm_id
        ).first()
        if existing_farm:
            raise HTTPException(status_code=400, detail="Farm code must be unique within the tenant")
    
    # Update fields
    for key, value in farm_in.dict(exclude_unset=True).items():
        setattr(farm, key, value)
    
    db.commit()
    db.refresh(farm)
    return farm

@router.delete("/{farm_id}", response_model=FarmOut)
def delete_farm(farm_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role == "tenant_admin" and farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Soft delete
    setattr(farm, "deleted", True)
    # Soft delete all sections, peripherals, and schedules linked to this farm
    # Sections
    sections = db.query(Section).filter(Section.farm_id == farm_id, Section.is_deleted == False).all()
    for section in sections:
        setattr(section, 'is_deleted', True)
    # Peripherals (farm and section)
    peripherals = db.query(PeripheralMapping).filter(PeripheralMapping.farm_id == farm_id, PeripheralMapping.is_deleted == False).all()
    # Also get section peripherals
    section_ids = [section.id for section in sections]
    if section_ids:
        peripherals += db.query(PeripheralMapping).filter(PeripheralMapping.section_id.in_(section_ids), PeripheralMapping.is_deleted == False).all()
    for peripheral in peripherals:
        setattr(peripheral, 'is_deleted', True)
        # Schedules for this peripheral
        schedules = db.query(Schedule).filter(Schedule.peripheral_mapping_id == peripheral.id, Schedule.is_deleted == False).all()
        for schedule in schedules:
            setattr(schedule, 'is_deleted', True)
    db.commit()
    db.refresh(farm)
    return farm 