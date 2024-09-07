// TODO: replace by websocket
// Mock WebSocket connection
export function mockWebSocket() {
  setTimeout(() => {
    if (/^\/tournament\/\d+\/lobby\/$/.test(window.location.pathname))
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

// Countdown in lobby page and navigate to the game page after countdown
export function tournamentLobbyCountdown() {
  let countdownValue = 3;
  const countdownElement = document.getElementById("countdown");

  setTimeout(() => {
    const countdownInterval = setInterval(() => {
      if (/^\/tournament\/\d+\/lobby\/$/.test(window.location.pathname)) {
        if (countdownValue > 1) {
          countdownValue--;
          countdownElement.textContent = `${countdownValue}`;
        } else {
          clearInterval(countdownInterval);
          navigate("/game/");
        }
      } else clearInterval(countdownInterval);
    }, 1000);
  }, 500);
}
const appendNewPlayerDiv = (playerAlias) => {
  console.log("appendNewPlayerDiv");
  const playerDiv = document.createElement("div");
  playerDiv.classList.add("tournament_lobby__name-container");
  playerDiv.innerHTML = `
		  <div class="tournament_lobby__name">${playerAlias}</div>
		  <span class="tournament_lobby__match-num"></span>
	  `;
  const nameListContainer = document.querySelector(
    ".tournament_lobby__name-list-container"
  );
  if (nameListContainer) {
    nameListContainer.appendChild(playerDiv);
  }
};

const updateNumPlayersInLobby = (numPlayersInLobby) => {
  console.log("updateNumPlayersInLobby");
  const numPlayersInLobbyElement = document.getElementById(
    "num-players-in-lobby"
  );
  if (numPlayersInLobbyElement)
    numPlayersInLobbyElement.textContent = `${numPlayersInLobby}`;
};

function handleFullTournamentLobby() {
  console.log("handleFullTournamentLobby2");
  document.getElementById("tournament-lobby-section").classList.add("full");
  document.querySelector(".tournament_lobby__header").innerHTML =
    'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
  document.querySelector(".tournament_lobby__description").innerHTML =
    '<span id="player1"></span> vs <span id="player2"></span>';
  const playerCount = document.querySelector(".tournament_lobby__player-count");
  if (playerCount) {
    playerCount.remove();
  }
}

function insertCountdown(countdownValue) {
  console.log("insertCountdown");
  const countdownElement = document.getElementById("countdown");
  countdownElement.textContent = `${countdownValue}`;
}

function insertPlayersInMatch(player1_alias, player2_alias) {
  console.log("insertPlayersInMatch");
  const player1Element = document.getElementById("player1");
  player1Element.textContent = `${player1_alias}`;
  const player2Element = document.getElementById("player2");
  player2Element.textContent = `${player2_alias}`;
}

export {
  appendNewPlayerDiv,
  handleFullTournamentLobby,
  updateNumPlayersInLobby,
  insertCountdown,
  insertPlayersInMatch,
};
