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

      if (page === "/tournament/pong") webSocketTest();
    }
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

function webSocketTest() {
  const canvas_height = 500;
  const canvas_width = 800;
  const paddle_height = 100;
  const paddle_width = 20;
  const increment = 10;
  const fps = 60;
  let upPressed = false;
  let downPressed = false;
  let paddle_y = 400;

  console.log("webSocketTest");
  var socket = new WebSocket("ws://localhost:8000/ws/pong/");
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
  };
  var backgroundColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--background-color");
  context.fillStyle = backgroundColor;
  context.fillRect(0, 0, canvas_width, canvas_height);
  drawBorders();

  socket.onmessage = function (e) {
    var data = JSON.parse(e.data);
    console.log(data);
    document.getElementById("messageDisplay").innerText = data.message;

    // Updating our game field will be here
  };

  console.log("webSocketTest SOCKET", socket); // for debugging

  socket.onopen = function (e) {
    console.log("WebSocket connection opened");
  };

  socket.onclose = function (e) {
    console.log("WebSocket connection closed");
  };

  document.getElementById("tournamentSendButton").onclick = function () {
    socket.send(
      JSON.stringify({
        message: "Test tournament message from client!",
        type: "tournament",
      })
    );
  };

  document.getElementById("gameSendButton").onclick = function () {
    socket.send(
      JSON.stringify({
        message: "Test game message from client!",
        type: "game",
      })
    );
  };

  function sendGameData(paddle_x, paddle_y, ball_x, ball_y) {
    socket.send(
      JSON.stringify({
        message: {
          paddle_x: paddle_x,
          paddle_y: paddle_y,
          ball_x: ball_x,
          ball_y: ball_y,
        },
        type: "game",
      })
    );
  }

  // Listen for keydown events
  window.addEventListener("keydown", function (event) {
    if (event.key === "ArrowUp") {
      upPressed = true;
    } else if (event.key === "ArrowDown") {
      downPressed = true;
    }
  });

  // Listen for keyup events
  window.addEventListener("keyup", function (event) {
    if (event.key === "ArrowUp") {
      upPressed = false;
    } else if (event.key === "ArrowDown") {
      downPressed = false;
    }
  });

  function updateCanvas(paddle_y) {
    context.fillStyle = backgroundColor;
    context.fillRect(0, 0, canvas_width, canvas_height);
    drawBorders();
    context.fillStyle = "white";
    context.fillRect(canvas_width - 50, paddle_y, 20, 100);
  }

  // In your game loop, check the flags and move the paddle
  setInterval(function () {
    if (upPressed) {
      if (paddle_y > paddle_height / 2) {
        paddle_y -= increment;
      } else {
        paddle_y = paddle_height / 2;
      }
    } else if (downPressed) {
      if (paddle_y < canvas_height - paddle_height - paddle_height / 2) {
        paddle_y += increment;
      } else {
        paddle_y = canvas_height - paddle_height - paddle_height / 2;
      }
    }
    // Send the game data
    updateCanvas(paddle_y);
    sendGameData(paddle_y);
  }, 1000 / fps);
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
