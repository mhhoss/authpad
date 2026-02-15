from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserOut(BaseModel):
    id: UUID
    email: str
    is_verified: bool
    created_at: datetime | None = None

    model_config = {
        "from_attributes": True
    }