import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    Project as DBProject,
    User as DBUser,
    ProjectUsers as DBProjectUsers,
    Task as DBTask,
)

# Import Pydantic schemas
from .schemas import (
    ProjectRead,
    ProjectCreate,
    ProjectUpdate,
    ProjectReadWithUsers,
    ProjectReadWithDetails,
    UserRead,
)

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(
    *, session: Session = Depends(get_session), project_in: ProjectCreate
) -> DBProject:
    db_project = DBProject.model_validate(project_in)
    try:
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project
    except IntegrityError as e:
        session.rollback()
        if "project.code" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project code already exists",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}",
            )


@router.get("/", response_model=List[ProjectRead])
def read_projects(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[DBProject]:
    projects = session.exec(select(DBProject).offset(skip).limit(limit)).all()
    return projects


@router.get("/{project_id}", response_model=ProjectReadWithDetails)
def read_project(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    db_project = session.get(DBProject, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )
    return db_project

    # # Fetch users
    # user_links = session.exec(
    #     select(DBProjectUsers).where(DBProjectUsers.project_id == project_id)
    # ).all()
    # user_ids = [link.user_id for link in user_links]
    # project_users_data = []
    # if user_ids:
    #     project_users_db = session.exec(
    #         select(DBUser).where(col(DBUser.id).in_(user_ids))
    #     ).all()
    #     project_users_data = [UserRead.model_validate(u) for u in project_users_db]

    # # Fetch tasks
    # project_tasks_db = session.exec(
    #     select(DBTask).where(DBTask.project_id == project_id)
    # ).all()
    # # We need to convert DBTask to schemas.TaskRead
    # project_tasks_data = []
    # for db_task_item in project_tasks_db:
    #     task_item_data = db_task_item.model_dump()
    #     if db_task_item.assignee:
    #         task_item_data["assignee"] = UserRead.model_validate(db_task_item.assignee)
    #     else:
    #         task_item_data["assignee"] = None
    #     # The project part of TaskRead is just ProjectRead, not ProjectReadWithDetails (to avoid recursion)
    #     # The current db_project is the project for these tasks
    #     task_item_data["project"] = ProjectRead.model_validate(
    #         db_project
    #     )  # or fetch project if needed for each task differently
    #     project_tasks_data.append(TaskRead(**task_item_data))

    # project_data = ProjectRead.model_validate(db_project).model_dump()
    # return ProjectReadWithDetails(
    #     **project_data, users=project_users_data, tasks=project_tasks_data
    # )


@router.patch("/{project_id}", response_model=ProjectRead)
def update_project(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    project_in: ProjectUpdate,
) -> DBProject:
    db_project = session.get(DBProject, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    project_data_update = project_in.model_dump(exclude_unset=True)
    for key, value in project_data_update.items():
        setattr(db_project, key, value)

    try:
        session.add(db_project)
        session.commit()
        session.refresh(db_project)
        return db_project
    except IntegrityError as e:
        session.rollback()
        if "project.code" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project code already exists on another project",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}",
            )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(*, session: Session = Depends(get_session), project_id: uuid.UUID):
    db_project = session.get(DBProject, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    # tasks_to_delete = session.exec(
    #     select(DBTask).where(DBTask.project_id == project_id)
    # ).all()
    # for task in tasks_to_delete:
    #     session.delete(task)

    # links_to_delete = session.exec(
    #     select(DBProjectUsers).where(DBProjectUsers.project_id == project_id)
    # ).all()
    # for link in links_to_delete:
    #     session.delete(link)

    session.delete(db_project)
    session.commit()


@router.post(
    "/{project_id}/users/{user_id}",
    # response_model=ProjectReadWithUsers,
    # tags=["Project User Management"],
)
def add_user_to_project(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    user_id: uuid.UUID,
):
    existing_link = session.exec(
        select(DBProjectUsers).where(
            DBProjectUsers.project_id == project_id, DBProjectUsers.user_id == user_id
        )
    ).first()

    if existing_link:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already in project"
        )

    db_project = session.get(DBProject, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    db_user = session.get(DBUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    new_link = DBProjectUsers(project_id=project_id, user_id=user_id)
    session.add(new_link)
    session.commit()


@router.delete(
    "/{project_id}/users/{user_id}",
    response_model=ProjectReadWithUsers,
    # tags=["Project User Management"],
)
def remove_user_from_project(
    *,
    session: Session = Depends(get_session),
    project_id: uuid.UUID,
    user_id: uuid.UUID,
):  # Return type is ProjectReadWithUsers
    db_project = session.get(DBProject, project_id)
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    db_user = session.get(DBUser, user_id)
    if not db_user:  # Check user existence for better error message
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    link_to_delete = session.exec(
        select(DBProjectUsers).where(
            DBProjectUsers.project_id == project_id, DBProjectUsers.user_id == user_id
        )
    ).first()

    if not link_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not associated with this project",
        )

    session.delete(link_to_delete)
    session.commit()

    # Reconstruct ProjectReadWithUsers response
    user_links = session.exec(
        select(DBProjectUsers).where(DBProjectUsers.project_id == project_id)
    ).all()
    current_user_ids = [link.user_id for link in user_links]
    project_users_data = []
    if current_user_ids:
        project_users_db = session.exec(
            select(DBUser).where(col(DBUser.id).in_(current_user_ids))
        ).all()
        project_users_data = [UserRead.model_validate(u) for u in project_users_db]

    project_response_data = ProjectRead.model_validate(db_project).model_dump()
    return ProjectReadWithUsers(**project_response_data, users=project_users_data)
