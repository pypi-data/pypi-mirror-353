#!!! YOU CAN USE THIS WITH SQLModels: from __future__ import annotations

import uuid
from typing import List, Optional, TYPE_CHECKING
from enum import Enum
import datetime

from sqlmodel import Field, Relationship
from pydantic import EmailStr, JsonValue

from .database import FloorsSQLModel


class FacilityBase(FloorsSQLModel):
    name: str = Field(unique=True, index=True, nullable=False)


class Facility(FacilityBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )
    floors: List["Floor"] = Relationship(back_populates="facility")


class FloorBase(FloorsSQLModel):
    name: str = Field(nullable=False)
    svg: bytes | None = None
    facility_id: Optional[uuid.UUID] = Field(
        foreign_key="facility.id",
        # index=True,
    )


class Floor(FloorBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )
    facility: Facility = Relationship(back_populates="floors")
    seats: list["Seat"] = Relationship(back_populates="floor")


class SeatBase(FloorsSQLModel):
    code: str = Field(unique=True, nullable=False)
    position_x: int
    position_y: int

    floor_id: Optional[uuid.UUID] = Field(
        # default=None,
        foreign_key="floor.id",
        # index=True,
        # nullable=True
    )


class Seat(SeatBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    floor: Floor = Relationship(back_populates="seats")
    assignations: list["Assignation"] = Relationship(back_populates="seat")


class ResourceCategory(str, Enum):
    USER = "User"
    WORKSTATION = "Workstation"
    SOFTWARE_LICENSE = "SoftwareLicense"
    OTHER = "Other"


class ResourceBase(FloorsSQLModel):
    category: ResourceCategory = Field(nullable=False, index=True)
    name: str
    properties: str  # JsonValue


class Resource(ResourceBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )
    assignations: list["Assignation"] = Relationship(back_populates="resource")


class AssignationStatus(str, Enum):
    PLANNED = "Planned"
    WIP = "In Progress"
    READY = "Ready"


class AssignationBase(FloorsSQLModel):
    start_date: datetime.date
    end_date: datetime.date
    status: AssignationStatus = Field(
        nullable=False,
        default=AssignationStatus.PLANNED,
        index=True,
    )

    seat_id: Optional[uuid.UUID] = Field(
        # default=None,
        foreign_key="seat.id",
        # index=True,
        # nullable=True
    )
    resource_id: Optional[uuid.UUID] = Field(
        # default=None,
        foreign_key="resource.id",
        # index=True,
        # nullable=True
    )


class Assignation(AssignationBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    seat: Seat = Relationship(back_populates="assignations")
    resource: Resource = Relationship(back_populates="assignations")

    tasks: list["Task"] = Relationship(back_populates="assignation")


class TaskType(str, Enum):
    SETUP_WORKSTATION = "Setup Workstation"
    INSTALL_SOFTWARES = "Install Softwares"


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    BLOCKED = "Blocked"


class TaskBase(FloorsSQLModel):
    type: TaskType
    status: TaskStatus = Field(
        nullable=False,
        default=TaskStatus.PENDING,
        index=True,
    )
    notes: str

    assignation_id: Optional[uuid.UUID] = Field(
        # default=None,
        foreign_key="assignation.id",
        # index=True,
        # nullable=True
    )


class Task(TaskBase, table=True):
    id: uuid.UUID | None = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True
    )

    assignation: Assignation = Relationship(back_populates="tasks")
