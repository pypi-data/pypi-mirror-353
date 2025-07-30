import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    AssignationBase,
    Assignation,
    AssignationStatus,
    SeatBase,
    Seat,
    ResourceBase,
    Resource,
    TaskBase,
)

router = APIRouter(
    prefix="/assignations",
    tags=["Floors Assignations"],
)


@router.post("/", response_model=Assignation, status_code=status.HTTP_201_CREATED)
def create_assignation(
    *, session: Session = Depends(get_session), assignation_in: AssignationBase
) -> Assignation:
    # Ensure seat and resources are valid:
    seat = session.get(Seat, assignation_in.seat_id)
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Seat with id {assignation_in.seat_id} not found",
        )
    resource = session.get(Resource, assignation_in.resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource with id {assignation_in.seat_id} not found",
        )

    new = Assignation.model_validate(assignation_in)

    try:
        session.add(new)
        session.commit()
        session.refresh(new)
        return new
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


class RelatedSeat(SeatBase):
    id: uuid.UUID


class RelatedResource(ResourceBase):
    id: uuid.UUID


class RelatedTask(TaskBase):
    id: uuid.UUID


class AssignationWithRelations(AssignationBase):
    id: uuid.UUID
    seat: RelatedSeat | None
    resource: RelatedResource | None
    tasks: List[RelatedTask]


@router.get("/", response_model=List[AssignationWithRelations])
def read_assignations(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[AssignationWithRelations]:
    assignations = session.exec(select(Assignation).offset(skip).limit(limit)).all()
    return assignations


@router.get("/{assignation_id}", response_model=AssignationWithRelations)
def read_assignation(
    *, session: Session = Depends(get_session), assignation_id: uuid.UUID
) -> AssignationWithRelations:
    assignation = session.get(Assignation, assignation_id)
    if not assignation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignation not found"
        )
    return assignation


@router.patch("/{assignation_id}", response_model=Assignation)
def update_assignation(
    *,
    session: Session = Depends(get_session),
    assignation_id: uuid.UUID,
    assignation_in: AssignationBase,
) -> Assignation:
    assignation = session.get(Assignation, assignation_id)
    if not assignation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignation not found"
        )

    data = assignation_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(assignation, key, value)

    try:
        session.add(assignation)
        session.commit()
        session.refresh(assignation)
        return assignation
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.delete("/{assignation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignation(
    *, session: Session = Depends(get_session), assignation_id: uuid.UUID
):
    assignation = session.get(Resource, assignation_id)
    if not assignation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Assignation not found"
        )

    # FIXME: Deal with related stuff ?

    session.delete(assignation)
    session.commit()
