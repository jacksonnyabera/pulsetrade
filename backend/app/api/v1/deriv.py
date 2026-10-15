import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.integrations.deriv_client import get_options_ws_url, list_options_accounts
from app.models.user import User
from app.schemas.deriv import DerivAccountOut, DerivCallbackRequest, WsUrlResponse
from app.services.deriv_service import (
    connect_deriv_account,
    get_active_account_and_token,
    pick_demo_account,
)

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


@router.get("/accounts/raw")
async def raw_accounts(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # Temporary debug endpoint. Remove once the UI is finished.
    found = await get_active_account_and_token(db, current_user.id)
    if found is None:
        raise HTTPException(status_code=404, detail="No Deriv account connected")
    _, token = found
    try:
        return await list_options_accounts(token)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=409, detail=f"Deriv returned {e.response.status_code}. Try reconnecting.")


@router.post("/ws-url", response_model=WsUrlResponse)
async def ws_url(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    found = await get_active_account_and_token(db, current_user.id)
    if found is None:
        raise HTTPException(status_code=404, detail="No Deriv account connected")
    account, token = found

    try:
        demo = pick_demo_account(await list_options_accounts(token))
        url = await get_options_ws_url(token, demo["account_id"])
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=409, detail=f"Deriv returned {e.response.status_code}. Try reconnecting.")

    # Beta safety rule: demo only
    if "/ws/demo" not in url:
        raise HTTPException(status_code=403, detail="Only demo accounts are enabled during beta")

    # Repair the saved record if it was stored incorrectly earlier
    account.deriv_loginid = demo["account_id"]
    account.account_type = "demo"
    account.currency = demo.get("currency", account.currency)
    await db.commit()

    return WsUrlResponse(url=url)