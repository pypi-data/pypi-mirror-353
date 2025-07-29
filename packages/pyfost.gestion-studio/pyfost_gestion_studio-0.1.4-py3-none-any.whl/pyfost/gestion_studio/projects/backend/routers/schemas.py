from __future__ import annotations

import uuid
from typing import List, Optional
from pydantic import (
    EmailStr,
    BaseModel,
    Field,
)


from ..models import UserBase, ProjectBase, TaskBase, TaskStatus


# --- User Schemas ---


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: uuid.UUID


class UserUpdate(BaseModel):
    login: Optional[str] = None
    email: Optional[EmailStr] = None


# --- Project Schemas ---


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: uuid.UUID


class ProjectUpdate(BaseModel):
    code: Optional[str] = None
    title: Optional[str] = None


# --- Task Schemas ---


class TaskCreate(TaskBase):
    pass


class TaskReadBase(
    TaskBase
):  # A base for TaskRead to avoid direct recursion if TaskRead needs UserRead etc.
    id: uuid.UUID


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None  # Added description here
    status: Optional[TaskStatus] = None
    assignee_id: Optional[uuid.UUID] = Field(
        default=None,
        nullable=True,
        description="Set to null or omit to unassign/leave as is",
    )


# --- Schemas with Relationships (for responses) ---


class UserReadWithRelations(UserRead):
    projects: List[ProjectRead] = []
    assigned_tasks: List[TaskReadBase] = []


class ProjectReadWithUsers(ProjectRead):
    users: List[UserRead] = []


class TaskRead(TaskReadBase):
    assignee: Optional[UserRead] = None
    project: ProjectRead


class ProjectReadWithDetails(ProjectRead):
    users: List[UserRead] = []
    tasks: List[TaskRead] = []


# Pydantic v2 automatically calls model_rebuild() on modules,
# but if you encounter issues with forward references not resolving,
# you can explicitly update them for each model at the end of the file.
# This is typically not needed for simple string forward refs within the same module.
# For Pydantic v1, you would do:
# UserReadWithProjects.update_forward_refs()
# ProjectReadWithUsers.update_forward_refs()
# TaskRead.update_forward_refs()
# ProjectReadWithDetails.update_forward_refs()

# For Pydantic V2, models are automatically rebuilt.
# If you had models in different files that depended on each other, you might need
# to ensure they are all imported and then call model_rebuild() on them.
# But within a single schemas.py, it should work out of the box.
