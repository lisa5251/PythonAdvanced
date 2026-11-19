
from getpass import getpass

from app.database import SessionLocal
from app.models.user import User
from app.routes.auth import pwd_context


db = SessionLocal()

try:
    email = input("Admin email: ").strip().lower()
    name = input("Admin name: ").strip()
    password = getpass("Admin password: ")

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")

    existing = db.query(User).filter(
        User.email == email
    ).first()

    if existing:
        existing.role = "admin"
        print("Existing account promoted to admin.")
    else:
        admin = User(
            name=name,
            email=email,
            password_hash=pwd_context.hash(password),
            role="admin"
        )
        db.add(admin)
        print("Admin account created.")

    db.commit()

except Exception as error:
    db.rollback()
    print("Error:", error)

finally:
    db.close()
