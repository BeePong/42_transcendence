import asyncio
import websockets
import ssl
import pathlib


async def ai_bot():
    url = "wss://nginx/ws/pong/1/?is_bot=True"

    # Create an SSL context that does not verify certificates (for testing purposes)
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations(
        "/etc/nginx/ssl/beepong.pem"
    )  # Adjust this path if needed

    async with websockets.connect(url, ssl=ssl_context) as websocket:
        # async with websockets.connect(url, ssl=ssl_context) as websocket:
        await websocket.send("Hello, I'm an AI bot!")
        response = await websocket.recv()
        print(f"Received: {response}")


asyncio.get_event_loop().run_until_complete(ai_bot())
