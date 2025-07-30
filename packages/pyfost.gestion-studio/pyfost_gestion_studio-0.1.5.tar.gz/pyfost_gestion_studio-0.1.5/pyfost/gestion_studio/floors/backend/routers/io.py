from __future__ import annotations
from typing import Annotated

import traceback
import uuid
import json
import io
import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import File, UploadFile
from fastapi.responses import StreamingResponse

from sqlmodel import Session, select, col
from sqlalchemy.exc import IntegrityError

from ..database import get_session, FloorsSQLModel, floors_engine
from ..models import (
    Facility,
    Floor,
    Seat,
    Resource,
    Assignation,
    Task,
)

router = APIRouter(
    prefix="/io",
    tags=["Floors IO"],
)

MODELS_TO_DUMP = {
    "facilities": Facility,
    "floors": Floor,
    "seats": Seat,
    "resources": Resource,
    "assignations": Assignation,
    "tasks": Task,
}


class DumpEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        elif isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


async def dump_model(session: Session, ModelType):
    all = session.exec(select(ModelType))
    data_dump = [record.model_dump() for record in all]
    return data_dump


async def load_models(ModelType, records):
    items = []
    for record in records:
        print(f"Loading {ModelType.__name__}:", record)
        for k, v in record.items():
            if k == "id" or k.endswith("_id"):
                record[k] = uuid.UUID(v)
            elif k.endswith("_date"):
                record[k] = datetime.date.fromisoformat(v)
        item = ModelType(**record)
        items.append(item)
    return items


@router.post("/dump_json_file/", response_class=StreamingResponse)
async def dump_json_file(*, session: Session = Depends(get_session)):
    data = {}
    for table_name, ModelType in MODELS_TO_DUMP.items():
        data[table_name] = await dump_model(session, ModelType)

    json_data_str = json.dumps(data, indent=2, cls=DumpEncoder)
    json_bytes = io.BytesIO(json_data_str.encode("utf-8"))
    timestamp = datetime.datetime.now().strftime("%Y_%m_%d-%H_%M_%S")
    filename = f"pyfost-floors_db_dump-{timestamp}.json"
    return StreamingResponse(
        content=json_bytes,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/load_json_file/")
async def load_json_file(
    file: Annotated[UploadFile, File(description="JSON Data to load in DB.")],
    *,
    session: Session = Depends(get_session),
):
    content = await file.read()
    try:
        data = json.loads(content)
    except Exception as err:
        print(
            f"Reading {file.filename}: JSON Load error: {err}\nFile content was:\n{content}\n"
        )
        raise

    FloorsSQLModel.metadata.drop_all(floors_engine)
    FloorsSQLModel.metadata.create_all(floors_engine)

    for table_name, ModelType in MODELS_TO_DUMP.items():
        items = await load_models(ModelType, data[table_name])
        session.add_all(items)
    session.commit()

    return {"filename": file.filename}
