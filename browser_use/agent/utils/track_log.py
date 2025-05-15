import asyncio
import os
from websockets.legacy.client import connect
import json

pending_websocket_logs: list[asyncio.Task] = []

def track_log_send(coro):
    task = asyncio.create_task(coro)
    pending_websocket_logs.append(task)
    return task

async def send_test_response_via_socket(payload: dict):
        global websocket_connection
        uri = os.getenv("TEST_BOOSTER_WEBSOCKET_URL", "")
        try:
            if websocket_connection is None or websocket_connection.closed:
                websocket_connection = await connect(uri)
            await websocket_connection.send(json.dumps(payload))
        except Exception as e:
            print(f"[WS] Erro ao enviar: {e}")
            websocket_connection = None  # força reconexão

async def send_test_response(request_id: str, response: any):
        await send_test_response_via_socket({
            'requestId': request_id,
            'response': response
        })