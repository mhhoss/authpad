from fastapi import APIRouter, Depends
from app.auth.dependencies import get_current_user
from app.user.schemas import UserOut


router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_me(current_user = Depends(get_current_user)):
    """
    Return the current user's info using a valid JWT token.
    """
    return UserOut(**dict(current_user))