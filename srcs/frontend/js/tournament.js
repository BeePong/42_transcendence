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
  document.getElementById(
    "num-players-in-lobby"
  ).textContent = `${numPlayersInLobby}`;
};

function handleFullTournamentLobby() {
  console.log("handleFullTournamentLobby2");
  // setTimeout(() => {
    if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
      document.getElementById("tournament-lobby-section").classList.add("full");
      document.querySelector(".tournament_lobby__header").innerHTML =
        'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
      document.querySelector(".tournament_lobby__description").innerHTML =
        '<span id="player1"></span> vs <span id="player2"></span>';
      const playerCount = document.querySelector(
        ".tournament_lobby__player-count"
      );
      if (playerCount) {
        playerCount.remove();
      }
      const leaveButton = document.getElementById("leave-button");
      if (leaveButton) {
        leaveButton.remove();
      }
    }
  // }, 1000);
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
  insertPlayersInMatch
};
