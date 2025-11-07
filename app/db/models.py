from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import DateTime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

import uuid

from .base import Base, TimestampMixin



class User(TimestampMixin, Base):
    '''Maps to existing `users` table in database'''
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    email_verified_at = Column(DateTime(timezone=True))

    # Relationships to otp_token table
    otp_tokens = relationship(
        "OTPToken",
        back_populates="user", 
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class OTPToken(TimestampMixin, Base):
    '''Maps to existing 'otp_tokens' table'''
    __tablename__ = "otp_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    otp_type = Column(String(20), nullable=False)
    token_hash = Column(String(255), nullable=False, index=True)
    destination = Column(String(255))
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used_at = Column(DateTime(timezone=True))

    user = relationship(
        "User",
        back_populates="otp_tokens"
        )


# Export models
__all__ = ["User", "OTPToken"]