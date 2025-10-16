from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.schemas.schemas import UserOut


router = APIRouter()

# this will be used for user profile, dashboard, and settings
@router.get("/me", response_model=UserOut)
async def get_me(email: str = Depends(get_current_user)):  # registered user only
    """
    Return the current user's info using a valid JWT token.
    """
    return UserOut(email=email)