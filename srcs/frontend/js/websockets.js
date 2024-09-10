import { loadPage } from "./route.js";
import {
  appendNewPlayerDiv,
  updateNumPlayersInLobby,
  insertCountdown,
  handleFullTournamentLobby,
} from "./tournament.js";

// Constants
const CANVAS_HEIGHT = 500;
const CANVAS_WIDTH = 800;
const PADDLE_HEIGHT = 100;
const PADDLE_WIDTH = 26;
const BALL_RADIUS = 15;
const PADDING_THICKNESS = 7;
const THICK_BORDER_THICKNESS = 5;
const CANVAS_ID = "game_canvas";
const COUNTDOWN_TIME = 6; // half of this is tournament countdown time, half is game countdown time

let old_ball_speed, new_ball_speed;

let socket = null;
let socket_tournament_id = null;

const getContext = () => {
  const canvas = document.getElementById(CANVAS_ID);
  if (!canvas) return null;
  return canvas.getContext("2d");
};

// Listen for the custom event to close the WebSocket connection
window.addEventListener("navigateAwayFromTournamentLobby", () => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.close();
  }
});

const drawBorders = (context) => {
  context.strokeStyle = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--color-tertiary");
  context.lineWidth = 2;
  context.beginPath();
  context.moveTo(0, 0);
  context.lineTo(CANVAS_WIDTH, 0);
  context.lineTo(CANVAS_WIDTH, CANVAS_HEIGHT);
  context.lineTo(0, CANVAS_HEIGHT);
  context.lineTo(0, 0);
  context.stroke();
  context.fillStyle = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--color-tertiary");
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

const insertAliasesGameInfo = (player1_alias, player2_alias) => {
  const alias1 = document.getElementById("alias-player1");
  if (alias1) alias1.textContent = player1_alias;
  const alias2 = document.getElementById("alias-player2");
  if (alias2) alias2.textContent = player2_alias;
};

const drawPaddle = (context, y, playerType /* isControlling */) => {
  context.fillStyle = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--color-tertiary");
  const x =
    playerType === "player1"
      ? PADDING_THICKNESS
      : CANVAS_WIDTH - PADDLE_WIDTH - PADDING_THICKNESS;
  context.fillRect(x, y - PADDLE_HEIGHT / 2, PADDLE_WIDTH, PADDLE_HEIGHT);
};

const drawEmptyCanvas = (context) => {
  const backgroundColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--background-color");

  context.fillStyle = backgroundColor;
  context.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  drawBorders(context);
  drawBall(context, CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2);
};

function updateCanvas(context, game_data) {
  if (!context) return;
  if (new_ball_speed === undefined) new_ball_speed = game_data.ball_speed;
  old_ball_speed = new_ball_speed;
  new_ball_speed = game_data.ball_speed;
  insertAliasesGameInfo(
    game_data.player1.player_name,
    game_data.player2.player_name
  );
  if (game_data.state === "finished") {
    socket.close();
    return;
  }
  const backgroundColor = getComputedStyle(
    document.documentElement
  ).getPropertyValue("--background-color");
  context.fillStyle = backgroundColor;
  context.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);
  drawBorders(context);
  drawBall(context, game_data.ball.x, game_data.ball.y);
  if (game_data.countdown > 0) {
    drawCountdown(
      context,
      game_data.countdown,
      game_data.ball.x,
      game_data.ball.y
    );
  }
  drawPaddle(context, game_data.player1.y, "player1");
  drawPaddle(context, game_data.player2.y, "player2");
}

function openWebSocket(tournament_id, type = "tournament") {
  if (socket && socket_tournament_id === tournament_id) {
    return;
  }

  var url;
  if (type === "solo")
    url =
      (window.location.protocol == "https:" ? "wss://" : "ws://") +
      window.location.host +
      "/ws/pong/" +
      tournament_id +
      "/" +
      "?is_bot=True";
  else
    url =
      (window.location.protocol == "https:" ? "wss://" : "ws://") +
      window.location.host +
      "/ws/pong/" +
      tournament_id +
      "/" +
      "?is_bot=False";

  socket = new WebSocket(url);

  if (type === "solo") {
    const canvasContext = getContext();
    if (canvasContext) drawEmptyCanvas(canvasContext);
  }

  socket.onmessage = function (e) {
    const match = window.location.pathname.match(
      /^\/tournament\/(\d+)\/lobby\/?$/
    );
    const solo_match = window.location.pathname.match(
      /^\/tournament\/(\d+)\/solo_game\/?$/
    );
    if (!(match || solo_match)) {
      socket.close();
      return;
    }
    let data;
    try {
      data = JSON.parse(e.data);
    } catch (e) {
      return false;
    }
    switch (data.type) {
      case "tournament":
        const tournamentMessage = data.message;
        switch (tournamentMessage.event) {
          case "new_player":
            appendNewPlayerDiv(tournamentMessage.player_alias);
            updateNumPlayersInLobby(
              tournamentMessage.num_players_in_tournament
            );
            if (
              tournamentMessage.num_players_in_tournament ===
              tournamentMessage.num_players
            ) {
              handleFullTournamentLobby(
                tournamentMessage.player1_alias,
                tournamentMessage.player2_alias
              );
            }
            break;
          case "countdown":
            insertCountdown(tournamentMessage.countdown);
            if (tournamentMessage.countdown === 1) {
              loadPage(window.location.pathname, "/", false, "", true);
              const canvasContext = getContext();
              if (canvasContext) drawEmptyCanvas(canvasContext);
            }
            break;
          case "game_finished":
            loadPage(window.location.pathname, "/", false, "", true);
            break;
          case "tournament_finished":
            socket.close();
            break;
          case "test":
            break;
          default:
            console.log("default");
        }
        break;

      case "game":
        if (data.message.countdown <= 3) {
          const gameState = data.message;
          const canvasContext = getContext();
          if (canvasContext) updateCanvas(canvasContext, gameState);
        }
        break;
    }
  };

  socket.onopen = function (e) {};

  socket.onerror = function (error) {};

  socket.onclose = function (e) {};

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

export { openWebSocket };
