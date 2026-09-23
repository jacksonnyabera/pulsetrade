from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.deriv_ticks import stream_ticks

router = APIRouter(prefix="/market", tags=["market"])


@router.websocket("/ticks/{symbol}")
async def ticks_ws(websocket: WebSocket, symbol: str):
    await websocket.accept()

    async def send_tick(tick_data: dict):
        await websocket.send_json(tick_data)

    try:
        await stream_ticks(symbol, send_tick)
    except WebSocketDisconnect:
        pass