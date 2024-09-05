import { loadPage } from "./route.js";
import {
  appendNewPlayerDiv,
  updateNumPlayersInLobby,
  insertCountdown,
  //handleFullTournamentLobby,
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

const drawPaddle = (context, y, playerType, isControlling) => {
  context.fillStyle = isControlling ? "yellow" : "white";
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

// function updateCanvas(context, game_data) {
//   if (!context || !game_data) return;

//   // Clear the canvas
//   context.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

//   // Draw the paddles
//   drawPaddle(context, game_data.player1_paddle_y, "player1", playerNumber === 1);
//   drawPaddle(context, game_data.player2_paddle_y, "player2", playerNumber === 2);

//   // Draw the ball
//   drawBall(context, game_data.ball.x, game_data.ball.y);

//   // Draw the borders
//   drawBorders(context);

//   // Update scores
//   insertScores(game_data.player1_score, game_data.player2_score);

//   // Debug output
//   console.log("Drawing paddles:", game_data.player1_paddle_y, game_data.player2_paddle_y);
// }

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
  console.log("updateCanvas game_data", game_data);
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

function openWebSocket(tournament_id) {
  const canvasContext = getContext();
  const url =
    (window.location.protocol == "https:" ? "wss://" : "ws://") +
    window.location.host +
    "/ws/pong/" +
    tournament_id +
    "/" +
    "?is_bot=False";

  console.log("Starting WebSocket on URL: ", url);
  const socket = new WebSocket(url);
  console.log("WebSocket created: ", socket);
  // TODO: remember to close websocket after the tournament is over

  socket.onmessage = function (e) {
    console.log("WebSocket message received");
    console.log("window.location.pathname", window.location.pathname);
    let data;
    try {
      data = JSON.parse(e.data);
    } catch (e) {
      console.log("Error parsing JSON data", e);
      return false;
    }
    console.log("parsed data:", data);
    switch (data.type) {
      case "tournament":
        // BELOW DIEGO'S VERSION
        // var tournament_data = data.message;

        // if (tournament_data.state === "PLAYING" && tournament_data.game_data) {
        //   console.log("tournament is playing, updating canvas");
        //   const canvasContext = getContext();
        //   if (canvasContext && tournament_data.game_data) {
        //     updateCanvas(canvasContext, tournament_data.game_data);
        //   }
        // } else if (tournament_data.state === "FINISHED") {
        //   console.log("Tournament finished. Winner:", tournament_data.winner);
        //   // Handle end of tournament (e.g., display winner, offer to start new game)
        // } else if (tournament_data.state === "WAITING") {
        //   console.log(
        //     "Waiting for players. Current players:",
        //     tournament_data.players
        //   );
        //   // Update UI to show waiting state and current players
        // }
        // updateTournamentInfo(tournament_data);

        const tournamentMessage = data.message;
        switch (tournamentMessage.event) {
          case "new_player":
            console.log("new_player");
            appendNewPlayerDiv(tournamentMessage.player_alias);
            updateNumPlayersInLobby(
              tournamentMessage.num_players_in_tournament
            );
            if (
              tournamentMessage.num_players_in_tournament ===
              tournamentMessage.num_players
            )
              handleFullTournamentLobby();
            break;
          case "countdown":
            console.log("countdown");
            if (tournamentMessage.countdown === 3)
              console.log("countdown is 3");
            loadPage(window.location.pathname);
            insertCountdown(tournamentMessage.countdown);
            break;
          // maybe not needed? just send game message instead
          case "game_started":
            console.log("game_started");
            const canvasContext = getContext();
            if (canvasContext) drawEmptyCanvas(canvasContext);
            break;
          case "game_finished":
            console.log("game_finished");
            // TODO: render winner page
            break;
          case "tournament_finished":
            console.log("tournament_finished");
            console.log("winner is", tournamentMessage.winner);
            break;
          default:
            loadPage(window.location.pathname);
        }

      case "game":
        const gameState = data.message;
        updateCanvas(canvasContext, gameState);
        break;
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
  function updateTournamentInfo(tournament_data) {
    // Update tournament state
    const stateElement = document.getElementById("tournament-state");
    if (stateElement) {
      stateElement.textContent = tournament_data.state;
    }

    // Update player list
    const playerListElement = document.getElementById("player-list");
    if (playerListElement) {
      playerListElement.textContent = tournament_data.players.join(", ");
    }

    // Update number of players
    const numPlayersElement = document.getElementById("num-players");
    if (numPlayersElement) {
      numPlayersElement.textContent = tournament_data.num_players;
    }

    // Update winner (if the tournament is finished)
    if (tournament_data.state === "FINISHED") {
      const winnerElement = document.getElementById("winner");
      if (winnerElement) {
        winnerElement.textContent = tournament_data.winner;
      }
    }

    // You can add more updates here based on your specific UI needs
  }
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
          //playerNumber: playerNumber,
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
