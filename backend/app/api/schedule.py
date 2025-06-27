from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.schedule import Schedule
from app.models.peripheral import PeripheralMapping, PeripheralType
from app.api.deps import get_db, get_current_user, require_admin
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleOut
from typing import List
from datetime import timedelta, datetime
from sqlalchemy import func
from croniter import croniter

router = APIRouter(prefix="/schedules", tags=["schedules"])

# Helper to check if two time windows overlap
def windows_overlap(start1, end1, start2, end2):
    return max(start1, start2) < min(end1, end2)

# Helper to get next N occurrences for a cron expression
def get_next_occurrences(cron_expr, base_dt, n=5):
    itr = croniter(cron_expr, base_dt)
    return [itr.get_next(datetime) for _ in range(n)]

@router.get("/peripheral/{mapping_id}", response_model=List[ScheduleOut])
def list_schedules(mapping_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    mapping = db.query(PeripheralMapping).filter(PeripheralMapping.id == mapping_id, PeripheralMapping.is_deleted == False).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Peripheral mapping not found")
    # TODO: Add tenant/farm/section RBAC check
    schedules = db.query(Schedule).filter(Schedule.peripheral_mapping_id == mapping_id, Schedule.is_deleted == False).all()
    return schedules

@router.post("/peripheral/{mapping_id}", response_model=ScheduleOut)
def create_schedule(mapping_id: int, schedule_in: ScheduleCreate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    mapping = db.query(PeripheralMapping).filter(PeripheralMapping.id == mapping_id, PeripheralMapping.is_deleted == False).first()
    if not mapping:
        raise HTTPException(status_code=404, detail="Peripheral mapping not found")
    ptype = db.query(PeripheralType).filter(PeripheralType.id == mapping.peripheral_type_id).first() if mapping else None
    # Robust exclusivity: check for overlap with all exclusive schedules in the same section/farm
    if ptype is not None and bool(getattr(ptype, 'exclusive_schedule', False)):
        print(f"[DEBUG] Checking exclusivity for mapping_id={mapping_id}, ptype={ptype.name}, exclusive_schedule={ptype.exclusive_schedule}")
        # Always check at the farm level for exclusivity, across all exclusive types
        farm_id = mapping.farm_id if mapping is not None and getattr(mapping, 'farm_id', None) is not None else None
        if farm_id is None and mapping is not None and getattr(mapping, 'section_id', None) is not None:
            from app.models.section import Section
            section = db.query(Section).filter(Section.id == mapping.section_id).first()
            if section:
                farm_id = section.farm_id
        print(f"[DEBUG] farm_id for exclusivity: {farm_id}")
        if farm_id is not None:
            # Get all exclusive peripheral type IDs
            exclusive_type_ids = [pt.id for pt in db.query(PeripheralType).filter(PeripheralType.exclusive_schedule == True).all()]
            print(f"[DEBUG] exclusive_type_ids: {exclusive_type_ids}")
            # Get all section IDs for this farm
            section_ids = [s.id for s in db.query(Section).filter(Section.farm_id == farm_id).all()]
            print(f"[DEBUG] section_ids in farm: {section_ids}")
            # Get all mappings in the farm (direct or via section) with exclusive types
            all_mappings = db.query(PeripheralMapping).filter(
                (
                    (PeripheralMapping.farm_id == farm_id) |
                    (PeripheralMapping.section_id.in_(section_ids) if section_ids else False)
                ),
                PeripheralMapping.peripheral_type_id.in_(exclusive_type_ids)
            ).all()
            print(f"[DEBUG] ALL mappings in farm (regardless of is_deleted): {[{'id': m.id, 'type_id': m.peripheral_type_id, 'section_id': m.section_id, 'farm_id': m.farm_id, 'is_deleted': m.is_deleted} for m in all_mappings]}")
            all_scheds = []
            for m in all_mappings:
                scheds = db.query(Schedule).filter(Schedule.peripheral_mapping_id == m.id).all()
                print(f"[DEBUG] ALL schedules for mapping {m.id} (regardless of is_deleted): {[{'id': s.id, 'cron': s.cron_expression, 'duration': s.duration_minutes, 'is_deleted': s.is_deleted} for s in scheds]}")
                all_scheds.extend(scheds)
            print(f"[DEBUG] ALL schedules in farm (regardless of is_deleted): {len(all_scheds)}")
            # Now filter to only active mappings
            relevant_mappings = db.query(PeripheralMapping).filter(
                (
                    (PeripheralMapping.farm_id == farm_id) |
                    (PeripheralMapping.section_id.in_(section_ids) if section_ids else False)
                ),
                PeripheralMapping.is_deleted == False,
                PeripheralMapping.peripheral_type_id.in_(exclusive_type_ids)
            ).all()
            print(f"[DEBUG] relevant_mappings: {[{'id': m.id, 'type_id': m.peripheral_type_id, 'section_id': m.section_id, 'farm_id': m.farm_id} for m in relevant_mappings]}")
        else:
            relevant_mappings = []
        # Gather all active schedules for these mappings
        all_schedules = []
        for m in relevant_mappings:
            schedules = db.query(Schedule).filter(
                Schedule.peripheral_mapping_id == m.id,
                Schedule.is_deleted == False
            ).all()
            print(f"[DEBUG] Schedules for mapping {m.id}: {[{'id': s.id, 'cron': s.cron_expression, 'duration': s.duration_minutes} for s in schedules]}")
            all_schedules.extend(schedules)
        print(f"[DEBUG] all_schedules count: {len(all_schedules)}")
        # For each, expand cron and check for overlap
        new_occurrences = get_next_occurrences(schedule_in.cron_expression, datetime.now(), n=7)
        print(f"[DEBUG] new_occurrences: {new_occurrences}")
        for sched in all_schedules:
            existing_occurrences = get_next_occurrences(sched.cron_expression, datetime.now(), n=7)
            sched_duration = getattr(sched, 'duration_minutes', None)
            if sched_duration is None:
                continue
            for new_start in new_occurrences:
                new_end = new_start + timedelta(minutes=schedule_in.duration_minutes)
                for exist_start in existing_occurrences:
                    exist_end = exist_start + timedelta(minutes=sched_duration)
                    if windows_overlap(new_start, new_end, exist_start, exist_end):
                        print(f"[DEBUG] Overlap detected: new [{new_start}, {new_end}] vs exist [{exist_start}, {exist_end}] (sched_id={sched.id})")
                        raise HTTPException(status_code=400, detail="Overlapping schedule not allowed for any exclusive peripheral in this farm.")
    schedule = Schedule(peripheral_mapping_id=mapping_id, cron_expression=schedule_in.cron_expression, duration_minutes=schedule_in.duration_minutes)
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.put("/{schedule_id}", response_model=ScheduleOut)
def update_schedule(schedule_id: int, schedule_in: ScheduleUpdate, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.is_deleted == False).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    mapping = db.query(PeripheralMapping).filter(PeripheralMapping.id == schedule.peripheral_mapping_id).first() if schedule else None
    ptype = db.query(PeripheralType).filter(PeripheralType.id == mapping.peripheral_type_id).first() if mapping else None
    # Robust exclusivity: check for overlap with all exclusive schedules in the same section/farm
    if ptype is not None and bool(getattr(ptype, 'exclusive_schedule', False)):
        print(f"[DEBUG] (UPDATE) Checking exclusivity for schedule_id={schedule_id}, ptype={ptype.name}, exclusive_schedule={ptype.exclusive_schedule}")
        cron_expr = schedule_in.cron_expression if schedule_in.cron_expression is not None else schedule.cron_expression
        duration = schedule_in.duration_minutes if schedule_in.duration_minutes is not None else getattr(schedule, 'duration_minutes', None)
        farm_id = mapping.farm_id if mapping is not None and getattr(mapping, 'farm_id', None) is not None else None
        if farm_id is None and mapping is not None and getattr(mapping, 'section_id', None) is not None:
            from app.models.section import Section
            section = db.query(Section).filter(Section.id == mapping.section_id).first()
            if section:
                farm_id = section.farm_id
        print(f"[DEBUG] (UPDATE) farm_id for exclusivity: {farm_id}")
        if farm_id is not None:
            exclusive_type_ids = [pt.id for pt in db.query(PeripheralType).filter(PeripheralType.exclusive_schedule == True).all()]
            print(f"[DEBUG] (UPDATE) exclusive_type_ids: {exclusive_type_ids}")
            from app.models.section import Section
            section_ids = [s.id for s in db.query(Section).filter(Section.farm_id == farm_id).all()]
            print(f"[DEBUG] (UPDATE) section_ids in farm: {section_ids}")
            all_mappings = db.query(PeripheralMapping).filter(
                (
                    (PeripheralMapping.farm_id == farm_id) |
                    (PeripheralMapping.section_id.in_(section_ids) if section_ids else False)
                ),
                PeripheralMapping.peripheral_type_id.in_(exclusive_type_ids)
            ).all()
            print(f"[DEBUG] (UPDATE) ALL mappings in farm (regardless of is_deleted): {[{'id': m.id, 'type_id': m.peripheral_type_id, 'section_id': m.section_id, 'farm_id': m.farm_id, 'is_deleted': m.is_deleted} for m in all_mappings]}")
            all_scheds = []
            for m in all_mappings:
                scheds = db.query(Schedule).filter(Schedule.peripheral_mapping_id == m.id).all()
                print(f"[DEBUG] (UPDATE) ALL schedules for mapping {m.id} (regardless of is_deleted): {[{'id': s.id, 'cron': s.cron_expression, 'duration': s.duration_minutes, 'is_deleted': s.is_deleted} for s in scheds]}")
                all_scheds.extend(scheds)
            print(f"[DEBUG] (UPDATE) ALL schedules in farm (regardless of is_deleted): {len(all_scheds)}")
            relevant_mappings = db.query(PeripheralMapping).filter(
                (
                    (PeripheralMapping.farm_id == farm_id) |
                    (PeripheralMapping.section_id.in_(section_ids) if section_ids else False)
                ),
                PeripheralMapping.is_deleted == False,
                PeripheralMapping.peripheral_type_id.in_(exclusive_type_ids)
            ).all()
            print(f"[DEBUG] (UPDATE) relevant_mappings: {[{'id': m.id, 'type_id': m.peripheral_type_id, 'section_id': m.section_id, 'farm_id': m.farm_id} for m in relevant_mappings]}")
        else:
            relevant_mappings = []
        all_schedules = []
        for m in relevant_mappings:
            schedules = db.query(Schedule).filter(
                Schedule.peripheral_mapping_id == m.id,
                Schedule.is_deleted == False,
                Schedule.id != schedule_id
            ).all()
            print(f"[DEBUG] (UPDATE) Schedules for mapping {m.id}: {[{'id': s.id, 'cron': s.cron_expression, 'duration': s.duration_minutes} for s in schedules]}")
            all_schedules.extend(schedules)
        print(f"[DEBUG] (UPDATE) all_schedules count: {len(all_schedules)}")
        new_occurrences = get_next_occurrences(cron_expr, datetime.now(), n=7)
        print(f"[DEBUG] (UPDATE) new_occurrences: {new_occurrences}")
        for sched in all_schedules:
            existing_occurrences = get_next_occurrences(sched.cron_expression, datetime.now(), n=7)
            sched_duration = getattr(sched, 'duration_minutes', None)
            if duration is None or sched_duration is None:
                continue
            for new_start in new_occurrences:
                new_end = new_start + timedelta(minutes=duration)
                for exist_start in existing_occurrences:
                    exist_end = exist_start + timedelta(minutes=sched_duration)
                    if windows_overlap(new_start, new_end, exist_start, exist_end):
                        print(f"[DEBUG] (UPDATE) Overlap detected: new [{new_start}, {new_end}] vs exist [{exist_start}, {exist_end}] (sched_id={sched.id})")
                        raise HTTPException(status_code=400, detail="Overlapping schedule not allowed for any exclusive peripheral in this farm.")
    for key, value in schedule_in.dict(exclude_unset=True).items():
        setattr(schedule, key, value)
    db.commit()
    db.refresh(schedule)
    return schedule

@router.delete("/{schedule_id}", response_model=ScheduleOut)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    schedule = db.query(Schedule).filter(Schedule.id == schedule_id, Schedule.is_deleted == False).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    setattr(schedule, 'is_deleted', True)
    db.commit()
    db.refresh(schedule)
    return schedule 