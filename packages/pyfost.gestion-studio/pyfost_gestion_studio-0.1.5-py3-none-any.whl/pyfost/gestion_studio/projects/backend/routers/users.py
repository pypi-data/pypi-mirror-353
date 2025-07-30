import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    User as DBUser,
    Project as DBProject,
    ProjectUsers as DBProjectUsers,
    Task as DBTask,
)

# Import Pydantic schemas from the new schemas.py
from .schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserReadWithRelations,
    ProjectRead,
)

router = APIRouter(
    prefix="/users",
    tags=["Projects Users"],
)

# --- Pydantic models are now in routers/schemas.py ---


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    *, session: Session = Depends(get_session), user_in: UserCreate
) -> DBUser:
    db_user = DBUser.model_validate(user_in)
    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()
        if "user.login" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Login already exists"
            )
        elif "user.email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}",
            )


@router.get("/", response_model=List[UserReadWithRelations])
def read_users(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> List[UserReadWithRelations]:
    users = session.exec(select(DBUser).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserReadWithRelations)
def read_user(
    *, session: Session = Depends(get_session), user_id: uuid.UUID
) -> UserReadWithRelations:
    db_user = session.get(DBUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return db_user
    # project_links = session.exec(
    #     select(DBProjectUsers).where(DBProjectUsers.user_id == user_id)
    # ).all()

    # project_ids = [link.project_id for link in project_links]
    # user_projects_data = []
    # if project_ids:
    #     user_projects_db = session.exec(
    #         select(DBProject).where(col(DBProject.id).in_(project_ids))
    #     ).all()
    #     user_projects_data = [
    #         ProjectRead.model_validate(p) for p in user_projects_db
    #     ]  # Use ProjectRead from schemas

    # # Construct the response model using UserRead and the fetched projects
    # user_data = UserRead.model_validate(db_user).model_dump()  # Get core user fields

    # # Create UserReadWithProjects instance
    # return UserReadWithProjects(**user_data, projects=user_projects_data)


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    *, session: Session = Depends(get_session), user_id: uuid.UUID, user_in: UserUpdate
) -> DBUser:
    db_user = session.get(DBUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    user_data = user_in.model_dump(exclude_unset=True)  # UserUpdate is SQLModel based
    for key, value in user_data.items():
        setattr(db_user, key, value)

    try:
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
    except IntegrityError as e:
        session.rollback()
        if "user.login" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Login already exists"
            )
        elif "user.email" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database integrity error: {e}",
            )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(*, session: Session = Depends(get_session), user_id: uuid.UUID):
    db_user = session.get(DBUser, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    links_to_delete = session.exec(
        select(DBProjectUsers).where(DBProjectUsers.user_id == user_id)
    ).all()
    for link in links_to_delete:
        session.delete(link)

    tasks_to_update = session.exec(
        select(DBTask).where(DBTask.assignee_id == user_id)
    ).all()
    for task in tasks_to_update:
        task.assignee_id = None
        session.add(task)

    session.delete(db_user)
    session.commit()
    return
