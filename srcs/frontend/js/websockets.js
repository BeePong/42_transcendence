let old_ball_speed, new_ball_speed;

function webSocketTest(tournament_id) {
  const canvas_height = 500;
  const canvas_width = 800;
  const paddle_height = 100;
  const paddle_width = 26;
  const ball_radius = 15;
  const padding_thickness = 7;
  const thick_border_thickness = 5;

  const url =
    (window.location.protocol == "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws/pong/" +
    tournament_id +
    "/" +
    "?is_bot=False";

  console.log("Starting WebSocket on URL: ", url);
  var socket = new WebSocket(url);
  // TODO: remember to close websocket after the tournament is over
  var canvas = document.getElementById("game_canvas");
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

  const drawCountdown = (countdown, x, y) => {
    context.fillStyle = "black";
    context.font = "20px Arial";
    context.textAlign = "center";
    context.textBaseline = "middle";
    context.fillText(countdown, x, y);
  };

  const insertScores = (player1_score, player2_score) => {
    const score1 = document.getElementById("score-player1");
    if (score1) score1.textContent = player1_score;
    const score2 = document.getElementById("score-player2");
    if (score2) score2.textContent = player2_score;
  };

  const drawPaddle = (y, player_type, controlling) => {
    const x =
      player_type === "player1"
        ? canvas_width - padding_thickness - paddle_width
        : padding_thickness;
    context.fillStyle = controlling ? "yellow" : "white";
    context.fillRect(x, y - paddle_height / 2, paddle_width, paddle_height);
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
    console.log("WebSocket message received");
    var data = JSON.parse(e.data);
    // parse message
    var jsonData = JSON.parse(data);
    // if type is tournament
    if (jsonData.type === "tournament") {
      var tournament_data = jsonData.message;
      console.log("tournament_data:", tournament_data);
      console.log("window.pathname", window.pathname);
      if (tournament_data.state === "NEW") {
        console.log("tournament is new, reloading page");
        loadPage(window.pathname);
      }
    } else {
      console.log("game data:", jsonData.message);
      updateCanvas(jsonData.message);
    }

    // Here tournament_lobby function will be called once the winner is determined, call loadPage on window.pathname (reload page)
    // every time game state is updated
    // if tpirnament not full
    // navigate to refresh page
    // when new player joins, send player into to tournamentLobbyAddPlayer(player), numPlayers and updatedNumPlayersInLobby
    // state is countdown, seconds number is 2, 1, 0 and call function to change number in countdown

    // when state is playing
    return false;
  };

  // console.log("webSocketTest SOCKET", socket); // for debugging

  socket.onopen = function (e) {
    console.log("WebSocket connection opened");
  };

  socket.onerror = function (error) {
    console.error("WebSocket error observed:", error);
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
    if (new_ball_speed === undefined) new_ball_speed = game_data.ball.speed;
    old_ball_speed = new_ball_speed;
    new_ball_speed = game_data.ball.speed;
    if (old_ball_speed !== new_ball_speed) {
      console.log("ball speed changed", old_ball_speed, new_ball_speed);
    }
    insertScores(game_data.player1.score, game_data.player2.score);
    if (game_data.state === "finished") {
      console.log("winner is", game_data.winner.username);
      socket.close();
      return;
    }
    //console.log("updateCanvas game_data", game_data);
    context.fillStyle = backgroundColor;
    context.fillRect(0, 0, canvas_width, canvas_height);
    drawBorders();
    drawBall(game_data.ball.x, game_data.ball.y);
    if (game_data.state === "countdown") {
      drawCountdown(game_data.countdown, game_data.ball.x, game_data.ball.y);
    }
    // TODO: pass controlling param to drawPaddle
    drawPaddle(game_data.player1.y, "player1");
    drawPaddle(game_data.player2.y, "player2");
  }
}

export { webSocketTest };
