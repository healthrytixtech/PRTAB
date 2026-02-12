import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..database import get_db
from .. import models
from ..auth import hash_password, verify_password, create_access_token, get_current_user_optional
from ..schemas import UserCreate, Token, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginBody(BaseModel):
    email: str | None = None
    password: str | None = None
    role: str | None = None


@router.post("/signup", response_model=Token)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    is_approved = body.role != models.Role.professional
    user_id = str(uuid.uuid4())
    password_hash = hash_password(body.password or str(uuid.uuid4())) if body.password else None
    user = models.UserIdentity(
        id=user_id,
        email=body.email,
        phone=body.phone,
        role=body.role,
        is_anonymous=body.is_anonymous,
        language=body.language or "en",
        password_hash=password_hash,
        is_approved=is_approved,
    )
    db.add(user)
    if body.role == models.Role.user:
        clinical = models.UserClinical(id=str(uuid.uuid4()), user_id=user_id)
        db.add(clinical)
    db.commit()
    db.refresh(user)
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return Token(access_token=token, user_id=user.id, role=user.role)


@router.post("/login", response_model=Token)
def login(body: LoginBody, db: Session = Depends(get_db)):
    if not body.email and not body.password:
        user_id = str(uuid.uuid4())
        user = models.UserIdentity(id=user_id, role=models.Role.user, is_anonymous=True, is_approved=True)
        db.add(user)
        clinical = models.UserClinical(id=str(uuid.uuid4()), user_id=user_id)
        db.add(clinical)
        db.commit()
        db.refresh(user)
        token = create_access_token(data={"sub": user.id, "role": "user"})
        return Token(access_token=token, user_id=user.id, role=models.Role.user)
    user = db.query(models.UserIdentity).filter(models.UserIdentity.email == body.email).first()
    if not user or not user.password_hash or not verify_password(body.password or "", user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if user.role == models.Role.professional and not user.is_approved:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Professional not yet approved")
    token = create_access_token(data={"sub": user.id, "role": user.role.value})
    return Token(access_token=token, user_id=user.id, role=user.role)


@router.get("/me", response_model=UserResponse)
def me(user: models.UserIdentity | None = Depends(get_current_user_optional)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return UserResponse(id=user.id, email=user.email, role=user.role, is_anonymous=user.is_anonymous, is_approved=user.is_approved, language=user.language)
