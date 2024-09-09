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

function handleFullTournamentLobby(player1_alias, player2_alias) {
  const lobbySection = document.getElementById("tournament-lobby-section");
  const header = document.querySelector(".tournament_lobby__header");
  const playerCount = document.querySelector(".tournament_lobby__player-count");

  if (lobbySection) lobbySection.classList.add("full");
  if (header)
    header.innerHTML =
      'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
  if (playerCount) playerCount.remove();
}

function insertCountdown(countdownValue) {
  console.log("insertCountdown");
  const countdownElement = document.getElementById("countdown");
  if (countdownElement) countdownElement.textContent = `${countdownValue}`;
}

export {
  appendNewPlayerDiv,
  handleFullTournamentLobby,
  updateNumPlayersInLobby,
  insertCountdown,
};
