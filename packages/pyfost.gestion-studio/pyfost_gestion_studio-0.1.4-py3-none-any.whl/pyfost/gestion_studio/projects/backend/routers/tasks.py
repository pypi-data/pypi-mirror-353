import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from ..database import get_session
from ..models import Task as DBTask, User as DBUser, Project as DBProject, TaskStatus

# Import Pydantic schemas
from .schemas import TaskRead, TaskCreate, TaskUpdate, UserRead, ProjectRead

router = APIRouter(
    prefix="/tasks",
    tags=["Projects Tasks"],
)


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    *, session: Session = Depends(get_session), task_in: TaskCreate
) -> TaskRead:
    project_db = session.get(DBProject, task_in.project_id)
    if not project_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {task_in.project_id} not found",
        )

    assignee_db_model: Optional[DBUser] = None
    if task_in.assignee_id:
        assignee_db_model = session.get(DBUser, task_in.assignee_id)
        if not assignee_db_model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Assignee (User) with id {task_in.assignee_id} not found",
            )

    db_task = DBTask.model_validate(task_in)  # Creates DBTask instance from TaskCreate
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    # db_task now has .assignee and .project loaded if relationships are set up (default is lazy load)

    # Construct TaskRead response
    task_data_for_resp = db_task.model_dump()  # Core fields from DBTask

    assignee_resp_model: Optional[UserRead] = None
    if (
        db_task.assignee
    ):  # Accessing .assignee will trigger lazy load if not already loaded
        assignee_resp_model = UserRead.model_validate(db_task.assignee)

    project_resp_model: ProjectRead = ProjectRead.model_validate(db_task.project)

    return TaskRead(
        **task_data_for_resp, assignee=assignee_resp_model, project=project_resp_model
    )


@router.get("/", response_model=List[TaskRead])
def read_tasks(
    *,
    session: Session = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    project_id: Optional[uuid.UUID] = None,
    assignee_id: Optional[uuid.UUID] = None,
    status: Optional[TaskStatus] = None,
) -> List[TaskRead]:
    statement = select(DBTask)
    if project_id:
        statement = statement.where(DBTask.project_id == project_id)
    if assignee_id:
        statement = statement.where(DBTask.assignee_id == assignee_id)
    if status:
        statement = statement.where(DBTask.status == status)

    db_tasks = session.exec(
        statement.offset(skip)
        .limit(limit)
        .options(
            # Eager load related objects if performance is an issue for N+1 queries
            # from sqlalchemy.orm import selectinload
            # selectinload(DBTask.assignee),
            # selectinload(DBTask.project)
        )
    ).all()
    return db_tasks

    # tasks_read_list = []
    # for task in db_tasks:
    #     task_data = task.model_dump()
    #     assignee_data = (
    #         UserRead.model_validate(task.assignee) if task.assignee else None
    #     )
    #     project_data = ProjectRead.model_validate(
    #         task.project
    #     )  # Task always has a project
    #     tasks_read_list.append(
    #         TaskRead(**task_data, assignee=assignee_data, project=project_data)
    #     )

    # return tasks_read_list


@router.get("/{task_id}", response_model=TaskRead)
def read_task(
    *, session: Session = Depends(get_session), task_id: uuid.UUID
) -> TaskRead:
    db_task = session.get(
        DBTask, task_id
    )  # Could add options for eager loading here too
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return db_task
    # task_data = db_task.model_dump()
    # assignee_data = (
    #     UserRead.model_validate(db_task.assignee) if db_task.assignee else None
    # )
    # project_data = ProjectRead.model_validate(db_task.project)

    # return TaskRead(**task_data, assignee=assignee_data, project=project_data)


@router.patch("/{task_id}", response_model=TaskRead)
def update_task(
    *, session: Session = Depends(get_session), task_id: uuid.UUID, task_in: TaskUpdate
) -> TaskRead:
    db_task = session.get(DBTask, task_id)
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task_data_update = task_in.model_dump(exclude_unset=True)  # TaskUpdate is SQLModel

    # Handle assignee_id separately if it's in the update and needs validation or special handling
    if "assignee_id" in task_data_update:
        new_assignee_id = task_data_update["assignee_id"]
        if new_assignee_id is not None:
            assignee_db = session.get(DBUser, new_assignee_id)
            if not assignee_db:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"New assignee (User) with id {new_assignee_id} not found",
                )
            # db_task.assignee_id will be set by setattr below
        # else: assignee_id is None, so unassign. setattr will handle.

    for key, value in task_data_update.items():
        setattr(db_task, key, value)

    session.add(db_task)
    session.commit()
    session.refresh(db_task)

    # Construct response
    task_data_resp = db_task.model_dump()
    assignee_resp = (
        UserRead.model_validate(db_task.assignee) if db_task.assignee else None
    )
    project_resp = ProjectRead.model_validate(db_task.project)

    return TaskRead(**task_data_resp, assignee=assignee_resp, project=project_resp)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(*, session: Session = Depends(get_session), task_id: uuid.UUID):
    task = session.get(DBTask, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    session.delete(task)
    session.commit()
    return
