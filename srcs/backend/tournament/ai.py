import asyncio
import websockets

async def ai_bot():
    url = "wss://localhost/ws/pong/1/?is_bot=True"
    async with websockets.connect(url) as websocket:
        await websocket.send("Hello, I'm an AI bot!")

asyncio.get_event_loop().run_until_complete(ai_bot())