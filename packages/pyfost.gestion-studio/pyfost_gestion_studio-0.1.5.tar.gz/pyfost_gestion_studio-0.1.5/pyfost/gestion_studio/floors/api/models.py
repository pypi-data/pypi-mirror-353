from __future__ import annotations

# This duplicates all the query and response models from the backend.
# Which sucks.
# But in real world situation, this api client would be generated from
# the backend openapi specs, and all would be duplicated.
# So I guess that's ok.
# (and we should generate this api from the backend openapi!!!)

import enum
import uuid
import datetime

from pydantic import BaseModel, Field, EmailStr, UUID4


class FloorsModel(BaseModel):
    pass


class RelatedFloor(BaseModel):
    id: uuid.UUID
    name: str


class Facility(FloorsModel):
    id: uuid.UUID | None
    name: str
    floors: list[RelatedFloor] = []


class RelatedSeat(BaseModel):
    id: uuid.UUID
    code: str
    position_x: int
    position_y: int


class Floor(FloorsModel):
    id: uuid.UUID | None
    name: str
    svg: str | None
    facility: Facility
    seats: list[RelatedSeat]


class Seat(FloorsModel):
    id: uuid.UUID | None
    code: str
    position_x: int
    position_y: int

    floor: RelatedFloor
    # assignations: list[Assignation]


class ResourceCategory(str, enum.Enum):
    USER = "User"
    WORKSTATION = "Workstation"
    SOFTWARE_LICENSE = "SoftwareLicense"
    OTHER = "Other"


class RelatedAssignation(FloorsModel):
    id: uuid.UUID | None
    start_date: datetime.date
    end_date: datetime.date
    status: AssignationStatus


class Resource(FloorsModel):
    id: uuid.UUID | None
    category: ResourceCategory
    name: str
    properties: str  # JsonValue
    assignations: list[RelatedAssignation]


class AssignationStatus(str, enum.Enum):
    PLANNED = "Planned"
    WIP = "In Progress"
    READY = "Ready"


class RelatedRessource(BaseModel):
    id: uuid.UUID
    category: ResourceCategory
    name: str


class RelatedTask(BaseModel):
    id: uuid.UUID
    type: TaskType
    status: TaskStatus


class Assignation(FloorsModel):
    id: uuid.UUID | None
    start_date: datetime.date
    end_date: datetime.date
    status: AssignationStatus
    seat: RelatedSeat | None
    resource: RelatedRessource | None
    tasks: list[RelatedTask]


class TaskType(str, enum.Enum):
    SETUP_WORKSTATION = "Setup Workstation"
    INSTALL_SOFTWARES = "Install Softwares"


class TaskStatus(str, enum.Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"


class Task(FloorsModel):
    id: uuid.UUID | None
    type: TaskType
    status: TaskStatus
    notes: str
    assignation_id: uuid.UUID | None
    assignation: RelatedAssignation
