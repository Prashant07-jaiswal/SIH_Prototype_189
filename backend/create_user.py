"""
CLI script to create users/investigators in the SQLite database.

Usage:
    python create_user.py <username> <password> [role]

Example:
    python create_user.py admin admin123 admin
    python create_user.py inspector_raj secret456 investigator
"""

import sys
from passlib.context import CryptContext
from database import SessionLocal, User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(username, password, role="investigator"):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == username).first()
        if existing:
            print(f"[!] User '{username}' already exists (ID: {existing.id}, Role: {existing.role})")
            return

        hashed = pwd_context.hash(password)
        new_user = User(
            username=username,
            hashed_password=hashed,
            role=role
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"[+] User created successfully!")
        print(f"    ID:       {new_user.id}")
        print(f"    Username: {new_user.username}")
        print(f"    Role:     {new_user.role}")
    finally:
        db.close()


def list_users():
    db = SessionLocal()
    try:
        users = db.query(User).all()
        if not users:
            print("No users found in database.")
            return
        print(f"\n{'ID':<5} {'Username':<20} {'Role':<15} {'Created At'}")
        print("-" * 60)
        for u in users:
            print(f"{u.id:<5} {u.username:<20} {u.role:<15} {u.created_at}")
        print()
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Existing users in database:")
        list_users()
        print("To create a user: python create_user.py <username> <password> [role]")
    elif len(sys.argv) >= 3:
        user = sys.argv[1]
        pwd = sys.argv[2]
        r = sys.argv[3] if len(sys.argv) > 3 else "investigator"
        create_user(user, pwd, r)
    else:
        print("Usage: python create_user.py <username> <password> [role]")
