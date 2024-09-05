// Constants
const CANVAS_HEIGHT = 500;
const CANVAS_WIDTH = 800;
const PADDLE_HEIGHT = 100;
const PADDLE_WIDTH = 26;
const BALL_RADIUS = 15;
const PADDING_THICKNESS = 7;
const THICK_BORDER_THICKNESS = 5;
const CANVAS_ID = "game_canvas";

let old_ball_speed, new_ball_speed;

const getContext = () => {
  const canvas = document.getElementById(CANVAS_ID);
  if (!canvas) return null;
  return canvas.getContext("2d");
};

const drawBorders = (context) => {
  context.strokeStyle = "white";
  context.lineWidth = 2;
  context.beginPath();
  context.moveTo(0, 0);
  context.lineTo(CANVAS_WIDTH, 0);
  context.lineTo(CANVAS_WIDTH, CANVAS_HEIGHT);
  context.lineTo(0, CANVAS_HEIGHT);
  context.lineTo(0, 0);
  context.stroke();
  context.fillStyle = "white";
  context.fillRect(0, 0, CANVAS_WIDTH, THICK_BORDER_THICKNESS);
  context.fillRect(
    0,
    CANVAS_HEIGHT - THICK_BORDER_THICKNESS,
    CANVAS_WIDTH,
    THICK_BORDER_THICKNESS
  );
};

const drawBall = (context, x, y) => {
  const ballColor = getComputedStyle(document.documentElement).getPropertyValue(
    "--color-secondary"
  );
  context.fillStyle = ballColor;
  context.beginPath();
  context.arc(x, y, BALL_RADIUS, 0, Math.PI * 2);
  context.fill();
};

const drawCountdown = (context, countdown, x, y) => {
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

const drawPaddle = (context, y, player_type, controlling) => {
  const x =
    player_type === "player1"
      ? CANVAS_WIDTH - PADDING_THICKNESS - PADDLE_WIDTH
      : PADDING_THICKNESS;
  context.fillStyle = controlling ? "yellow" : "white";
  context.fillRect(x, y - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
};

const drawEmptyCanvas = (context) => {
  var backgroundColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--background-color");

  context.fillStyle = backgroundColor;
  context.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  drawBorders(context);
  drawBall(context, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
};

function updateCanvas(context, game_data) {
  if (!context) return;
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
  context.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  drawBorders(context);
  drawBall(context, game_data.ball.x, game_data.ball.y);
  if (game_data.state === "countdown") {
    drawCountdown(
      context,
      game_data.countdown,
      game_data.ball.x,
      game_data.ball.y
    );
  }
  // TODO: pass controlling param to drawPaddle
  drawPaddle(context, game_data.player1.y, "player1");
  drawPaddle(context, game_data.player2.y, "player2");
}

function webSocketTest(tournament_id) {
  const canvasContext = getContext();
  if (canvasContext) drawEmptyCanvas(canvasContext);
  const url =
    (window.location.protocol == "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws/pong/" +
    tournament_id +
    "/" +
    "?is_bot=False";

  console.log("Starting WebSocket on URL: ", url);
  var socket = new WebSocket(url);
  console.log("WebSocket created: ", socket);
  // TODO: remember to close websocket after the tournament is over

  socket.onmessage = function (e) {
    console.log("WebSocket message received");
    var data = JSON.parse(e.data);
    console.log("parsed data:", data);
    // parse message
    // try {
    //   var jsonData = JSON.parse(data);
    // } catch (e) {
    //   console.log("Error parsing JSON data", e);
    //   return false;
    // }
    // if type is tournament
    if (data.type === "tournament") {
      var tournament_data = data.message;
      console.log("tournament_data:", tournament_data);
      console.log("window.location.pathname", window.location.pathname);
      console.log("tournament_data.state", tournament_data.state);
      // if (tournament_data.state === "NEW") {
      //   console.log("tournament is new, reloading page");
      //   loadPage(window.location.pathname); //TODO: console logging error that loadPoge is not defined here. Also, we should not reload page 'cause it tries to connect to websocket again and might cause errors. Asked Wing about this.
      // }
    } else {
      console.log("game data:", data.message);
      updateCanvas(canvasContext, jsonData.message);
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
}

export { webSocketTest };