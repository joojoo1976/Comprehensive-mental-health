# نماذج المحتوى

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base

class ContentType(enum.Enum):
    ARTICLE = "article"
    MEDITATION = "meditation"
    EXERCISE = "exercise"
    PROGRAM = "program"
    VIDEO = "video"
    AUDIO = "audio"
    BOOK = "book"

class ContentCategory(Base):
    __tablename__ = "content_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    articles = relationship("Article", back_populates="category")
    meditations = relationship("Meditation", back_populates="category")
    exercises = relationship("Exercise", back_populates="category")
    programs = relationship("Program", back_populates="category")

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    author = Column(String, nullable=True)
    read_time = Column(Integer, nullable=True)  # بالدقائق
    featured_image_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    category = relationship("ContentCategory", back_populates="articles")
    bookmarks = relationship("ArticleBookmark", back_populates="article")

class Meditation(Base):
    __tablename__ = "meditations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    audio_url = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    duration = Column(Integer, nullable=False)  # بالدقائق
    guide = Column(String, nullable=True)
    background_music_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    category = relationship("ContentCategory", back_populates="meditations")
    completions = relationship("MeditationCompletion", back_populates="meditation")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    duration = Column(Integer, nullable=False)  # بالدقائق
    difficulty_level = Column(Integer, nullable=False)  # 1-5
    video_url = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    category = relationship("ContentCategory", back_populates="exercises")
    completions = relationship("ExerciseCompletion", back_populates="exercise")

class Program(Base):
    __tablename__ = "programs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("content_categories.id"), nullable=True)
    duration = Column(Integer, nullable=False)  # بالأيام
    difficulty_level = Column(Integer, nullable=False)  # 1-5
    image_url = Column(String, nullable=True)
    published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    category = relationship("ContentCategory", back_populates="programs")
    enrollments = relationship("ProgramEnrollment", back_populates="program")
    modules = relationship("ProgramModule", back_populates="program")

class ProgramModule(Base):
    __tablename__ = "program_modules"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)
    content = Column(Text, nullable=True)
    duration = Column(Integer, nullable=True)  # بالدقائق
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    program = relationship("Program", back_populates="modules")
    completions = relationship("ModuleCompletion", back_populates="module")

class SupportGroup(Base):
    __tablename__ = "support_groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    topic = Column(String, nullable=False)
    max_members = Column(Integer, nullable=True)
    is_private = Column(Boolean, default=False)
    moderator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # العلاقات
    moderator = relationship("User")
    memberships = relationship("GroupMembership", back_populates="group")
    posts = relationship("GroupPost", back_populates="group")

class GroupMembership(Base):
    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("support_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    is_admin = Column(Boolean, default=False)

    # العلاقات
    group = relationship("SupportGroup", back_populates="memberships")
    user = relationship("User", back_populates="group_memberships")

class GroupPost(Base):
    __tablename__ = "group_posts"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("support_groups.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    group = relationship("SupportGroup", back_populates="posts")
    user = relationship("User")
    comments = relationship("GroupComment", back_populates="post")

class GroupComment(Base):
    __tablename__ = "group_comments"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("group_posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    post = relationship("GroupPost", back_populates="comments")
    user = relationship("User")

class ArticleBookmark(Base):
    __tablename__ = "article_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # العلاقات
    user = relationship("User", back_populates="bookmarks")
    article = relationship("Article", back_populates="bookmarks")

class MeditationCompletion(Base):
    __tablename__ = "meditation_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    meditation_id = Column(Integer, ForeignKey("meditations.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    rating = Column(Integer, nullable=True)  # 1-5

    # العلاقات
    user = relationship("User")
    meditation = relationship("Meditation", back_populates="completions")

class ExerciseCompletion(Base):
    __tablename__ = "exercise_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    # العلاقات
    user = relationship("User")
    exercise = relationship("Exercise", back_populates="completions")

class ProgramEnrollment(Base):
    __tablename__ = "program_enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    progress = Column(Integer, default=0)  # بالمئوية

    # العلاقات
    user = relationship("User", back_populates="program_enrollments")
    program = relationship("Program", back_populates="enrollments")

class ModuleCompletion(Base):
    __tablename__ = "module_completions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_id = Column(Integer, ForeignKey("program_modules.id"), nullable=False)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)

    # العلاقات
    user = relationship("User")
    module = relationship("ProgramModule", back_populates="completions")
