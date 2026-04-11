"""Admin auth router — multi-user RBAC login with role-based access."""
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.database import get_db
from app.models.admin_user import AdminUser, UserRole
from app.auth.jwt import create_access_token, verify_token, security

router = APIRouter(prefix="/api/admin/auth", tags=["Admin Auth"])

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Master admin seeds — these are created on first boot
MASTER_ADMIN_SEEDS = [
    {"email": "xos.owner@gmail.com", "full_name": "XOS Owner", "phone": "+919999000001"},
    {"email": "hello.navos@gmail.com", "full_name": "Navos Admin", "phone": "+919999000002"},
    {"email": "drshansherif@gmail.com", "full_name": "Dr. Shan Sherif", "phone": "+919999000003"},
    {"email": "admin@navos.space", "full_name": "Navos Space Admin", "phone": "+919999000004"},
]

DEFAULT_MASTER_PASSWORD = "UIG@admin2026"  # Changed on first login


# --- Schemas ---

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str

class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    full_name: str

class AdminUserCreate(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole = UserRole.sub_agent
    password: str

class AdminUserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]
    login_count: int
    created_at: datetime
    model_config = {"from_attributes": True}

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


# --- Seed helper ---

def seed_master_admins(db: Session):
    """Create master admin accounts if they don't exist."""
    for seed in MASTER_ADMIN_SEEDS:
        existing = db.query(AdminUser).filter(AdminUser.email == seed["email"]).first()
        if not existing:
            user = AdminUser(
                email=seed["email"],
                full_name=seed["full_name"],
                phone=seed["phone"],
                role=UserRole.master_admin,
                password_hash=_pwd.hash(DEFAULT_MASTER_PASSWORD),
                is_active=True,
            )
            db.add(user)
    db.commit()


# --- Role dependency ---

def get_admin_user(credentials=Depends(security), db: Session = Depends(get_db)) -> AdminUser:
    """Verify JWT and return the AdminUser record."""
    token_data = verify_token(credentials.credentials)
    if token_data is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(AdminUser).filter(AdminUser.email == token_data.sub, AdminUser.is_active == True).first()
    if not user:
        raise HTTPException(status_code=403, detail="Access denied")
    return user


def require_admin(user: AdminUser = Depends(get_admin_user)) -> AdminUser:
    """Require admin or master_admin role."""
    if user.role not in (UserRole.master_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def require_master(user: AdminUser = Depends(get_admin_user)) -> AdminUser:
    """Require master_admin role."""
    if user.role != UserRole.master_admin:
        raise HTTPException(status_code=403, detail="Master admin access required")
    return user


# --- Endpoints ---

@router.post("/login", response_model=AdminTokenResponse)
def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    """Login with email + password. Returns JWT with role."""
    # Auto-seed master admins on first login attempt
    seed_master_admins(db)

    user = db.query(AdminUser).filter(
        AdminUser.email == request.email.lower(),
        AdminUser.is_active == True,
    ).first()

    if not user or not _pwd.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Update login tracking
    user.last_login_at = datetime.now(timezone.utc)
    user.login_count += 1
    db.commit()

    token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=timedelta(hours=24),
    )
    return AdminTokenResponse(
        access_token=token,
        role=user.role.value,
        full_name=user.full_name,
    )


@router.get("/me", response_model=AdminUserResponse)
def get_current_admin(user: AdminUser = Depends(get_admin_user)):
    """Get current logged-in admin's profile."""
    return user


@router.post("/change-password")
def change_password(req: PasswordChangeRequest, user: AdminUser = Depends(get_admin_user), db: Session = Depends(get_db)):
    """Change own password."""
    if not _pwd.verify(req.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    user.password_hash = _pwd.hash(req.new_password)
    db.commit()
    return {"message": "Password changed successfully"}


# --- User management (admin/master only) ---

@router.get("/users", response_model=List[AdminUserResponse])
def list_users(admin: AdminUser = Depends(require_admin), db: Session = Depends(get_db)):
    """List all admin users."""
    return db.query(AdminUser).order_by(AdminUser.role, AdminUser.created_at).all()


@router.post("/users", response_model=AdminUserResponse, status_code=201)
def create_user(user_in: AdminUserCreate, admin: AdminUser = Depends(require_admin), db: Session = Depends(get_db)):
    """Create a new admin user (admin/master only)."""
    existing = db.query(AdminUser).filter(AdminUser.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Only master admins can create other admins
    if user_in.role in (UserRole.master_admin, UserRole.admin) and admin.role != UserRole.master_admin:
        raise HTTPException(status_code=403, detail="Only master admins can create admin accounts")

    user = AdminUser(
        email=user_in.email.lower(),
        full_name=user_in.full_name,
        phone=user_in.phone,
        role=user_in.role,
        password_hash=_pwd.hash(user_in.password),
        created_by=admin.email,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, admin: AdminUser = Depends(require_master), db: Session = Depends(get_db)):
    """Deactivate a user (master only)."""
    target = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    if target.email == admin.email:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
    target.is_active = False
    db.commit()
    return {"message": f"User {target.email} deactivated"}


@router.patch("/users/{user_id}/activate")
def activate_user(user_id: int, admin: AdminUser = Depends(require_master), db: Session = Depends(get_db)):
    """Reactivate a user (master only)."""
    target = db.query(AdminUser).filter(AdminUser.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    target.is_active = True
    db.commit()
    return {"message": f"User {target.email} activated"}
