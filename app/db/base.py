import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    '''Base class for all SQLAlchemy models'''
    pass


class TimestampMixin:
    '''for adding created_at and updated_at timestamps to all models'''
    created_at = Column(DateTime(timezone=True), server_default = func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default = func.now(), onupdate=func.now(), nullable=False)


class IDMixin:
    '''for adding UUID primary key to all models'''
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

