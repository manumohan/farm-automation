from app.db.session import SessionLocal
from app.models.peripheral import PeripheralType

def seed_peripheral_types():
    db = SessionLocal()
    types = [
        {"name": "Valve", "scope": "section"},
        {"name": "Light", "scope": "section"},
        {"name": "Pump", "scope": "farm"},
        {"name": "Flow Sensor", "scope": "farm"},
        {"name": "Moisture Sensor", "scope": "farm"},
    ]
    for t in types:
        exists = db.query(PeripheralType).filter_by(name=t["name"]).first()
        if not exists:
            db.add(PeripheralType(**t))
    db.commit()
    db.close()

if __name__ == "__main__":
    seed_peripheral_types() 