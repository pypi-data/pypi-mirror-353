#!!! YOU CAN USE THIS WITH SQLModels: from __future__ import annotations

import uuid
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

from sqlmodel import Field, Relationship
from pydantic import EmailStr

from .database import FloorsSQLModel


# --- Link Table: ProjectUsers ---
class ProjectUsers(FloorsSQLModel, table=True):
    __tablename__ = "project_users"

    project_id: uuid.UUID | None = Field(
        default=None, foreign_key="project.id", primary_key=True
    )
    user_id: uuid.UUID | None = Field(
        default=None, foreign_key="user.id", primary_key=True
    )


# --- Task Status Enum ---
class TaskStatus(str, Enum):
    NYS = "NYS"
    WIP = "WIP"
    DONE = "Done"


# --- User Model ---


class UserBase(FloorsSQLModel):
    login: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)


class User(UserBase, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )
    projects: list["Project"] = Relationship(
        back_populates="users", link_model=ProjectUsers
    )
    assigned_tasks: list["Task"] = Relationship(back_populates="assignee")


# --- Project Model ---
class ProjectBase(FloorsSQLModel):
    code: str = Field(unique=True, index=True)
    title: str


class Project(ProjectBase, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    users: list["User"] = Relationship(
        back_populates="projects", link_model=ProjectUsers
    )
    tasks: List["Task"] = Relationship(back_populates="project", cascade_delete=True)


# --- Task Model ---
class TaskBase(FloorsSQLModel):
    title: str
    description: Optional[str] = Field(default=None)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    assignee_id: Optional[uuid.UUID] = Field(
        default=None, foreign_key="user.id", index=True, nullable=True
    )
    status: TaskStatus = Field(default=TaskStatus.NYS)


class Task(TaskBase, table=True):
    id: Optional[uuid.UUID] = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    project: Project = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(back_populates="assigned_tasks")


User.model_rebuild()
Task.model_rebuild()
