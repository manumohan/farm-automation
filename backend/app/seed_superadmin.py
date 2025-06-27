from app.db.session import SessionLocal
from app.services.user_service import get_password_hash
from app.models.user import User

def seed_superadmin():
    db = SessionLocal()
    username = "superadmin"
    email = "superadmin@example.com"
    password = "supersecret"
    role = "super_admin"
    status = "active"
    existing = db.query(User).filter(User.username == username).first()
    if not existing:
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role=role,
            status=status
        )
        db.add(user)
        db.commit()
        print(f"Seeded super_admin user: {username} / {password}")
    else:
        print("Superadmin already exists.")
    db.close()

if __name__ == "__main__":
    seed_superadmin() 