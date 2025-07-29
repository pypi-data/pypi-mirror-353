import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    TaskBase,
    Task,
    AssignationBase,
    Assignation,
    AssignationStatus,
)

router = APIRouter(
    prefix="/tasks",
    tags=["Floors Tasks"],
)


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(*, session: Session = Depends(get_session), task_in: TaskBase) -> Task:
    # Ensure assignation is valid:
    assignation = session.get(Assignation, task_in.assignation_id)
    if not assignation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignation with id {task_in.assignation_id} not found",
        )

    new = Task.model_validate(task_in)

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


class RelatedAssignation(AssignationBase):
    id: uuid.UUID


class TaskWithRelations(TaskBase):
    id: uuid.UUID
    assignation: RelatedAssignation


@router.get("/", response_model=List[TaskWithRelations])
def read_tasks(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[TaskWithRelations]:
    tasks = session.exec(select(Task).offset(skip).limit(limit)).all()
    return tasks


@router.get("/{task_id}", response_model=TaskWithRelations)
def read_task(
    *, session: Session = Depends(get_session), task_id: uuid.UUID
) -> TaskWithRelations:
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id} not found"
        )
    return task
