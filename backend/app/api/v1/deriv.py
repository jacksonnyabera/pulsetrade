from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.deriv import DerivAccountOut, DerivCallbackRequest
from app.services.deriv_service import connect_deriv_account

router = APIRouter(prefix="/deriv", tags=["deriv"])


@router.post("/callback", response_model=DerivAccountOut, status_code=status.HTTP_201_CREATED)
async def deriv_callback(
    payload: DerivCallbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        account = await connect_deriv_account(db, current_user.id, payload.code, payload.code_verifier)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Deriv connection failed: {str(e)}")
    return DerivAccountOut(
        id=str(account.id),
        deriv_loginid=account.deriv_loginid,
        account_type=account.account_type,
        currency=account.currency,
        is_active=account.is_active,
    )