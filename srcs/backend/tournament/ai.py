import asyncio
import json
import os
import random
import ssl
import time
import sys

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
FPS = 30
MAX_SCORE = 500
PADDING_THICKNESS = 7
THICK_BORDER_THICKNESS = 5
UPPER_LIMIT = PADDING_THICKNESS + PADDLE_HEIGHT / 2
LOWER_LIMIT = FIELD_HEIGHT - PADDING_THICKNESS - PADDLE_HEIGHT / 2


# Step 1: Log in to the website
def login(tournament_id):
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
        "username": "AI_Bot" + str(tournament_id),  # Replace with your actual username
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
            "username": "AI_Bot" + str(tournament_id),  # Same username as above
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

    # Debug print
    print(f"Ball position: x={ball_position['x']:.2f}, y={ball_position['y']:.2f}")
    print(f"Ball vector: x={ball_vector['x']:.2f}, y={ball_vector['y']:.2f}")
    print(f"Ball speed: {ball_speed:.2f}")
    print(f"AI paddle position: y={ai_paddle_position:.2f}")

    # Check if the ball is moving towards the AI paddle (left side)

    # Calculate time for the ball to reach the right edge
    time_to_right_edge = (FIELD_WIDTH - ball_position["x"]) / abs(
        ball_vector["x"] * ball_speed
    )

    # Predict the y-position where the ball will hit the right edge
    predicted_y = (
        ball_position["y"] + ball_vector["y"] * ball_speed * time_to_right_edge
    )

    # Handle bounces off top and bottom edges
    while predicted_y < 0 or predicted_y > FIELD_HEIGHT:
        if predicted_y < 0:
            predicted_y = -predicted_y
        elif predicted_y > FIELD_HEIGHT:
            predicted_y = 2 * FIELD_HEIGHT - predicted_y

    print(f"Ball will hit right edge at y = {predicted_y:.2f}")

    # Move paddle towards the predicted position
    paddle_center = ai_paddle_position + PADDLE_HEIGHT / 2
    if predicted_y < paddle_center - PADDLE_HEIGHT / 4:
        return "ArrowUp"
    elif predicted_y > paddle_center + PADDLE_HEIGHT / 4:
        return "ArrowDown"
    else:
        return None  # Stay in position


async def ai_movement_logic(websocket, game_state_event, game_state_data):
    while True:
        await game_state_event.wait()  # Wait for a new game state
        game_state_event.clear()  # After the event is set and the wait is over, reset the event.

        print("AI movement logic triggered")
        print("Game state data:")
        print(json.dumps(game_state_data, indent=2))
        # Check if the necessary keys are present in the game state data
        message = game_state_data.get("message", {})
        if "ball" in message and "player2" in message and "ball_vector" in message:
            ball_position = message["ball"]
            ball_vector = message["ball_vector"]
            print("Ball vector:", json.dumps(ball_vector, indent=2))

            # Check if it's the AI's turn to defend
            if ball_vector["x"] > 0:  # Ball is moving towards the AI paddle
                print("Ball is moving towards AI paddle (right side)")
                # Calculate AI move
                move = await calculate_ai_move(message)

                # Execute the move
                if move:
                    await send_game_data(websocket, move, "keydown")
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    await send_game_data(websocket, move, "keyup")
                # await asyncio.sleep(1)  # Wait for 1 second before the next move
            # else:
            #     print("Ball is moving away from AI paddle (right side)")

        # await asyncio.sleep(1)  # Wait for 1 second before the next move


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
async def ai_bot(session, tournament_id):
    # Step 1: Get CSRF token
    tournament_page_url = "https://nginx:8443/page/tournament/"
    try:
        response = session.get(tournament_page_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        csrf_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
        if csrf_input is None:
            print(
                "CSRF token input not found in the HTML. Trying to find it in cookies."
            )
            csrf_token = session.cookies.get("csrftoken")
            if csrf_token is None:
                raise ValueError("CSRF token not found in HTML or cookies")
        else:
            csrf_token = csrf_input.get("value")
        print("Successfully retrieved CSRF token.")
    except requests.RequestException as e:
        print(f"Failed to retrieve CSRF token: {e}")
        return

    # Step 2: Join the tournament
    join_tournament_url = "https://nginx:8443/page/tournament/"
    # tournament_id = tournament_id  # Replace with the actual tournament ID
    join_data = {
        "tournament_id": tournament_id,
        "alias": f"AI_Bot{tournament_id}",  # Set alias to be the same as username
        "csrfmiddlewaretoken": csrf_token,
    }

    try:
        response = session.post(
            join_tournament_url,
            data=join_data,
            headers={"Referer": tournament_page_url},
            verify=False,
        )
        response.raise_for_status()
        print("Successfully joined the tournament.")
    except requests.RequestException as e:
        print(f"Failed to join the tournament: {e}")
        return

    # Step 3: Establish WebSocket connection (existing code)
    url = f"wss://nginx:8443/ws/pong/{tournament_id}/"

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
        try:
            while True:
                try:
                    # Receive and print the game state
                    async with asyncio.timeout(30):
                        game_state = await websocket.recv()
                        game_state_data.update(json.loads(game_state))
                        current_time = time.time()

                        # Check if the game has finished
                        if (
                            game_state_data.get("type") == "tournament"
                            and game_state_data.get("message", {}).get("event")
                            == "game_finished"
                        ):
                            print("Game finished. Stopping AI bot.")
                            break

                        # Signal that a new game state has been received
                        game_state_event.set()

                except asyncio.TimeoutError:
                    print("Timeout waiting for game state. Reconnecting...")
                    break  # Break the loop to attempt reconnection
                except websockets.ConnectionClosedError as e:
                    print(f"WebSocket connection closed: {e}")
                    break  # Break the loop to attempt reconnection
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    break  # Break the loop for any other unexpected errors
        finally:
            print("Cleaning up and closing connection...")
            await websocket.close()
            # Perform any other necessary cleanup here


# Main execution
def run_ai_bot(tournament_id):
    session = login(tournament_id)
    if session:
        asyncio.get_event_loop().run_until_complete(ai_bot(session, tournament_id))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ai.py <tournament_id>")
        sys.exit(1)

    tournament_id = int(sys.argv[1])
    run_ai_bot(tournament_id)
