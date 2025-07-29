from typing import Generator

from sqlmodel import create_engine, SQLModel, Session, text, SQLModel, MetaData
from sqlalchemy.orm import registry

PYFOST_PROJECTS_DATABASE_URL = "sqlite:///./fost.gestion_studio.projects.db"
# For PostgreSQL (example, ensure you have python-dotenv and a .env file or set env var)
# from dotenv import load_dotenv
# import os
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@host:port/dbname")

# echo=True is good for development to see SQL queries
projects_engine = create_engine(PYFOST_PROJECTS_DATABASE_URL, echo=False)
projects_registry = registry()


class FloorsSQLModel(SQLModel, registry=projects_registry):
    pass


def create_db_and_tables():
    # FloorsSQLModel.metadata.drop_all(projects_engine)
    FloorsSQLModel.metadata.create_all(projects_engine)
    if projects_engine.url.drivername.lower().startswith("sqlite://"):
        with projects_engine.connect() as connection:
            connection.execute(text("PRAGMA foreign_keys=ON"))  # for SQLite only

    from .models import Project, User, Task, ProjectUsers
    import uuid
    from sqlmodel import select

    if 0:

        with Session(projects_engine) as session:
            proj = Project(code="P01", title="Project 01")
            session.add(proj)
            session.commit()
            session.refresh(proj)

            dee = User(login="dee", email="dee@dee.com")
            session.add(dee)
            session.commit()
            session.refresh(dee)

            new_link = ProjectUsers(project_id=proj.id, user_id=dee.id)
            session.add(new_link)
            session.commit()

            task = Task(
                title="A task...",
                description="Assigned to dee!",
                status="NYS",
                project_id=proj.id,
                assignee_id=dee.id,
            )
            session.add(task)
            session.commit()
            # session.refresh(task)
            # session.refresh(dee)
            # session.refresh(proj)

    if 0:
        with Session(projects_engine) as session:
            # task = session.get(Task, uuid.UUID("6afecf1d-21e0-424e-a803-c6d10d98846a"))
            assignee = session.get(
                User, uuid.UUID("be85ffde-da81-4f98-8842-0b5521371393")
            )  # task.assignee_id)
            # print("----------------------->proj tasks   :", proj.tasks)
            # print("----------------------->dee projects :", dee.projects)
            print(
                "----------------------->assignee tasks    :", assignee.assigned_tasks
            )
            for user in session.exec(select(User).offset(0).limit(100)).all():
                print(">>>", user.login)
                print("    ", user.projects)
                print("    ", user.assigned_tasks)
            # print("----------------------->task project :", task.project)
            # print("----------------------->task assignee:", task.assignee)


def get_session() -> Generator[Session, None, None]:
    with Session(projects_engine) as session:
        yield session
