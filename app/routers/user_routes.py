from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.schemas import UserRead, UserRead


router = APIRouter()

# this will be used for user profile, dashboard, and settings
@router.get("/me", response_model=UserRead)
async def get_me(current_user = Depends(get_current_user)):  # registered user only
    """
    Return the current user's info using a valid JWT token.
    """
    return UserRead(**dict(current_user))