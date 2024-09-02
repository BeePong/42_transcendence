import asyncio
import json
import os
import random
import ssl
import time

# import aiohttp
import requests
import websockets
from bs4 import BeautifulSoup

# Game settings TODO: use them in front-end and back-end
FIELD_WIDTH = 800
FIELD_HEIGHT = 500
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 26
PADDLE_SPEED = 20
BALL_RADIUS = 15
BALL_STARTING_SPEED = 5
BALL_SPEED_INCREMENT = 0
FPS = 15
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


async def calculate_ai_move(game_state_data):
    ball_position = game_state_data["ball"]
    ai_paddle_position = game_state_data["player2"]["y"]  # Assuming AI is player2
    ball_vector = game_state_data["ball_vector"]
    ball_speed = game_state_data["ball_speed"]

    # Predict the ball's future y-position when it reaches the AI paddle
    time_to_paddle = (FIELD_WIDTH - ball_position["x"]) / ball_vector["x"]
    predicted_ball_y = ball_position["y"] + ball_vector["y"] * time_to_paddle

    # Handle ball bouncing off the top and bottom boundaries
    if predicted_ball_y < 0:
        predicted_ball_y = -predicted_ball_y
    elif predicted_ball_y > FIELD_HEIGHT:
        predicted_ball_y = 2 * FIELD_HEIGHT - predicted_ball_y

    print(f"Predicted ball y-position: {predicted_ball_y}")
    print(f"AI paddle position: {ai_paddle_position}")

    # Determine the move direction
    if predicted_ball_y < ai_paddle_position:
        return "ArrowUp"
    elif predicted_ball_y > ai_paddle_position:
        return "ArrowDown"
    else:
        return None  # No movement needed


async def ai_movement_logic(websocket, game_state_event, game_state_data):
    while True:
        await game_state_event.wait()  # Wait for a new game state
        game_state_event.clear()  # Clear the event

        print("AI movement logic triggered")
        print(json.dumps(game_state_data, indent=2))
        # Check if the necessary keys are present in the game state data
        if (
            "ball" in game_state_data
            and "player2" in game_state_data
            and "ball_vector" in game_state_data
        ):
            print("Calculating AI move")
            # Calculate AI move
            move = await calculate_ai_move(game_state_data)
            print(f"AI move: {move}")

            # Execute the move
            if move:
                await send_game_data(websocket, move, "keydown")
                await asyncio.sleep(random.uniform(0.2, 0.6))
                await send_game_data(websocket, move, "keyup")

        await asyncio.sleep(1)  # Wait for 1 second before the next move


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
        url, ssl=ssl_context, extra_headers=headers, ping_interval=None
    ) as websocket:
        print("WebSocket connection established.")

        game_state_event = asyncio.Event()
        game_state_data = {}

        # Start the AI movement logic coroutine
        asyncio.create_task(
            ai_movement_logic(websocket, game_state_event, game_state_data)
        )

        # Example loop to simulate key press and release
        while True:
            try:
                # Receive and print the game state
                async with asyncio.timeout(30):
                    game_state = await websocket.recv()
                    game_state_data.update(json.loads(game_state))
                    current_time = time.time()
                    # print(f"Received game state at {current_time}:")
                    # print(json.dumps(game_state_data, indent=2))

                    # Calculate and print the delay
                    server_timestamp = game_state_data["timestamp"]
                    delay = current_time - server_timestamp
                    # print(f"Delay: {delay:.4f} seconds")

                    # Signal that a new game state has been received
                    game_state_event.set()

                    # Clear the message queue
                    # while websocket.messages:
                    #     _ = await websocket.recv()
                    #     print("Skipped an old message")

                    # # Calculate AI move
                    # move = await calculate_ai_move(game_state_data)

                    # # Execute the move
                    # if move:
                    #     await send_game_data(websocket, move, "keydown")
                    #     await asyncio.sleep(random.uniform(0.2, 0.6))
                    #     await send_game_data(websocket, move, "keyup")

            except websockets.ConnectionClosedError as e:
                print(f"WebSocket connection closed: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")


# Main execution
session = login()
if session:
    asyncio.get_event_loop().run_until_complete(ai_bot(session))
