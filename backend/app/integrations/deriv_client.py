import httpx

from app.core.config import settings


async def exchange_code_for_token(code: str, code_verifier: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.deriv_token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": settings.deriv_client_id,
                "code": code,
                "code_verifier": code_verifier,
                "redirect_uri": settings.deriv_redirect_uri,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response.raise_for_status()
        return response.json()


async def get_deriv_accounts(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.deriv_api_base}/trading/v1/options/accounts",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()

async def list_options_accounts(access_token: str) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.get(
            f"{settings.deriv_api_base}/trading/v1/options/accounts",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()


async def get_options_ws_url(access_token: str, account_id: str) -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            f"{settings.deriv_api_base}/trading/v1/options/accounts/{account_id}/otp",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()["data"]["url"]