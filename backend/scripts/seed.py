#!/usr/bin/env python3
"""Seed dummy users and professionals. Run from backend: python scripts/seed.py"""
import sys
import os
import uuid

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import UserIdentity, UserClinical, Role
from app.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

def seed():
    if not db.query(UserIdentity).filter(UserIdentity.email == "admin@wellness.local").first():
        db.add(UserIdentity(id=str(uuid.uuid4()), email="admin@wellness.local", role=Role.admin, password_hash=hash_password("admin123"), is_approved=True))
        print("Created admin: admin@wellness.local / admin123")
    if not db.query(UserIdentity).filter(UserIdentity.email == "pro@wellness.local").first():
        db.add(UserIdentity(id=str(uuid.uuid4()), email="pro@wellness.local", role=Role.professional, password_hash=hash_password("pro123"), is_approved=False))
        print("Created professional (pending): pro@wellness.local / pro123")
    if not db.query(UserIdentity).filter(UserIdentity.email == "pro2@wellness.local").first():
        pid = str(uuid.uuid4())
        db.add(UserIdentity(id=pid, email="pro2@wellness.local", role=Role.professional, password_hash=hash_password("pro123"), is_approved=True))
        db.add(UserClinical(id=str(uuid.uuid4()), user_id=pid))
        print("Created professional (approved): pro2@wellness.local / pro123")
    if not db.query(UserIdentity).filter(UserIdentity.email == "user@wellness.local").first():
        uid = str(uuid.uuid4())
        db.add(UserIdentity(id=uid, email="user@wellness.local", role=Role.user, password_hash=hash_password("user123"), is_approved=True))
        db.add(UserClinical(id=str(uuid.uuid4()), user_id=uid))
        print("Created user: user@wellness.local / user123")
    db.commit()
    db.close()
    print("Seed done.")

if __name__ == "__main__":
    seed()
