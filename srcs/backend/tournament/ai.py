import requests
import asyncio
import websockets
import ssl
from bs4 import BeautifulSoup
import json
import random
import os
import time

# Game settings TODO: use them in front-end and back-end
FIELD_WIDTH = 800
FIELD_HEIGHT = 500
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 26
PADDLE_SPEED = 20
BALL_RADIUS = 15
BALL_STARTING_SPEED = 5
BALL_SPEED_INCREMENT = 0
FPS = 30
MAX_SCORE = 500
PADDING_THICKNESS = 7
THICK_BORDER_THICKNESS = 5
UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2


# Step 1: Log in to the website
def login():
    session = requests.Session()

    # Step 1a: Get the CSRF token by visiting the login page
    login_page_url = "https://nginx:8443/page/accounts/login/"
    response = session.get(login_page_url, verify=False)
    if response.status_code != 200:
        print("Failed to load login page.")
        return None

    # Parse the login page to find the CSRF token
    soup = BeautifulSoup(response.text, "html.parser")
    csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"}).get("value")

    # Step 1b: Submit the login form with the CSRF token
    login_url = "https://nginx:8443/page/accounts/login/"
    payload = {
        "username": "dummy",  # Replace with your actual username
        "password": "test123!",  # Replace with your actual password
        "csrfmiddlewaretoken": csrf_token,  # Include the CSRF token
    }

    # Perform the login
    response = session.post(
        login_url, data=payload, headers={"Referer": login_url}, verify=False
    )

    # Check if login was successful
    if response.status_code == 200:
        print("Login successful.")
        return session
    elif response.status_code == 400:
        print("Login failed: User does not exist. Attempting to register...")

        # Step 2: Register the user
        register_url = "https://nginx:8443/page/accounts/register/"
        register_payload = {
            "username": "dummy",  # Same username as above
            "password1": "test123!",  # Same password as above
            "password2": "test123!",  # Password confirmation
            "csrfmiddlewaretoken": csrf_token,  # CSRF token
        }

        # Get the CSRF token for the registration page
        response = session.get(register_url, verify=False)
        if response.status_code != 200:
            print("Failed to load registration page.")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"}).get("value")
        register_payload["csrfmiddlewaretoken"] = csrf_token

        # Submit the registration form
        response = session.post(
            register_url,
            data=register_payload,
            headers={"Referer": register_url},
            verify=False,
        )

        # Check if registration was successful
        if response.status_code == 201:
            print("Registration successful. Logging in...")
            return session  # Attempt to log in again after registration
        else:
            print(f"Registration failed. Status code: {response.status_code}")
            return None
    else:
        print(f"Login failed. Status code: {response.status_code}")
        return None


# Step 2: Use the session to establish a WebSocket connection
async def ai_bot(session):
    # Define the WebSocket URL
    url = "wss://nginx:8443/ws/pong/1/?is_bot=True"

    # Extract the session cookie
    cookies = session.cookies.get_dict()
    cookie_header = "; ".join([f"{name}={value}" for name, value in cookies.items()])
    # print(f"Session cookie: {cookie_header}")

    # SSL context to trust the self-signed certificate
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.load_verify_locations("/etc/nginx/ssl/beepong.pem")

    # Define the headers to include the session cookie
    headers = {
        "Cookie": cookie_header,
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Origin": "https://nginx",
        "Connection": "keep-alive",
    }

    async with websockets.connect(
        url, ssl=ssl_context, extra_headers=headers, ping_interval=30, ping_timeout=60
    ) as websocket:
        print("WebSocket connection established.")

        # Function to send game data, similar to the sendGameData function in JavaScript
        async def send_game_data(websocket, key, key_action):
            message = {
                "message": {
                    "key": key,
                    "keyAction": key_action,
                },
                "type": "game",
            }
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")

        # Example loop to simulate key press and release
        while True:
            try:
                # Receive and print the game state
                async with asyncio.timeout(30):
                    game_state = await websocket.recv()
                    print(f"Received game state at {time.time()}: {game_state}")
                    print(f"Received game state: {game_state}")

                # Extract positions from the game state
                game_state_data = json.loads(game_state)
                ball_position = game_state_data["ball"]
                ai_paddle_position = game_state_data["player2"][
                    "y"
                ]  # Assuming AI is player2

                # Extract ball vector (direction) and speed
                ball_vector = game_state_data["ball_vector"]
                ball_speed = game_state_data["ball_speed"]

                # Predict the ball's future y-position when it reaches the AI paddle
                field_width = FIELD_WIDTH
                time_to_paddle = (field_width - ball_position["x"]) / ball_vector["x"]

                predicted_ball_y = (
                    ball_position["y"] + ball_vector["y"] * time_to_paddle
                )

                # Handle ball bouncing off the top and bottom boundaries
                field_height = FIELD_HEIGHT
                if predicted_ball_y < 0:
                    predicted_ball_y = -predicted_ball_y
                elif predicted_ball_y > field_height:
                    predicted_ball_y = 2 * field_height - predicted_ball_y

                print(f"Predicted ball y-position: {predicted_ball_y}")
                print(f"AI paddle position: {ai_paddle_position}")

                # Move the AI paddle towards the predicted intersection point
                if predicted_ball_y < ai_paddle_position:
                    await send_game_data(websocket, "ArrowUp", "keydown")
                    # Simulate holding the key down for a short duration
                    await asyncio.sleep(random.uniform(0.2, 0.6))
                    await send_game_data(websocket, "ArrowUp", "keyup")
                elif predicted_ball_y > ai_paddle_position:
                    await send_game_data(websocket, "ArrowDown", "keydown")
                    # Simulate holding the key down for a short duration
                    await asyncio.sleep(random.uniform(0.2, 0.6))
                    await send_game_data(websocket, "ArrowDown", "keyup")

                # Add a delay to refresh the AI's view once per second
                print("Waiting for 1 second...")
                await asyncio.sleep(1)

            except websockets.ConnectionClosedError as e:
                print(f"WebSocket connection closed: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


# Main execution
session = login()
if session:
    asyncio.get_event_loop().run_until_complete(ai_bot(session))


# import asyncio
# import aiohttp


# async def ai_bot():
#     login_url = "https://nginx/page/accounts/login/"
#     websocket_url = "wss://nginx/ws/pong/1/?is_bot=True"
#     payload = {"username": "your_username", "password": "your_password"}

#     async with aiohttp.ClientSession(trust_env=True) as session:
#         # Send a POST request to the login endpoint with the user's credentials
#         async with session.post(login_url, data=payload) as response:
#             if response.status == 200:
#                 print("Login successful")
#             else:
#                 print("Login failed")
#                 return

#         # Connect to the WebSocket server
#         async with session.ws_connect(websocket_url) as ws:
#             await ws.send_str("Hello, I'm an AI bot!")


# asyncio.get_event_loop().run_until_complete(ai_bot())
