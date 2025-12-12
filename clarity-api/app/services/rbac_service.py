"""
Role-Based Access Control (RBAC) Service

Implements enterprise-grade permission system for SOC 2 compliance.
"""

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, JSONB, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import BaseModel
from app.models.user import User
from app.services.audit_service import log_audit_event
from typing import List, Optional, Dict
from fastapi import HTTPException, status
import uuid
import logging

logger = logging.getLogger(__name__)


class Role(BaseModel):
    """Role model for RBAC"""
    __tablename__ = 'roles'

    organization_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(String(500))

    # Permissions as JSONB for flexibility
    permissions = Column(JSONB, default=dict)

    # Built-in vs custom roles
    is_system_role = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)


# Default system roles and permissions
SYSTEM_ROLES = {
    'admin': {
        'name': 'Administrator',
        'description': 'Full system access including user management and settings',
        'permissions': {
            # Invoice permissions
            'invoices.view': True,
            'invoices.create': True,
            'invoices.edit': True,
            'invoices.delete': True,
            'invoices.approve': True,
            'invoices.reject': True,
            'invoices.export': True,

            # Vendor permissions
            'vendors.view': True,
            'vendors.create': True,
            'vendors.edit': True,
            'vendors.delete': True,

            # User permissions
            'users.view': True,
            'users.create': True,
            'users.edit': True,
            'users.delete': True,
            'users.manage_roles': True,

            # Settings permissions
            'settings.view': True,
            'settings.edit': True,
            'settings.manage_workflows': True,
            'settings.manage_integrations': True,

            # Audit & reporting
            'audit.view': True,
            'reports.view': True,
            'reports.export': True,
            'analytics.view': True,
        }
    },
    'approver': {
        'name': 'Approver',
        'description': 'Can review and approve/reject invoices',
        'permissions': {
            'invoices.view': True,
            'invoices.approve': True,
            'invoices.reject': True,
            'invoices.export': True,
            'vendors.view': True,
            'reports.view': True,
        }
    },
    'accountant': {
        'name': 'Accountant',
        'description': 'Can manage invoices and vendors',
        'permissions': {
            'invoices.view': True,
            'invoices.create': True,
            'invoices.edit': True,
            'invoices.export': True,
            'vendors.view': True,
            'vendors.create': True,
            'vendors.edit': True,
            'reports.view': True,
            'reports.export': True,
            'analytics.view': True,
        }
    },
    'viewer': {
        'name': 'Viewer',
        'description': 'Read-only access to invoices and reports',
        'permissions': {
            'invoices.view': True,
            'vendors.view': True,
            'reports.view': True,
        }
    }
}


def initialize_system_roles(db: Session, organization_id: uuid.UUID) -> List[Role]:
    """
    Create default system roles for an organization

    Args:
        db: Database session
        organization_id: Organization UUID

    Returns:
        List of created Role objects
    """
    created_roles = []

    for role_key, role_config in SYSTEM_ROLES.items():
        # Check if role already exists
        existing = db.query(Role).filter(
            Role.organization_id == organization_id,
            Role.name == role_config['name'],
            Role.is_system_role == True
        ).first()

        if not existing:
            role = Role(
                organization_id=organization_id,
                name=role_config['name'],
                description=role_config['description'],
                permissions=role_config['permissions'],
                is_system_role=True,
                is_active=True
            )
            db.add(role)
            created_roles.append(role)
            logger.info(f"Created system role: {role_config['name']}")

    db.commit()
    return created_roles


def check_permission(user: User, permission: str, db: Session) -> bool:
    """
    Check if user has a specific permission

    Args:
        user: User object
        permission: Permission string (e.g., 'invoices.approve')
        db: Database session

    Returns:
        True if user has permission, False otherwise
    """
    # Admin users always have all permissions (bypass RBAC)
    if user.is_superuser:
        return True

    # Get user's role
    if not user.role_id:
        logger.warning(f"User {user.id} has no role assigned")
        return False

    role = db.query(Role).filter(Role.id == user.role_id).first()

    if not role or not role.is_active:
        logger.warning(f"User {user.id} has invalid or inactive role")
        return False

    # Check permission in role
    has_permission = role.permissions.get(permission, False)

    logger.debug(f"Permission check: user={user.email}, permission={permission}, result={has_permission}")

    return has_permission


def require_permission(permission: str):
    """
    Decorator to require specific permission for an endpoint

    Usage:
        @router.post("/invoices/{invoice_id}/approve")
        @require_permission('invoices.approve')
        async def approve_invoice(invoice_id: str, current_user: User = Depends(get_current_user)):
            ...
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs
            current_user = kwargs.get('current_user') or kwargs.get('user')
            db = kwargs.get('db')

            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )

            # Check permission
            if not check_permission(current_user, permission, db):
                # Log failed permission check
                log_audit_event(
                    db=db,
                    event_type='permission_denied',
                    action='access_denied',
                    organization_id=current_user.organization_id,
                    user_id=current_user.id,
                    status='failure',
                    details={'permission': permission}
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission}"
                )

            return await func(*args, **kwargs)

        return wrapper
    return decorator


def assign_role_to_user(
    user_id: uuid.UUID,
    role_id: uuid.UUID,
    admin_user: User,
    db: Session
) -> User:
    """
    Assign role to user (with audit logging)

    Args:
        user_id: User to assign role to
        role_id: Role ID to assign
        admin_user: User performing the action
        db: Database session

    Returns:
        Updated User object
    """
    # Check admin has permission
    if not check_permission(admin_user, 'users.manage_roles', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to manage user roles"
        )

    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Get role
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )

    # Verify role belongs to same organization
    if role.organization_id != user.organization_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role does not belong to user's organization"
        )

    # Store old role for audit
    old_role_id = user.role_id

    # Assign role
    user.role_id = role_id
    db.commit()

    # Log role change
    log_audit_event(
        db=db,
        event_type='role_assigned',
        action='update',
        organization_id=admin_user.organization_id,
        user_id=admin_user.id,
        resource_type='user',
        resource_id=user_id,
        details={
            'target_user': user.email,
            'old_role_id': str(old_role_id) if old_role_id else None,
            'new_role_id': str(role_id),
            'role_name': role.name
        }
    )

    logger.info(f"Assigned role {role.name} to user {user.email} by {admin_user.email}")

    return user


def create_custom_role(
    name: str,
    description: str,
    permissions: Dict[str, bool],
    organization_id: uuid.UUID,
    admin_user: User,
    db: Session
) -> Role:
    """
    Create custom role for organization

    Args:
        name: Role name
        description: Role description
        permissions: Dictionary of permissions
        organization_id: Organization UUID
        admin_user: User creating the role
        db: Database session

    Returns:
        Created Role object
    """
    # Check admin has permission
    if not check_permission(admin_user, 'users.manage_roles', db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create roles"
        )

    # Check if role name already exists for this org
    existing = db.query(Role).filter(
        Role.organization_id == organization_id,
        Role.name == name
    ).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{name}' already exists"
        )

    # Create role
    role = Role(
        organization_id=organization_id,
        name=name,
        description=description,
        permissions=permissions,
        is_system_role=False,
        is_active=True
    )

    db.add(role)
    db.commit()

    # Log role creation
    log_audit_event(
        db=db,
        event_type='role_created',
        action='create',
        organization_id=organization_id,
        user_id=admin_user.id,
        resource_type='role',
        resource_id=role.id,
        details={
            'role_name': name,
            'permissions': list(permissions.keys())
        }
    )

    logger.info(f"Created custom role '{name}' for organization {organization_id}")

    return role


def get_user_permissions(user: User, db: Session) -> Dict[str, bool]:
    """
    Get all permissions for a user

    Args:
        user: User object
        db: Database session

    Returns:
        Dictionary of permissions
    """
    # Superusers have all permissions
    if user.is_superuser:
        all_permissions = {}
        for role_config in SYSTEM_ROLES.values():
            all_permissions.update(role_config['permissions'])
        return all_permissions

    # Get user's role
    if not user.role_id:
        return {}

    role = db.query(Role).filter(Role.id == user.role_id).first()

    if not role or not role.is_active:
        return {}

    return role.permissions or {}
