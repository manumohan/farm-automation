from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.db.session import SessionLocal
from app.models.section import Section
from app.models.farm import Farm
from app.schemas.section import SectionCreate, SectionUpdate, SectionOut
from app.api.deps import get_db, get_current_user, require_admin
from typing import List
from app.models.peripheral import PeripheralMapping
from app.models.schedule import Schedule

router = APIRouter(prefix="/sections", tags=["sections"])

@router.get("/", response_model=List[SectionOut])
def list_sections(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    if current_user.role == "super_admin":
        # Super admin can see all sections with farm names
        sections = db.query(Section).options(joinedload(Section.farm)).filter(Section.is_deleted == False).all()
        # Add farm_name to each section object
        for section in sections:
            section.farm_name = section.farm.name if section.farm else None
        return sections
    else:
        # Tenant admin can only see sections in their tenant's farms
        sections = db.query(Section).options(joinedload(Section.farm)).join(Farm).filter(
            Farm.tenant_id == current_user.tenant_id,
            Section.is_deleted == False
        ).all()
        # Add farm_name to each section object
        for section in sections:
            section.farm_name = section.farm.name if section.farm else None
        return sections

@router.get("/farm/{farm_id}", response_model=List[SectionOut])
def list_sections_by_farm(farm_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if farm exists and user has access
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if current_user.role == "tenant_admin" and farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    sections = db.query(Section).filter(
        Section.farm_id == farm_id,
        Section.is_deleted == False
    ).all()
    
    # Add farm_name to each section object
    for section in sections:
        section.farm_name = farm.name
    
    return sections

@router.post("/", response_model=SectionOut)
def create_section(section_in: SectionCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if farm exists and user has access
    farm = db.query(Farm).filter(Farm.id == section_in.farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if current_user.role == "tenant_admin" and farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if section_code is unique within the farm (excluding deleted sections)
    existing_section = db.query(Section).filter(
        Section.farm_id == section_in.farm_id,
        Section.section_code == section_in.section_code,
        Section.is_deleted == False
    ).first()
    if existing_section:
        raise HTTPException(status_code=400, detail="Section code must be unique within the farm")
    
    section = Section(
        farm_id=section_in.farm_id,
        name=section_in.name,
        section_code=section_in.section_code,
        description=section_in.description,
        crop_type=section_in.crop_type,
        area=section_in.area,
        section_incharge_name=section_in.section_incharge_name,
        notes=section_in.notes
    )
    db.add(section)
    db.commit()
    db.refresh(section)
    return section

@router.get("/{section_id}", response_model=SectionOut)
def get_section(section_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    section = db.query(Section).options(joinedload(Section.farm)).filter(
        Section.id == section_id, 
        Section.is_deleted == False
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Check if user has access to this section's farm
    if current_user.role == "tenant_admin" and section.farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Add farm_name
    section.farm_name = section.farm.name if section.farm else None
    
    return section

@router.put("/{section_id}", response_model=SectionOut)
def update_section(section_id: int, section_in: SectionUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    section = db.query(Section).options(joinedload(Section.farm)).filter(
        Section.id == section_id, 
        Section.is_deleted == False
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Check if user has access to this section's farm
    if current_user.role == "tenant_admin" and section.farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check if section_code is unique within the farm (if being updated)
    if section_in.section_code and section_in.section_code != section.section_code:
        existing_section = db.query(Section).filter(
            Section.farm_id == section.farm_id,
            Section.section_code == section_in.section_code,
            Section.is_deleted == False,
            Section.id != section_id
        ).first()
        if existing_section:
            raise HTTPException(status_code=400, detail="Section code must be unique within the farm")
    
    # Update fields
    for key, value in section_in.dict(exclude_unset=True).items():
        setattr(section, key, value)
    
    db.commit()
    db.refresh(section)
    
    # Add farm_name
    section.farm_name = section.farm.name if section.farm else None
    
    return section

@router.delete("/{section_id}", response_model=SectionOut)
def delete_section(section_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    section = db.query(Section).options(joinedload(Section.farm)).filter(
        Section.id == section_id, 
        Section.is_deleted == False
    ).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    
    # Check if user has access to this section's farm
    if current_user.role == "tenant_admin" and section.farm.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Soft delete
    setattr(section, "is_deleted", True)
    # Soft delete all peripherals and their schedules linked to this section
    peripherals = db.query(PeripheralMapping).filter(PeripheralMapping.section_id == section_id, PeripheralMapping.is_deleted == False).all()
    for peripheral in peripherals:
        setattr(peripheral, 'is_deleted', True)
        schedules = db.query(Schedule).filter(Schedule.peripheral_mapping_id == peripheral.id, Schedule.is_deleted == False).all()
        for schedule in schedules:
            setattr(schedule, 'is_deleted', True)
    db.commit()
    db.refresh(section)
    
    # Add farm_name
    section.farm_name = section.farm.name if section.farm else None
    
    return section 