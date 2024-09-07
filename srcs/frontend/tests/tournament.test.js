import {
	appendNewPlayerDiv,
	updateNumPlayersInLobby,
	handleFullTournamentLobby,
	insertCountdown,
	insertPlayersInMatch
} from '../js/tournament';

// Set up a basic DOM environment for testing using jsdom
const { JSDOM } = require('jsdom');
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
  <body>
    <div id="num-players-in-lobby"></div>
    <section id="tournament-lobby-section"></section>
    <div class="tournament_lobby__name-list-container"></div>
    <div class="tournament_lobby__header"></div>
    <div class="tournament_lobby__description"></div>
    <div class="tournament_lobby__player-count"></div>
    <button id="leave-button"></button>
    <span id="countdown"></span>
    <span id="player1"></span>
    <span id="player2"></span>
  </body>
</html>
`);

// Use the simulated DOM as the global DOM for the test
global.window = dom.window;
global.document = dom.window.document;

jest.useFakeTimers(); // In case there are timeouts or intervals in the code

describe('Tournament Lobby Functions', () => {
  beforeEach(() => {
    // Reset any DOM changes before each test
    document.body.innerHTML = dom.window.document.body.innerHTML;
  });

  test('appendNewPlayerDiv should add a new player div to the name list container', () => {
    const playerAlias = 'Player1';
    appendNewPlayerDiv(playerAlias);

    const nameListContainer = document.querySelector('.tournament_lobby__name-list-container');
    const playerDiv = nameListContainer.querySelector('.tournament_lobby__name-container');

    expect(playerDiv).not.toBeNull();
    expect(playerDiv.textContent).toContain(playerAlias);
  });

  test('updateNumPlayersInLobby should update the number of players', () => {
    const numPlayers = 5;
    updateNumPlayersInLobby(numPlayers);

    const numPlayersInLobbyElement = document.getElementById('num-players-in-lobby');
    expect(numPlayersInLobbyElement.textContent).toBe(`${numPlayers}`);
  });

  test('handleFullTournamentLobby should update the lobby DOM elements for a full tournament', () => {
    // Mock window.location.pathname
    Object.defineProperty(window, 'location', {
      value: {
        pathname: '/tournament/123/lobby'
      },
      writable: true,
    });

    handleFullTournamentLobby();

    const lobbySection = document.getElementById('tournament-lobby-section');
    expect(lobbySection.classList.contains('full')).toBe(true);

    const header = document.querySelector('.tournament_lobby__header');
    expect(header.innerHTML).toContain('BEEPONG CUP IS STARTING');

    const description = document.querySelector('.tournament_lobby__description');
    expect(description.innerHTML).toContain('vs');

    const playerCount = document.querySelector('.tournament_lobby__player-count');
    expect(playerCount).toBeNull();

    const leaveButton = document.getElementById('leave-button');
    expect(leaveButton).toBeNull();
  });

  test('insertCountdown should update the countdown value', () => {
    const countdownValue = 10;
    insertCountdown(countdownValue);

    const countdownElement = document.getElementById('countdown');
    expect(countdownElement.textContent).toBe(`${countdownValue}`);
  });

  test('insertPlayersInMatch should update player names in the match', () => {
    const player1 = 'Player1';
    const player2 = 'Player2';

    insertPlayersInMatch(player1, player2);

    const player1Element = document.getElementById('player1');
    const player2Element = document.getElementById('player2');

    expect(player1Element.textContent).toBe(player1);
    expect(player2Element.textContent).toBe(player2);
  });
});