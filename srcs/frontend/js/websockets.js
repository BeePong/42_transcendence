function webSocketTest(tournament_id) {
  const canvas_height = 500;
  const canvas_width = 800;
  const paddle_height = 100;
  const paddle_width = 26;
  const ball_radius = 15;
  const padding_thickness = 7;
  const thick_border_thickness = 5;

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
    context.fillRect(0, 0, canvas_width, thick_border_thickness);
    context.fillRect(
      0,
      canvas_height - thick_border_thickness,
      canvas_width,
      thick_border_thickness
    );
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

export { webSocketTest };
