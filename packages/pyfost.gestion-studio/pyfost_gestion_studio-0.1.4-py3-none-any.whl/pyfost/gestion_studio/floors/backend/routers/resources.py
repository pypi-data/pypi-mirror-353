import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    ResourceBase,
    Resource,
    AssignationBase,
    Assignation,
)


router = APIRouter(
    prefix="/resources",
    tags=["Floors Resources"],
)


@router.post("/", response_model=Resource, status_code=status.HTTP_201_CREATED)
def create_resource(
    *, session: Session = Depends(get_session), resource_in: ResourceBase
) -> Resource:
    new_resource = Resource.model_validate(resource_in)
    try:
        session.add(new_resource)
        session.commit()
        session.refresh(new_resource)
        return new_resource
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


class RelatedAssignation(AssignationBase):
    id: uuid.UUID
    seat_id: uuid.UUID


class ResourceWithAssignations(ResourceBase):
    id: uuid.UUID
    assignations: List[RelatedAssignation]


@router.get("/", response_model=List[ResourceWithAssignations])
def read_resources(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[ResourceWithAssignations]:
    resources = session.exec(select(Resource).offset(skip).limit(limit)).all()
    return resources


@router.get("/{resource_id}", response_model=Resource)
def read_resource(*, session: Session = Depends(get_session), resource_id: uuid.UUID):
    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )
    return resource


@router.patch("/{resource_id}", response_model=Resource)
def update_resource(
    *,
    session: Session = Depends(get_session),
    resource_id: uuid.UUID,
    resource_in: ResourceBase,
) -> Resource:
    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    data = resource_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(resource, key, value)

    try:
        session.add(resource)
        session.commit()
        session.refresh(resource)
        return resource
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(*, session: Session = Depends(get_session), resource_id: uuid.UUID):
    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found"
        )

    # FIXME: Deal with related stuff (assignment, etc...)

    session.delete(resource)
    session.commit()
