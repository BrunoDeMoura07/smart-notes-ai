import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str | None = None
    content: str = Field(min_length=1)


class NoteAccepted(BaseModel):
    id: uuid.UUID
    status: str


class NoteStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: str
    error_message: str | None = None


class NoteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None
    source_type: str
    original_text: str | None
    original_filename: str | None
    summary: str | None
    tags: list[str] | None
    status: str
    error_message: str | None
    processing_started_at: datetime | None
    processing_completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class NoteListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str | None
    source_type: str
    status: str
    created_at: datetime


class NoteList(BaseModel):
    items: list[NoteListItem]
    total: int
    page: int
    page_size: int


class NoteUpdate(BaseModel):
    title: str | None = None
    tags: list[str] | None = None
