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
	const numPlayersInLobby = parseInt(document.getElementById('num-players-in-lobby').textContent, 10);
	const numPlayers = parseInt(document.getElementById('num-players').textContent, 10);

	// Update number of players in lobby
	const updatedNumPlayersInLobby = numPlayersInLobby + 1;
	document.getElementById('num-players-in-lobby').textContent = `${updatedNumPlayersInLobby}`;

	// Add new div for new player
	const playerDiv = document.createElement('div');
	playerDiv.classList.add('tournament_lobby__name-container');
	playerDiv.innerHTML = `
		<div class="tournament_lobby__name">Dummy</div>
		<span class="tournament_lobby__match-num"></span>
	`;
	document.querySelector('.tournament_lobby__name-list-container').appendChild(playerDiv);

	// If the lobby is full, go to handle full tournament lobby. Otherwise, add new players again
	(updatedNumPlayersInLobby === numPlayers) ? handleFullTournamentLobby() : mockWebSocket();
}

// Handle full tournament lobby
function handleFullTournamentLobby() {
	setTimeout(() => {
		if (/^\/tournament\/\d+\/lobby\/$/.test(window.location.pathname)) {
			document.getElementById('tournament-lobby-section').classList.add('full');
			document.querySelector('.tournament_lobby__header').innerHTML = 'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
			document.querySelector('.tournament_lobby__description').textContent = 'dummy vs dummy';
			document.querySelector('.tournament_lobby__player-count').remove();
			document.getElementById('leave-button').remove();
			tournamentLobbyCountdown();
		}
	}, 1000);
}

// Countdown in lobby page and navigate to the game page after countdown
export function tournamentLobbyCountdown() {
  let countdownValue = 3;
  const countdownElement = document.getElementById('countdown');

  setTimeout(() => {
    const countdownInterval = setInterval(() => {
			if (/^\/tournament\/\d+\/lobby\/$/.test(window.location.pathname))
			{
				if (countdownValue > 1) {
					countdownValue--;
					countdownElement.textContent = `${countdownValue}`;
				} else {
					clearInterval(countdownInterval);
					navigate('/game/');
				}
			}
			else
				clearInterval(countdownInterval);
    }, 1000);
  }, 500);
}
