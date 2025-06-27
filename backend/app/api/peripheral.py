from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.peripheral import PeripheralType, PeripheralMapping
from app.models.device import Device
from app.models.section import Section
from app.models.farm import Farm
from app.api.deps import get_db, get_current_user
from typing import List, Optional
from app.models.schedule import Schedule

router = APIRouter(prefix="/peripherals", tags=["peripherals"])

# Helper: permission check for tenant admin

def check_tenant_access(entity, current_user):
    if current_user.role == "tenant_admin":
        if hasattr(entity, 'tenant_id') and entity.tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        if hasattr(entity, 'farm_id'):
            # Section or Device
            if hasattr(entity, 'farm') and entity.farm.tenant_id != current_user.tenant_id:
                raise HTTPException(status_code=403, detail="Not enough permissions")

# 1. List peripheral types
@router.get("/types", response_model=List[dict])
def list_peripheral_types(scope: Optional[str] = Query(None), db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    q = db.query(PeripheralType)
    if scope:
        q = q.filter(PeripheralType.scope == scope)
    return [{"id": t.id, "name": t.name, "scope": t.scope} for t in q.all()]

# 2. List available GPIO pins for a device
@router.get("/devices/{device_id}/available-gpio-pins", response_model=List[int])
def available_gpio_pins(device_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    device = db.query(Device).filter(Device.id == device_id, Device.is_deleted == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    check_tenant_access(device, current_user)
    all_pins = [int(pin.strip()) for pin in (device.available_gpio_pins or '').split(',') if pin.strip().isdigit()]
    used_pins = set(
        m.gpio_pin for m in db.query(PeripheralMapping).filter_by(device_id=device_id, is_deleted=False)
    )
    return [pin for pin in all_pins if pin not in used_pins]

# 3. List peripheral mappings for a section
@router.get("/sections/{section_id}", response_model=List[dict])
def list_section_peripherals(section_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    section = db.query(Section).filter(Section.id == section_id, Section.is_deleted == False).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    check_tenant_access(section.farm, current_user)
    mappings = db.query(PeripheralMapping, PeripheralType).join(PeripheralType, PeripheralMapping.peripheral_type_id == PeripheralType.id).filter(
        PeripheralMapping.section_id == section_id, PeripheralMapping.is_deleted == False
    ).all()
    return [{
        "id": m[0].id,
        "device_id": m[0].device_id,
        "section_id": m[0].section_id,
        "peripheral_type_id": m[0].peripheral_type_id,
        "peripheral_type_name": m[1].name,
        "gpio_pin": m[0].gpio_pin,
        "is_deleted": m[0].is_deleted
    } for m in mappings]

# 4. List peripheral mappings for a farm
@router.get("/farms/{farm_id}", response_model=List[dict])
def list_farm_peripherals(farm_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    check_tenant_access(farm, current_user)
    mappings = db.query(PeripheralMapping, PeripheralType).join(PeripheralType, PeripheralMapping.peripheral_type_id == PeripheralType.id).filter(
        PeripheralMapping.farm_id == farm_id, PeripheralMapping.is_deleted == False
    ).all()
    return [{
        "id": m[0].id,
        "device_id": m[0].device_id,
        "farm_id": m[0].farm_id,
        "peripheral_type_id": m[0].peripheral_type_id,
        "peripheral_type_name": m[1].name,
        "gpio_pin": m[0].gpio_pin,
        "is_deleted": m[0].is_deleted
    } for m in mappings]

# 5. Attach peripheral to section
@router.post("/sections/{section_id}", response_model=dict)
def attach_section_peripheral(section_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    section = db.query(Section).filter(Section.id == section_id, Section.is_deleted == False).first()
    if not section:
        raise HTTPException(status_code=404, detail="Section not found")
    check_tenant_access(section.farm, current_user)
    device_id = data.get("device_id")
    peripheral_type_id = data.get("peripheral_type_id")
    gpio_pin = data.get("gpio_pin")
    # Validation
    if not all([device_id, peripheral_type_id, gpio_pin is not None]):
        raise HTTPException(status_code=400, detail="device_id, peripheral_type_id, and gpio_pin are required")
    # Only one active mapping per (section, type)
    exists = db.query(PeripheralMapping).filter_by(section_id=section_id, peripheral_type_id=peripheral_type_id, is_deleted=False).first()
    if exists:
        raise HTTPException(status_code=400, detail="A peripheral of this type is already attached to this section.")
    # Only one mapping per GPIO pin per device
    pin_used = db.query(PeripheralMapping).filter_by(device_id=device_id, gpio_pin=gpio_pin, is_deleted=False).first()
    if pin_used:
        raise HTTPException(status_code=400, detail="This GPIO pin is already in use on this device.")
    # Only allow types with correct scope
    ptype = db.query(PeripheralType).filter_by(id=peripheral_type_id, scope='section').first()
    if not ptype:
        raise HTTPException(status_code=400, detail="Invalid peripheral type for section.")
    # Only allow allowed pins
    device = db.query(Device).filter(Device.id == device_id, Device.is_deleted == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    all_pins = [int(pin.strip()) for pin in (device.available_gpio_pins or '').split(',') if pin.strip().isdigit()]
    if gpio_pin not in all_pins:
        raise HTTPException(status_code=400, detail="GPIO pin not available on this device.")
    mapping = PeripheralMapping(device_id=device_id, section_id=section_id, peripheral_type_id=peripheral_type_id, gpio_pin=gpio_pin)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return {"id": mapping.id}

# 6. Attach peripheral to farm
@router.post("/farms/{farm_id}", response_model=dict)
def attach_farm_peripheral(farm_id: int, data: dict, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    farm = db.query(Farm).filter(Farm.id == farm_id, Farm.deleted == False).first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    check_tenant_access(farm, current_user)
    device_id = data.get("device_id")
    peripheral_type_id = data.get("peripheral_type_id")
    gpio_pin = data.get("gpio_pin")
    if not all([device_id, peripheral_type_id, gpio_pin is not None]):
        raise HTTPException(status_code=400, detail="device_id, peripheral_type_id, and gpio_pin are required")
    exists = db.query(PeripheralMapping).filter_by(farm_id=farm_id, peripheral_type_id=peripheral_type_id, is_deleted=False).first()
    if exists:
        raise HTTPException(status_code=400, detail="A peripheral of this type is already attached to this farm.")
    pin_used = db.query(PeripheralMapping).filter_by(device_id=device_id, gpio_pin=gpio_pin, is_deleted=False).first()
    if pin_used:
        raise HTTPException(status_code=400, detail="This GPIO pin is already in use on this device.")
    ptype = db.query(PeripheralType).filter_by(id=peripheral_type_id, scope='farm').first()
    if not ptype:
        raise HTTPException(status_code=400, detail="Invalid peripheral type for farm.")
    device = db.query(Device).filter(Device.id == device_id, Device.is_deleted == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    all_pins = [int(pin.strip()) for pin in (device.available_gpio_pins or '').split(',') if pin.strip().isdigit()]
    if gpio_pin not in all_pins:
        raise HTTPException(status_code=400, detail="GPIO pin not available on this device.")
    mapping = PeripheralMapping(device_id=device_id, farm_id=farm_id, peripheral_type_id=peripheral_type_id, gpio_pin=gpio_pin)
    db.add(mapping)
    db.commit()
    db.refresh(mapping)
    return {"id": mapping.id}

# 7. Soft delete peripheral mapping
@router.delete("/{mapping_id}", response_model=dict)
def delete_peripheral_mapping(mapping_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mapping = db.query(PeripheralMapping).filter(PeripheralMapping.id == mapping_id, PeripheralMapping.is_deleted == False).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")
    # Check tenant access
    # Get section or farm
    if mapping.section_id is not None:
        section = db.query(Section).filter(Section.id == mapping.section_id).first()
        if section is not None:
            check_tenant_access(section.farm, current_user)
    elif mapping.farm_id is not None:
        farm = db.query(Farm).filter(Farm.id == mapping.farm_id).first()
        if farm is not None:
            check_tenant_access(farm, current_user)
    mapping.is_deleted = True  # type: ignore
    # Soft delete all schedules linked to this peripheral
    schedules = db.query(Schedule).filter(Schedule.peripheral_mapping_id == mapping.id, Schedule.is_deleted == False).all()
    for schedule in schedules:
        setattr(schedule, 'is_deleted', True)
    db.commit()
    db.refresh(mapping)
    return {"id": mapping.id, "deleted": True} 