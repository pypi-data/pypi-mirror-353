import uuid
from typing import List, Sequence, Annotated

from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import File, UploadFile

from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session
from ..models import (
    FacilityBase,
    Facility,
    FloorBase,
    Floor,
    SeatBase,
    Seat,
)

router = APIRouter(
    tags=["Floors Seats"],
)

#
# ---- Facility
#


@router.post(
    "/facilities/", response_model=Facility, status_code=status.HTTP_201_CREATED
)
def create_facility(
    *, session: Session = Depends(get_session), facility_in: FacilityBase
) -> Facility:
    new_one = Facility.model_validate(facility_in)
    try:
        session.add(new_one)
        session.commit()
        session.refresh(new_one)
        return new_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


class RelatedFloor(BaseModel):
    id: uuid.UUID
    name: str


class FacilityWithFloors(FacilityBase):
    id: uuid.UUID
    floors: List[RelatedFloor] = []


@router.get("/facilities/", response_model=Sequence[FacilityWithFloors])
def read_facilities(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> Sequence[FacilityWithFloors]:
    facilities = session.exec(select(Facility).offset(skip).limit(limit)).all()
    return facilities


@router.get("/facilities/id_from_name/{facility_name}", response_model=uuid.UUID)
def get_facility_id_from_name(
    *, session: Session = Depends(get_session), facility_name: str
) -> uuid.UUID:
    facility_id = session.exec(
        select(Facility.id).where(Facility.name == facility_name)
    ).first()
    if not facility_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Facility with name {facility_name!r} not found",
        )
    return facility_id


@router.get("/facilities/{facility_id}", response_model=FacilityWithFloors)
def read_facility(
    *, session: Session = Depends(get_session), facility_id: uuid.UUID
) -> FacilityWithFloors:
    facility = session.get(Facility, facility_id)
    if not facility:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found"
        )
    return facility


@router.patch("/facilities/{facility_id}", response_model=Facility)
def update_facility(
    *,
    session: Session = Depends(get_session),
    facility_id: uuid.UUID,
    facility_in: FacilityBase,
) -> Facility:
    found_one = session.get(Facility, facility_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found"
        )

    data = facility_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(found_one, key, value)

    try:
        session.add(found_one)
        session.commit()
        session.refresh(found_one)
        return found_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.delete("/facilities/{facility_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_facility(*, session: Session = Depends(get_session), facility_id: uuid.UUID):
    found_one = session.get(Facility, facility_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Facility not found"
        )

    # FIXME: Deal with related stuff (assignment, etc...)

    session.delete(found_one)
    session.commit()


#
# ---- Floor
#


@router.post("/floors/", response_model=Floor, status_code=status.HTTP_201_CREATED)
def create_floor(
    *, session: Session = Depends(get_session), floor_in: FloorBase
) -> Floor:
    new_one = Floor.model_validate(floor_in)
    try:
        session.add(new_one)
        session.commit()
        session.refresh(new_one)
        return new_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


class RelatedSeat(BaseModel):
    id: uuid.UUID
    code: str
    position_x: int
    position_y: int


class FloorWithRelations(FloorBase):
    id: uuid.UUID
    facility: Facility
    seats: list[RelatedSeat] = []


@router.get("/floors/", response_model=Sequence[FloorWithRelations])
def read_floors(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = 100
) -> Sequence[FloorWithRelations]:
    found = session.exec(select(Floor).offset(skip).limit(limit)).all()
    return found


@router.get("/floors/id_from_name/{floor_name}", response_model=uuid.UUID)
def get_facility_id_from_name(
    facility_id: uuid.UUID, *, session: Session = Depends(get_session), floor_name: str
) -> uuid.UUID:
    floor_id = session.exec(
        select(Floor.id).where(
            Floor.facility_id == facility_id, Floor.name == floor_name
        )
    ).first()
    if not floor_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor with name {floor_name!r} not found",
        )
    return floor_id


@router.get("/floors/{floor_id}", response_model=Floor)
def read_floor(*, session: Session = Depends(get_session), floor_id: uuid.UUID):
    found_one = session.get(Floor, floor_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found"
        )
    return found_one


@router.patch("/floors/{floor_id}", response_model=Floor)
def update_floor(
    *,
    session: Session = Depends(get_session),
    floor_id: uuid.UUID,
    floor_in: FacilityBase,
) -> Floor:
    found_one = session.get(Floor, floor_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found"
        )

    data = floor_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(found_one, key, value)

    try:
        session.add(found_one)
        session.commit()
        session.refresh(found_one)
        return found_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.patch("/floors/{floor_id}/svg", response_model=Floor)
async def update_floor_svg(
    *,
    session: Session = Depends(get_session),
    floor_id: uuid.UUID,
    svg: Annotated[UploadFile, File(description="SVG file to use as Floor Map.")],
) -> Floor:
    found_one = session.get(Floor, floor_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor wiht id {floor_id} not found",
        )

    content = await svg.read()
    found_one.svg = content

    try:
        session.add(found_one)
        session.commit()
        session.refresh(found_one)
        return found_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.get("/floors/{floor_id}/svg", response_model=bytes | None)
def read_floor_svg(*, session: Session = Depends(get_session), floor_id: uuid.UUID):
    found_one = session.get(Floor, floor_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Floor with id {floor_id} not found",
        )
    return found_one.svg


@router.delete("/floors/{floor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_floor(*, session: Session = Depends(get_session), floor_id: uuid.UUID):
    found_one = session.get(Floor, floor_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Floor not found"
        )

    # FIXME: Deal with related stuff (assignment, etc...)

    session.delete(found_one)
    session.commit()


#
# ---- Seat
#


@router.post("/seats/", response_model=Seat, status_code=status.HTTP_201_CREATED)
def create_seat(*, session: Session = Depends(get_session), seat_in: SeatBase) -> Seat:
    new_one = Seat.model_validate(seat_in)
    try:
        session.add(new_one)
        session.commit()
        session.refresh(new_one)
        return new_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


class SeatWithRelations(SeatBase):
    id: uuid.UUID
    floor: RelatedFloor


@router.get("/seats/", response_model=List[SeatWithRelations])
def read_seats(
    *, session: Session = Depends(get_session), skip: int = 0, limit: int = -1
) -> List[SeatWithRelations]:
    found = session.exec(select(Seat).offset(skip).limit(limit)).all()
    return found


@router.get("/seats/{seat_id}", response_model=SeatWithRelations)
def read_seat(
    *, session: Session = Depends(get_session), seat_id: uuid.UUID
) -> SeatWithRelations:
    found_one = session.get(Seat, seat_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found"
        )
    return found_one


@router.patch("/seats/{seat_id}", response_model=Seat)
def update_seat(
    *,
    session: Session = Depends(get_session),
    seat_id: uuid.UUID,
    seat_in: FacilityBase,
) -> Seat:
    found_one = session.get(Seat, seat_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found"
        )

    data = seat_in.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(found_one, key, value)

    try:
        session.add(found_one)
        session.commit()
        session.refresh(found_one)
        return found_one
    except IntegrityError as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database integrity error: {e}",
        )


@router.delete("/seats/{seta_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_seat(*, session: Session = Depends(get_session), seat_id: uuid.UUID):
    found_one = session.get(Floor, seat_id)
    if not found_one:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Seat not found"
        )

    # FIXME: Deal with related stuff (assignment, etc...)

    session.delete(found_one)
    session.commit()
