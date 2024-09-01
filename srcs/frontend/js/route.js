// Handle navigation based on path or event 
export function navigate(eventOrPath, redirectUrl = '/') {
	let path;
	if (typeof eventOrPath === 'string')
			path = eventOrPath;
	else {
			eventOrPath.preventDefault();
			path = eventOrPath.currentTarget.getAttribute('href');
	}

	// Do not render again for the same path
	if (window.location.pathname === path)
			return;

	loadPage(path, redirectUrl, true);
}

// Load content based on the path, and add the redirect url for login and register page 
export async function loadPage(path, redirectUrl = '/', fromNavigate = false, queryString = '') {
	// If the path is '/', set page to '/home'.
	// Otherwise, remove the trailing slash from the path and set page to the resulting string.
	const page = path === '/' ? '/home' : path.replace(/\/$/, '');
	try {
			const response = await fetch(`/page${page}/${queryString}`);

			if (!response.ok) {
					if (!(response.status === 400 || response.status === 401 || response.status === 404))
							throw new Error('Network response was not ok');
			}

			// If the navigation was triggered programmatically (fromNavigate is true) and the response status is not 401 (unauthorized),
			// update the browser's history to the new path without reloading the page.
			if (fromNavigate === true && response.status !== 400 && response.status !== 401)
				history.pushState(null, null, path);

			// Handle 42 authorization error by fetching the error page
			if (page === '/accounts/oauth_error' && response.status === 400)
				fetchOauthErrorPage();
			// Redirect to login page if the user is not login
			else if (response.status === 401) {
				const data = await response.json();
				if (data.authenticated === false) {
					redirectToLoginPage(redirectUrl);
				}
			}
			else {
				const data = await response.text();
				document.getElementById('content').innerHTML = data;

				// Add the redirect url for login and register page 
				if ((page === '/accounts/login' || page === '/accounts/register') && redirectUrl !== '/')
					changeRedirectUrlandOauthState(redirectUrl);

				// perform countdown in tournmament lobby if the list is full. Otherwise, wait for other players.
				if (/^\/tournament\/\d+\/lobby$/.test(page)) {
					if (document.querySelector('.full')) {
						if (!document.querySelector('.winner'))
							tournamentLobbyCountdown()
					}
					else
						mockWebSocket(); //TODO: open websocket
				}
			}
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}

// Fetching the error page for 42 authorization error
async function fetchOauthErrorPage() {
	try {
		const response = await fetch('/page/accounts/oauth_error/');
		if (!response.ok) {
				throw new Error('Network response was not ok');
		}
		const data = await response.text();
		document.getElementById('content').innerHTML = data;
	}
	catch (error) {
		console.error('There was a problem with the fetch operation:', error);
	}
}

// redirect to login page
async function redirectToLoginPage(redirectUrl) {
	
	// update the browser's history to the login path
	history.pushState(null, null, '/accounts/login');

	try {
		const response = await fetch('/page/accounts/login/');
		if (!response.ok) {
				throw new Error('Network response was not ok');
		}
		const data = await response.text();
		document.getElementById('content').innerHTML = data;

		changeRedirectUrlandOauthState(redirectUrl);
	}
	catch (error) {
		console.error('There was a problem with the fetch operation:', error);
	}
}

// Change the redirect url in the form and the state of the oauth
function changeRedirectUrlandOauthState(redirectUrl) {
	// Change the redirect url in the form
	document.getElementById('redirectUrl').value = redirectUrl;

	// Change the state of the oauth according to the redirect url
	const login42UrlElement = document.getElementById('login-42-url');

	const updatedLogin42Url = new URL(login42UrlElement.href);
	const newStateParam = `qwerty|${encodeURIComponent(`https://localhost${redirectUrl}`)}`;
	updatedLogin42Url.searchParams.set('state', newStateParam);

	login42UrlElement.href = updatedLogin42Url.toString();
}

// TODO: replace by websocket
// Mock WebSocket connection
function mockWebSocket() {
	setTimeout(() => {
		if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname))
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
		if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
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
function tournamentLobbyCountdown() {
  let countdownValue = 3;
  const countdownElement = document.getElementById('countdown');

  setTimeout(() => {
    const countdownInterval = setInterval(() => {
			if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname))
			{
				if (countdownValue > 1) {
					countdownValue--;
					countdownElement.textContent = `${countdownValue}`;
				} else {
					clearInterval(countdownInterval);
					navigate('/game');
				}
			}
			else
				clearInterval(countdownInterval);
    }, 1000);
  }, 500);
}

// Load navbar
export async function loadNavBar() {
	try {
			const response = await fetch('/page/navbar/');
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			const data = await response.text();
			document.getElementById('navbar-content').innerHTML = data;
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}

// Listen to popstate events for back/forward navigation
window.addEventListener('popstate', () => {
	loadPage(window.location.pathname);
});

// Initial page load
document.addEventListener('DOMContentLoaded', () => {
	loadNavBar();
	loadPage(window.location.pathname, '/', false, window.location.search);
});

// Attach navigate to the global window object for use in inline event handlers
window.navigate = navigate;