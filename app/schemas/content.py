# نماذج المحتوى (Schemas)

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.models.content import ContentType

# Base schemas


class ContentCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None


class ContentCategoryCreate(ContentCategoryBase):
    pass


class ContentCategoryUpdate(ContentCategoryBase):
    pass


class ContentCategoryInDBBase(ContentCategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ContentCategory(ContentCategoryInDBBase):
    pass


class ArticleBase(BaseModel):
    title: str
    content: str
    summary: Optional[str] = None
    category_id: Optional[int] = None
    author: Optional[str] = None
    read_time: Optional[int] = None
    featured_image_url: Optional[str] = None
    published: bool = False


class ArticleCreate(ArticleBase):
    pass


class ArticleUpdate(ArticleBase):
    pass


class ArticleInDBBase(ArticleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Article(ArticleInDBBase):
    pass


class MeditationBase(BaseModel):
    title: str
    description: str
    audio_url: str
    category_id: Optional[int] = None
    duration: int  # بالدقائق
    guide: Optional[str] = None
    background_music_url: Optional[str] = None
    published: bool = False


class MeditationCreate(MeditationBase):
    pass


class MeditationUpdate(MeditationBase):
    pass


class MeditationInDBBase(MeditationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Meditation(MeditationInDBBase):
    pass


class ExerciseBase(BaseModel):
    title: str
    description: str
    instructions: str
    category_id: Optional[int] = None
    duration: int  # بالدقائق
    difficulty_level: int  # 1-5
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    published: bool = False


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(ExerciseBase):
    pass


class ExerciseInDBBase(ExerciseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Exercise(ExerciseInDBBase):
    pass


class ProgramBase(BaseModel):
    title: str
    description: str
    category_id: Optional[int] = None
    duration: int  # بالأيام
    difficulty_level: int  # 1-5
    image_url: Optional[str] = None
    published: bool = False


class ProgramCreate(ProgramBase):
    pass


class ProgramUpdate(ProgramBase):
    pass


class ProgramInDBBase(ProgramBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class Program(ProgramInDBBase):
    pass


class ProgramModuleBase(BaseModel):
    program_id: int
    title: str
    description: Optional[str] = None
    order: int
    content: Optional[str] = None
    duration: Optional[int] = None  # بالدقائق


class ProgramModuleCreate(ProgramModuleBase):
    pass


class ProgramModuleUpdate(ProgramModuleBase):
    pass


class ProgramModuleInDBBase(ProgramModuleBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ProgramModule(ProgramModuleInDBBase):
    pass


class SupportGroupBase(BaseModel):
    name: str
    description: str
    topic: str
    max_members: Optional[int] = None
    is_private: bool = False


class SupportGroupCreate(SupportGroupBase):
    moderator_id: int


class SupportGroupUpdate(SupportGroupBase):
    pass


class SupportGroupInDBBase(SupportGroupBase):
    id: int
    moderator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class SupportGroup(SupportGroupInDBBase):
    pass


class GroupMembershipBase(BaseModel):
    group_id: int
    user_id: int
    is_admin: bool = False


class GroupMembershipCreate(GroupMembershipBase):
    pass


class GroupMembershipInDBBase(GroupMembershipBase):
    id: int
    joined_at: datetime

    class Config:
        orm_mode = True


class GroupMembership(GroupMembershipInDBBase):
    pass


class GroupPostBase(BaseModel):
    group_id: int
    user_id: int
    content: str


class GroupPostCreate(GroupPostBase):
    pass


class GroupPostInDBBase(GroupPostBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GroupPost(GroupPostInDBBase):
    pass


class GroupCommentBase(BaseModel):
    post_id: int
    user_id: int
    content: str


class GroupCommentCreate(GroupCommentBase):
    pass


class GroupCommentInDBBase(GroupCommentBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class GroupComment(GroupCommentInDBBase):
    pass


class ArticleBookmarkBase(BaseModel):
    user_id: int
    article_id: int


class ArticleBookmarkCreate(ArticleBookmarkBase):
    pass


class ArticleBookmarkInDBBase(ArticleBookmarkBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class ArticleBookmark(ArticleBookmarkInDBBase):
    pass


class MeditationCompletionBase(BaseModel):
    user_id: int
    meditation_id: int
    rating: Optional[int] = None  # 1-5


class MeditationCompletionCreate(MeditationCompletionBase):
    pass


class MeditationCompletionInDBBase(MeditationCompletionBase):
    id: int
    completed_at: datetime

    class Config:
        orm_mode = True


class MeditationCompletion(MeditationCompletionInDBBase):
    pass


class ExerciseCompletionBase(BaseModel):
    user_id: int
    exercise_id: int
    notes: Optional[str] = None


class ExerciseCompletionCreate(ExerciseCompletionBase):
    pass


class ExerciseCompletionInDBBase(ExerciseCompletionBase):
    id: int
    completed_at: datetime

    class Config:
        orm_mode = True


class ExerciseCompletion(ExerciseCompletionInDBBase):
    pass


class ProgramEnrollmentBase(BaseModel):
    user_id: int
    program_id: int
    progress: int = 0  # بالمئوية


class ProgramEnrollmentCreate(ProgramEnrollmentBase):
    pass


class ProgramEnrollmentInDBBase(ProgramEnrollmentBase):
    id: int
    enrolled_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ProgramEnrollment(ProgramEnrollmentInDBBase):
    pass


class ModuleCompletionBase(BaseModel):
    user_id: int
    module_id: int
    notes: Optional[str] = None


class ModuleCompletionCreate(ModuleCompletionBase):
    pass


class ModuleCompletionInDBBase(ModuleCompletionBase):
    id: int
    completed_at: datetime

    class Config:
        orm_mode = True


class ModuleCompletion(ModuleCompletionInDBBase):
    pass
