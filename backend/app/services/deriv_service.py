import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.encryption import encrypt_token
from app.integrations.deriv_client import exchange_code_for_token, get_deriv_accounts
from app.models.api_token import ApiToken
from app.models.deriv_account import DerivAccount


async def connect_deriv_account(db: AsyncSession, user_id: uuid.UUID, code: str, code_verifier: str) -> DerivAccount:
    token_data = await exchange_code_for_token(code, code_verifier)
    access_token = token_data["access_token"]

    accounts_data = await get_deriv_accounts(access_token)
    # Deriv returns account info; exact shape confirmed once we see a real response —
    # using .get() defensively so this doesn't hard-crash on an unexpected shape.
    account_info = accounts_data.get("accounts", [accounts_data])[0] if isinstance(accounts_data, dict) else accounts_data[0]

    deriv_account = DerivAccount(
        user_id=user_id,
        deriv_loginid=account_info.get("loginid", account_info.get("account_id", "unknown")),
        account_type="demo" if "VRT" in str(account_info.get("loginid", "")) else "real",
        currency=account_info.get("currency", "USD"),
    )
    db.add(deriv_account)
    await db.flush()

    api_token = ApiToken(
        deriv_account_id=deriv_account.id,
        encrypted_token=encrypt_token(access_token),
    )
    db.add(api_token)
    await db.commit()
    await db.refresh(deriv_account)
    return deriv_account