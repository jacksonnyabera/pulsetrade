import uuid

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import decrypt_token, encrypt_token
from app.integrations.deriv_client import exchange_code_for_token, list_options_accounts
from app.models.api_token import ApiToken
from app.models.deriv_account import DerivAccount


def pick_demo_account(accounts_response: dict) -> dict:
    for account in accounts_response.get("data") or []:
        if account.get("account_type") == "demo" and account.get("status", "active") == "active":
            return account
    raise ValueError("No active Deriv demo account found")


async def connect_deriv_account(db: AsyncSession, user_id: uuid.UUID, code: str, code_verifier: str) -> DerivAccount:
    token_data = await exchange_code_for_token(code, code_verifier)
    access_token = token_data["access_token"]

    demo = pick_demo_account(await list_options_accounts(access_token))

    # Only the newest connection stays active
    await db.execute(
        update(DerivAccount)
        .where(DerivAccount.user_id == user_id, DerivAccount.is_active.is_(True))
        .values(is_active=False)
    )

    deriv_account = DerivAccount(
        user_id=user_id,
        deriv_loginid=demo["account_id"],
        account_type="demo",
        currency=demo.get("currency", "USD"),
    )
    db.add(deriv_account)
    await db.flush()

    db.add(ApiToken(deriv_account_id=deriv_account.id, encrypted_token=encrypt_token(access_token)))
    await db.commit()
    await db.refresh(deriv_account)
    return deriv_account


async def get_active_account_and_token(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(DerivAccount, ApiToken)
        .join(ApiToken, ApiToken.deriv_account_id == DerivAccount.id)
        .where(DerivAccount.user_id == user_id, DerivAccount.is_active.is_(True))
        .order_by(DerivAccount.connected_at.desc())
        .limit(1)
    )
    row = result.first()
    if row is None:
        return None
    account, token = row
    return account, decrypt_token(token.encrypted_token)