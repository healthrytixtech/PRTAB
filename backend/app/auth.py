from datetime import datetime
from typing import Optional
import httpx
import jwt as pyjwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import settings
from .database import get_db
from . import models

# ─── Legacy in-house JWT (kept for backward compat) ───────────────────────
from passlib.context import CryptContext
from datetime import timedelta
from jose import JWTError, jwt

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
bearer_scheme = HTTPBearer(auto_error=False)

_clerk_jwks_cache: Optional[dict] = None


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_legacy_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None


# ─── Clerk JWT verification ────────────────────────────────────────────────

def _get_clerk_jwks() -> dict:
    """Fetch Clerk JWKS (public keys) – cached in memory."""
    global _clerk_jwks_cache
    if _clerk_jwks_cache is not None:
        return _clerk_jwks_cache
    if not settings.clerk_jwks_url:
        return {}
    try:
        resp = httpx.get(settings.clerk_jwks_url, timeout=5)
        resp.raise_for_status()
        _clerk_jwks_cache = resp.json()
        return _clerk_jwks_cache
    except Exception:
        return {}


def _verify_clerk_token(token: str) -> Optional[dict]:
    """Verify a Clerk-issued JWT and return the payload, or None on failure."""
    if not settings.clerk_jwks_url:
        return None
    try:
        jwks = _get_clerk_jwks()
        header = pyjwt.get_unverified_header(token)
        kid = header.get("kid")
        # Find matching key
        key = None
        for k in jwks.get("keys", []):
            if k.get("kid") == kid:
                key = pyjwt.algorithms.RSAAlgorithm.from_jwk(k)  # type: ignore[attr-defined]
                break
        if key is None:
            return None
        payload = pyjwt.decode(
            token,
            key,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except Exception:
        return None


def _get_or_create_clerk_user(payload: dict, db: Session) -> models.UserIdentity:
    """Return existing DB user for a Clerk sub, or create one on first login."""
    clerk_id: str = payload.get("sub", "")
    user = db.query(models.UserIdentity).filter(models.UserIdentity.clerk_id == clerk_id).first()
    if user:
        return user
    # First login – provision a local shadow record
    import uuid
    user = models.UserIdentity(
        id=str(uuid.uuid4()),
        clerk_id=clerk_id,
        email=payload.get("email"),
        role=models.Role.user,
        is_anonymous=False,
        is_approved=True,
    )
    db.add(user)
    clinical = models.UserClinical(id=str(uuid.uuid4()), user_id=user.id)
    db.add(clinical)
    db.commit()
    db.refresh(user)
    return user


# ─── FastAPI dependencies ──────────────────────────────────────────────────

def get_current_user_optional(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[models.UserIdentity]:
    """Returns current user from either a Clerk JWT or a legacy in-house JWT."""
    if not creds:
        return None
    token = creds.credentials

    # Try Clerk first
    clerk_payload = _verify_clerk_token(token)
    if clerk_payload:
        return _get_or_create_clerk_user(clerk_payload, db)

    # Fall back to legacy JWT
    payload = decode_legacy_token(token)
    if not payload or "sub" not in payload:
        return None
    return db.query(models.UserIdentity).filter(models.UserIdentity.id == payload["sub"]).first()


def get_current_user(
    user: Optional[models.UserIdentity] = Depends(get_current_user_optional),
) -> models.UserIdentity:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user


def require_role(role: models.Role):
    def _check(current: models.UserIdentity = Depends(get_current_user)) -> models.UserIdentity:
        if current.role != role and current.role != models.Role.admin:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        if role == models.Role.professional and not current.is_approved:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Professional not yet approved")
        return current
    return _check
