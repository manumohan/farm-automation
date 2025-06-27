from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.device import Device
from app.api.deps import get_db, get_current_user
from app.schemas.device import DeviceOut, DeviceCreate

router = APIRouter(prefix="/devices", tags=["devices"])

@router.get("/", response_model=list[DeviceOut])
def list_devices(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return db.query(Device).all()

@router.post("/", response_model=DeviceOut)
def create_device(device_in: DeviceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    # Validation: Only one non-deleted device per farm
    existing_device = db.query(Device).filter(Device.farm_id == device_in.farm_id, Device.is_deleted == False).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="A device already exists for this farm. Only one non-deleted device is allowed per farm.")
    device = Device(**device_in.dict(exclude_unset=True))
    db.add(device)
    db.commit()
    db.refresh(device)
    return device

@router.put("/{device_id}", response_model=DeviceOut)
def update_device(device_id: int, device_in: DeviceCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    device = db.query(Device).filter(Device.id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    for key, value in device_in.dict(exclude_unset=True).items():
        setattr(device, key, value)
    db.commit()
    db.refresh(device)
    return device

@router.delete("/{device_id}", response_model=DeviceOut)
def delete_device(device_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role not in ["tenant_admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    device = db.query(Device).filter(Device.id == device_id, Device.is_deleted == False).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    device.is_deleted = True
    db.commit()
    db.refresh(device)
    return device 