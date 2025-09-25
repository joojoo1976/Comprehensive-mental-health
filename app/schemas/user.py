# نماذج المستخدمين (Schemas)

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr

from app.models.user import UserRole

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    role: UserRole = UserRole.USER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[constr(min_length=1, max_length=100)] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserInDBBase(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None
    email_verified: bool = False

    class Config:
        orm_mode = True

# Additional schemas for specific endpoints
class User(UserInDBBase):
    pass

class UserInDB(UserInDBBase):
    hashed_password: str

class UserProfileBase(BaseModel):
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birth_date: Optional[datetime] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    language: Optional[str] = "ar"
    notification_preferences: Optional[str] = None
    privacy_settings: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileInDBBase(UserProfileBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserProfile(UserProfileInDBBase):
    pass

class UserPreferencesBase(BaseModel):
    meditation_reminders: bool = True
    sleep_reminders: bool = True
    activity_reminders: bool = True
    mood_check_ins: bool = True
    preferred_meditation_length: int = 10
    preferred_sleep_reminder_time: str = "22:00"
    preferred_activity_reminder_time: str = "09:00"
    preferred_mood_check_in_time: str = "20:00"
    content_categories: Optional[str] = None  # JSON

class UserPreferencesCreate(UserPreferencesBase):
    pass

class UserPreferencesUpdate(UserPreferencesBase):
    pass

class UserPreferencesInDBBase(UserPreferencesBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UserPreferences(UserPreferencesInDBBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class TokenPayload(BaseModel):
    sub: Optional[int] = None
