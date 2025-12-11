from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_active_user
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.user import User
from app.models.organization import Organization
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    AuthResponse,
    UserResponse,
    OrganizationResponse
)
import re
from datetime import datetime

router = APIRouter()


def generate_slug(company_name: str) -> str:
    """
    Generate URL-friendly slug from company name

    Args:
        company_name: Company name string

    Returns:
        Slug string (lowercase, alphanumeric with hyphens)
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', company_name.lower())
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user and organization

    Creates:
    1. New organization with auto-generated slug
    2. New user associated with the organization
    3. Unique email address: slug@process.clarityap.com

    Returns JWT token and user/organization info
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Generate slug from company name
    base_slug = generate_slug(request.company_name)
    slug = base_slug
    counter = 1

    # Ensure slug is unique
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Generate organization email
    org_email = f"{slug}@process.clarityap.com"

    # Create organization
    organization = Organization(
        name=request.company_name,
        slug=slug,
        email=org_email,
        country="US",
        currency="USD",
        default_gl_account="6000",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(organization)
    db.flush()  # Get the organization ID

    # Create user
    hashed_password = get_password_hash(request.password)
    user = User(
        email=request.email,
        hashed_password=hashed_password,
        first_name=request.first_name,
        last_name=request.last_name,
        organization_id=organization.id,
        is_active=True,
        is_superuser=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    db.refresh(organization)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Prepare response
    return AuthResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "organization_id": str(user.organization_id),
                "is_active": user.is_active
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "slug": organization.slug,
                "email": organization.email,
                "country": organization.country,
                "currency": organization.currency
            }
        },
        message="Registration successful"
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token

    Validates:
    - Email exists
    - Password is correct
    - User is active

    Returns JWT token and user/organization info
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account"
        )

    # Get organization
    organization = db.query(Organization).filter(Organization.id == user.organization_id).first()

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id)})

    # Prepare response
    return AuthResponse(
        success=True,
        data={
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "organization_id": str(user.organization_id),
                "is_active": user.is_active
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "slug": organization.slug,
                "email": organization.email,
                "country": organization.country,
                "currency": organization.currency
            }
        },
        message="Login successful"
    )


@router.get("/me", response_model=AuthResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user information

    Requires valid JWT token in Authorization header
    Returns user and organization info
    """
    # Get organization
    organization = db.query(Organization).filter(Organization.id == current_user.organization_id).first()

    return AuthResponse(
        success=True,
        data={
            "user": {
                "id": str(current_user.id),
                "email": current_user.email,
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "organization_id": str(current_user.organization_id),
                "is_active": current_user.is_active
            },
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "slug": organization.slug,
                "email": organization.email,
                "country": organization.country,
                "currency": organization.currency
            }
        },
        message="User info retrieved successfully"
    )


@router.post("/logout")
def logout():
    """
    Logout endpoint (client-side token removal)

    For MVP, this is handled client-side by removing the token.
    In production, implement token blacklisting with Redis.
    """
    return {
        "success": True,
        "message": "Logout successful. Remove token from client."
    }
