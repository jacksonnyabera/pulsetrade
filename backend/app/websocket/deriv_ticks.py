import asyncio
import json

import websockets

from app.core.config import settings

DERIV_WS_URL = f"wss://ws.derivws.com/websockets/v3?app_id={settings.deriv_client_id}"


async def stream_ticks(symbol: str, on_tick):
    async with websockets.connect(DERIV_WS_URL) as deriv_ws:
        await deriv_ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))
        async for message in deriv_ws:
            data = json.loads(message)
            if data.get("msg_type") == "tick":
                tick = data["tick"]
                await on_tick({"symbol": tick["symbol"], "price": tick["quote"], "epoch": tick["epoch"]})