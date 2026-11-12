"""
Authentication: register, log in, and single sign-on (SSO) token checks.

How it works
  - Passwords are never stored. They are hashed with bcrypt (passlib) and only the hash is
    kept in users.password_hash, which meets the brief's "encrypt the password" requirement.
  - Logging in returns a signed JWT (JSON Web Token) that lasts ACCESS_TOKEN_EXPIRE_DAYS (7).
    The website keeps it in localStorage and the app keeps it on the phone.
  - SSO: when the website or app opens, it calls GET /auth/sso with the saved token. A valid
    token returns the user straight away, so they skip the login screen on every visit.

Logging: successful and failed sign-ins are logged with the user id or a masked email
(mask_email), never a password or token.

References:
  FastAPI (2024) "OAuth2 with Password (and hashing), Bearer with JWT tokens", FastAPI documentation.
  Available at: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/ (Accessed: 12 November 2026).
  Passlib (2020) "CryptContext Tutorial", Passlib 1.7.4 documentation.
  Available at: https://passlib.readthedocs.io/en/stable/narr/context-tutorial.html (Accessed: 12 November 2026).
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

from database import get_db
from logging_config import get_logger, mask_email
import models
import schemas

load_dotenv()
log = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# Settings come from environment variables (Vercel project settings, or backend/.env locally).
SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))

if SECRET_KEY == "change-this-secret-key-in-production":
    # Fine on a laptop, dangerous online: anyone who knows the default could forge tokens.
    log.warning("SECRET_KEY is not set - using the development default. Set it on the server.")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()


def hash_password(password: str) -> str:
    """Return a salted bcrypt hash of the password (the plain password is never stored)."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check a typed password against the stored bcrypt hash."""
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a signed JWT holding the user id ('sub'), email and role, with an expiry date."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Dependency used by every protected endpoint: reads 'Authorization: Bearer <token>',
    checks the signature and expiry, and loads the user. Any problem -> 401, and the
    website/app sends the user back to the login screen.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        user_id = int(sub) if sub is not None else None
        if user_id is None:
            log.warning("Rejected token with no user id")
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError as e:
        # Usually an expired token (older than 7 days) or one signed with an old SECRET_KEY.
        log.info("Rejected invalid or expired token (%s)", type(e).__name__)
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        log.warning("Valid token for a user that no longer exists user_id=%s", user_id)
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    """Dependency for staff-only endpoints (products, order status): non-admins get 403."""
    if current_user.role != "admin":
        log.warning("Blocked non-admin from an admin action user_id=%s", current_user.id)
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.post("/register", response_model=schemas.Token, status_code=201)
def register(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    """Create a customer account and sign them in straight away (returns a token)."""
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        log.info("Registration refused - email already registered (%s)", mask_email(payload.email))
        raise HTTPException(status_code=400, detail="Email already registered")

    # New sign-ups are always customers; admin accounts are only created by seed.py.
    user = models.User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        role="customer",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    log.info("New customer registered user_id=%s (%s)", user.id, mask_email(user.email))

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """Check email + password and return a token. Same message for wrong email or password."""
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        # One generic message so attackers can't tell which emails have accounts;
        # the log still shows failed attempts so repeated guessing can be spotted.
        log.warning("Failed login (%s)", mask_email(payload.email))
        raise HTTPException(status_code=401, detail="Invalid email or password")

    log.info("Login succeeded user_id=%s role=%s", user.id, user.role)
    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/sso", response_model=schemas.UserOut)
def sso_verify(current_user: models.User = Depends(get_current_user)):
    """
    SSO endpoint — the mobile app and website call this on startup with the stored token.
    If the token is valid, returns the user profile and the session continues.
    If the token is expired/invalid, returns 401 and the app redirects to login.
    """
    log.info("SSO session restored user_id=%s", current_user.id)
    return current_user


@router.get("/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(get_current_user)):
    """Return the signed-in user's profile (used by the app's Settings screen)."""
    return current_user
