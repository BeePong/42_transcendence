// Handle navigation based on path or event
function navigate(eventOrPath, redirectUrl = "/") {
  let path;
  if (typeof eventOrPath === "string") path = eventOrPath;
  else {
    eventOrPath.preventDefault();
    path = eventOrPath.currentTarget.getAttribute("href");
  }

  // Do not render again for the same path
  if (window.location.pathname === path) return;

  loadPage(path, redirectUrl, true);
}

// Load content based on the path, and add the redirect url for login and register page
async function loadPage(path, redirectUrl = "/", fromNavigate = false) {
  // If the path is '/', set page to '/home'.
  // Otherwise, remove the trailing slash from the path and set page to the resulting string.
  const page = path === "/" ? "/home" : path.replace(/\/$/, "");
  try {
    const response = await fetch(`/page${page}/`);

    if (!response.ok) {
      if (!(response.status === 401 || response.status === 404))
        throw new Error("Network response was not ok");
    }

    // If the navigation was triggered programmatically (fromNavigate is true) and the response status is not 401 (unauthorized),
    // update the browser's history to the new path without reloading the page.
    if (fromNavigate === true && response.status !== 401)
      history.pushState(null, null, path);

    // Redirect to login page if the user is not login
    if (response.status === 401) {
      const data = await response.json();
      if (data.authenticated === false) {
        redirectToLoginPage(redirectUrl);
      }
    } else {
      const data = await response.text();
      document.getElementById("content").innerHTML = data;

      // Add the redirect url for login and register page
      if (page === "/accounts/login" || page === "/accounts/register")
        document.getElementById("redirectUrl").value = redirectUrl;
      // console.log("page", page);
      //if (page === "/tournament/pong") webSocketTest();
      // if url contains "lobby", start mockWebSocket
      var match = page.match(/^\/tournament\/(\d+)\/lobby$/);
      console.log("match", match);
      if (match) {
        var tournament_id = match[1];
        webSocketTest(tournament_id);
      }
    }
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

function webSocketTest(tournament_id) {
  const canvas_height = 500;
  const canvas_width = 800;
  const paddle_height = 100;
  const paddle_width = 26;
  const ball_radius = 15;
  const padding_thickness = 5;

  // console.log("webSocketTest");
  // console.log("window.location.protocol", window.location.protocol);
  // var socket = new WebSocket("ws://localhost:8000/ws/pong/");
  const url =
    (window.location.protocol == "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws/pong/" +
    tournament_id +
    "/";

  // console.log("Starting WebSocket on URL: ", url);
  var socket = new WebSocket(url);
  // TODO: remember to close websocket after the tournament is over
  var canvas = document.getElementById("gameCanvas");
  var context = canvas.getContext("2d");

  const drawBorders = () => {
    context.strokeStyle = "white";
    context.lineWidth = 2;
    context.beginPath();
    context.moveTo(0, 0);
    context.lineTo(canvas_width, 0);
    context.lineTo(canvas_width, canvas_height);
    context.lineTo(0, canvas_height);
    context.lineTo(0, 0);
    context.stroke();
    context.fillStyle = "white";
    // TODO: finish drawing borders
  };

  const drawBall = (x, y) => {
    context.fillStyle = primaryColor;
    context.beginPath();
    context.arc(x, y, ball_radius, 0, Math.PI * 2);
    context.fill();
  };

  const drawPaddle = (y) => {
    context.fillStyle = "white";
    context.fillRect(
      canvas_width - padding_thickness - paddle_width,
      y - paddle_height / 2,
      paddle_width,
      paddle_height
    );
  };

  var backgroundColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--background-color");
  var primaryColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--color-secondary");

  context.fillStyle = backgroundColor;
  context.fillRect(0, 0, canvas_width, canvas_height);
  drawBorders();
  drawBall(canvas_width / 2, canvas_height / 2);

  socket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    console.log("socket data:", data);
    updateCanvas(data);
    // Updating our game field will be here
  };

  // console.log("webSocketTest SOCKET", socket); // for debugging

  socket.onopen = function (e) {
    console.log("WebSocket connection opened");
  };

  socket.onclose = function (e) {
    console.log("WebSocket connection closed");
  };

  function sendGameData(key, keyAction) {
    socket.send(
      JSON.stringify({
        message: {
          key: key,
          keyAction: keyAction,
          player_id: "player1",
        },
        type: "game",
      })
    );
  }

  window.addEventListener("keydown", function (event) {
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      sendGameData(event.key, "keydown");
    }
  });

  window.addEventListener("keyup", function (event) {
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      sendGameData(event.key, "keyup");
    }
  });

  function updateCanvas(game_data) {
    //console.log("updateCanvas game_data", game_data);
    context.fillStyle = backgroundColor;
    context.fillRect(0, 0, canvas_width, canvas_height);
    drawBorders();
    drawBall(game_data.ball.x, game_data.ball.y);
    drawPaddle(game_data.player1.y);
  }
}

// redirect to login page
async function redirectToLoginPage(redirectUrl) {
  // update the browser's history to the login path
  history.pushState(null, null, "/accounts/login");

  try {
    const response = await fetch("/page/accounts/login/");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.text();
    document.getElementById("content").innerHTML = data;
    document.getElementById("redirectUrl").value = redirectUrl;
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// TODO: replace by websocket
// Mock WebSocket connection
function mockWebSocket() {
  setTimeout(() => {
    if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname))
      tournamentLobbyAddPlayer();
  }, 1000); // Simulate a new player joining every second
}

// Add player in the tournament lobby
function tournamentLobbyAddPlayer() {
  const numPlayersInLobby = parseInt(
    document.getElementById("num-players-in-lobby").textContent,
    10
  );
  const numPlayers = parseInt(
    document.getElementById("num-players").textContent,
    10
  );

  // Update number of players in lobby
  const updatedNumPlayersInLobby = numPlayersInLobby + 1;
  document.getElementById(
    "num-players-in-lobby"
  ).textContent = `${updatedNumPlayersInLobby}`;

  // Add new div for new player
  const playerDiv = document.createElement("div");
  playerDiv.classList.add("tournament_lobby__name-container");
  playerDiv.innerHTML = `
		<div class="tournament_lobby__name">Dummy</div>
		<span class="tournament_lobby__match-num"></span>
	`;
  document
    .querySelector(".tournament_lobby__name-list-container")
    .appendChild(playerDiv);

  // If the lobby is full, go to handle full tournament lobby. Otherwise, add new players again
  updatedNumPlayersInLobby === numPlayers
    ? handleFullTournamentLobby()
    : mockWebSocket();
}

// Handle full tournament lobby
function handleFullTournamentLobby() {
  setTimeout(() => {
    if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
      document.getElementById("tournament-lobby-section").classList.add("full");
      document.querySelector(".tournament_lobby__header").innerHTML =
        'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
      document.querySelector(".tournament_lobby__description").textContent =
        "dummy vs dummy";
      document.querySelector(".tournament_lobby__player-count").remove();
      document.getElementById("leave-button").remove();
      tournamentLobbyCountdown();
    }
  }, 1000);
}

// Countdown in lobby page and navigate to the game page after countdown
function tournamentLobbyCountdown() {
  let countdownValue = 3;
  const countdownElement = document.getElementById("countdown");

  setTimeout(() => {
    const countdownInterval = setInterval(() => {
      if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
        if (countdownValue > 1) {
          countdownValue--;
          countdownElement.textContent = `${countdownValue}`;
        } else {
          clearInterval(countdownInterval);
          navigate("/game");
        }
      } else clearInterval(countdownInterval);
    }, 1000);
  }, 500);
}

// Load navbar
async function loadNavBar() {
  try {
    const response = await fetch("/page/navbar/");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.text();
    document.getElementById("navbar-content").innerHTML = data;
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// Listen to popstate events for back/forward navigation
window.addEventListener("popstate", () => {
  loadPage(window.location.pathname);
});

// Initial page load
document.addEventListener("DOMContentLoaded", () => {
  loadNavBar();
  loadPage(window.location.pathname);
});
