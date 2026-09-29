from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import User
from app.models.schemas import RegisterRequest, LoginRequest
from app.services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

bearer = HTTPBearer(auto_error=False)

# Simple session storage
active_sessions = {}


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db),
):
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_token(credentials.credentials)

    user = db.query(User).filter(User.id == int(payload["sub"])).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# ---------------- REGISTER ----------------

@router.post("/register")
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    if db.query(User).filter(
        (User.username == payload.username) |
        (User.email == payload.email)
    ).first():
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username)

    return {
        "message": "Account created",
        "token": token,
        "username": user.username,
    }


# ---------------- LOGIN ----------------

@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.username == payload.username
    ).first()

    if not user or not verify_password(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    token = create_access_token(user.id, user.username)

    active_sessions[user.username] = {
        "username": user.username,
        "login_time": datetime.now(timezone.utc).isoformat(),
        "last_activity": datetime.now(timezone.utc).isoformat(),
        "user_data": {},
        "token": token,
    }

    return {
        "message": "Login successful",
        "token": token,
        "username": user.username,
    }


# ---------------- LOGOUT ----------------

@router.post("/logout")
def logout():
    return {
        "message": "Logout successful"
    }


# ---------------- TOKEN ----------------

@router.post("/token")
def token(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.username == payload.username
    ).first()

    if not user or not verify_password(
        payload.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(
        user.id,
        user.username
    )

    active_sessions[user.username] = {
        "username": user.username,
        "login_time": datetime.now(timezone.utc).isoformat(),
        "last_activity": datetime.now(timezone.utc).isoformat(),
        "user_data": {},
        "token": access_token,
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ---------------- SESSION INFO ----------------

@router.get("/session-info")
def session_info(
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    if username not in active_sessions:
        active_sessions[username] = {
            "username": username,
            "login_time": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "user_data": {},
        }

    session = active_sessions[username]
    session["last_activity"] = datetime.now(timezone.utc).isoformat()

    return {
        "username": session["username"],
        "login_time": session["login_time"],
        "last_activity": session["last_activity"],
        "session_active": True,
        "user_data": session["user_data"],
    }


# ---------------- SESSION DATA ----------------

@router.post("/session-data")
def session_data(
    data: dict,
    current_user: User = Depends(get_current_user),
):
    username = current_user.username

    if username not in active_sessions:
        active_sessions[username] = {
            "username": username,
            "login_time": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "user_data": {},
        }

    active_sessions[username]["user_data"].update(data)
    active_sessions[username]["last_activity"] = datetime.now(timezone.utc).isoformat()

    return {
        "message": "Session data updated",
        "data": active_sessions[username]["user_data"],
    }
# ---------------- CHANGE USERNAME ----------------

@router.put("/change-username")
def change_username(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_username = data.get("username", "").strip()

    if not new_username:
        raise HTTPException(
            status_code=400,
            detail="Username cannot be empty",
        )

    existing_user = db.query(User).filter(
        User.username == new_username,
        User.id != current_user.id,
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Username already exists",
        )

    old_username = current_user.username

    current_user.username = new_username
    db.commit()
    db.refresh(current_user)

    if old_username in active_sessions:
        active_sessions[new_username] = active_sessions.pop(old_username)
        active_sessions[new_username]["username"] = new_username

    return {
        "message": "Username changed successfully",
        "username": new_username,
    }