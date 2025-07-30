from __future__ import annotations

# This duplicates all the query and response models from the backend.
# Which sucks.
# But in real world situation, this api client would be generated from
# the backend openapi specs, and all would be duplicated.
# So I guess that's ok.
# (and we should generate this api from the backend openapi!!!)

import enum

from pydantic import BaseModel, Field, EmailStr, UUID4


class UserBase(BaseModel):
    id: UUID4
    email: EmailStr
    login: str


class User(UserBase):
    projects: list[Project]


class Project(BaseModel):
    id: UUID4
    code: str
    title: str


class TaskStatus(str, enum.Enum):
    NYS = "NYS"
    WIP = "WIP"
    Done = "Done"


class Task(BaseModel):
    id: UUID4
    project: Project
    title: str
    description: str | None = None
    status: TaskStatus = Field(default=TaskStatus.NYS)
    assignee_id: str | None = None
    assignee: UserBase | None = None
