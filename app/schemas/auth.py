from pydantic import BaseModel
from typing import List, Optional

# --- Permission Schemas ---

class PermissionBase(BaseModel):
    name: str = Field(..., example="users:create")
    description: Optional[str] = None

class PermissionCreate(PermissionBase):
    pass

class Permission(PermissionBase):
    id: int

    class Config:
        orm_mode = True

# --- Role Schemas ---

class RoleBase(BaseModel):
    name: str = Field(..., example="admin")
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(RoleBase):
    pass

# This schema will be used for reading a role, including its permissions
class Role(RoleBase):
    id: int
    permissions: List[Permission] = []

    class Config:
        orm_mode = True

# --- Audit Log Schemas ---

class AuditLogEntry(BaseModel):
    timestamp: str
    user_email: str
    user_id: str
    role: str
    ip_address: str
    method: str
    path: str
    missing_permissions: str