from typing import Generator

from sqlmodel import create_engine, SQLModel, Session, text, SQLModel, MetaData
from sqlalchemy.orm import registry

FLOORS_DATABASE_URL = "sqlite:///./fost.gestion_studio.floors.db"

floors_engine = create_engine(FLOORS_DATABASE_URL, echo=False)
floors_registry = registry()


class FloorsSQLModel(SQLModel, registry=floors_registry):
    pass


def create_db_and_tables():
    reset_all = False
    test_read = False

    if reset_all:
        FloorsSQLModel.metadata.drop_all(floors_engine)
    FloorsSQLModel.metadata.create_all(floors_engine)
    if floors_engine.url.drivername.lower().startswith("sqlite://"):
        with floors_engine.connect() as connection:
            connection.execute(text("PRAGMA foreign_keys=ON"))  # for SQLite only

    if reset_all:
        from .models import Facility, Floor, Seat, Resource, ResourceCategory, Task

        with Session(floors_engine) as session:
            facilities = []
            for name in ["LBA", "LBB", "LAA"]:
                facility = Facility(name=name)
                session.add(facility)
                session.commit()
                session.refresh(facility)
                facilities.append(facility)

            for facility in facilities:
                for name in ["RdC", "1st", "2nd"]:
                    print("+", facility.name, name)
                    floor = Floor(name=name, facility_id=facility.id)
                    session.add(floor)
                    session.commit()

                    for x in range(10):
                        for y in range(5):
                            seat = Seat(
                                floor_id=floor.id,
                                code=f"{facility.name}_{floor.name}_Seat{x:03}{y:03}",
                                position_x=x,
                                position_y=y,
                            )
                            session.add(seat)
                    session.commit()

            for name in ["Alice", "Bob", "Carol", "Dee"]:
                print("+ User Resource", name)
                resource = Resource(
                    category=ResourceCategory.USER,
                    name=name,
                    properties="",
                    assignations=[],
                )
                session.add(resource)
            session.commit()

            for name in ["Photoshop", "Harmony", "Reemo", "Blender"]:
                print("+ Software Resource", name)
                resource = Resource(
                    category=ResourceCategory.SOFTWARE_LICENSE,
                    name=name,
                    properties="",
                    assignations=[],
                )
                session.add(resource)
            session.commit()

            for name in ['Screen 24"', "Screen BenQ/Eizo", 'Cintiq 22"']:
                print("+ Hardware Resource", name)
                resource = Resource(
                    category=ResourceCategory.SOFTWARE_LICENSE,
                    name=name,
                    properties="",
                    assignations=[],
                )
                session.add(resource)
            session.commit()

    if test_read:
        from .models import Facility, Floor, Seat, Resource, Task
        import uuid

        with Session(floors_engine) as session:
            facility_id = uuid.UUID("4b644ace-5676-4a28-a334-adb17610c635")
            facility = session.get(Facility, facility_id)
            assert facility is not None
            print("    ----->", facility.floors)


def get_session() -> Generator[Session, None, None]:
    with Session(floors_engine) as session:
        yield session
