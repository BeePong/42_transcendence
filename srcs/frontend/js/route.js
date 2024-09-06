import { openWebSocket } from "./websockets.js";
import { tournamentLobbyCountdown } from "./tournament.js";

// Handle navigation based on path or event 
function navigate(eventOrPath, redirectUrl = '/') {
	const path = typeof eventOrPath === 'string' 
		? eventOrPath 
		: (eventOrPath.preventDefault(), eventOrPath.currentTarget.getAttribute('href'));

	if (window.location.pathname !== path) // Do not render again for the same path
		loadPage(path, redirectUrl, true);
}

// Load content based on the path
export async function loadPage(path, redirectUrl = '/', fromNavigate = false, queryString = '') {
	// If the path is '/', set page to '/home'.
	// Otherwise, remove the trailing slash from the path and set page to the resulting string.
	const page = path === '/' ? '/home' : path.replace(/\/$/, '');
	try {
			const response = await fetch(`/page${page}/${queryString}`);

			if (!response.ok && response.status !== 404) {
					if (response.status === 400 || response.status === 401) {
						if (response.status === 400)
							return loadPage('/accounts/oauth_error/'); // Handle oauth error response by fetching the error page
						else
							return navigate('/accounts/login/', redirectUrl); // Redirect to login page if the user is not authenticated	
					}
					else {
						throw new Error('Network response was not ok');
					}
			}
			if (fromNavigate === true) // If this function is called by navigate(), update the browser's history to the new path without reloading the page
				history.pushState(null, null, path);

			const data = await response.text();
			updatePageContent(data, page, redirectUrl); // Handle content updates
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}

// Update page content and handle specific actions based on the page
function updatePageContent(data, page, redirectUrl) {
	document.getElementById('content').innerHTML = data;

	// Add the redirect URL for login and register pages
	if ((page === '/accounts/login' || page === '/accounts/register') && redirectUrl !== '/')
		changeRedirectUrlandOauthState(redirectUrl);
  var match = page.match(/^\/tournament\/(\d+)\/lobby$/);
  if (match) {
    console.log("URL matched websocket");
    var tournament_id = match[1];
    openWebSocket(tournament_id);
  }
  var solo_match = page.match(/^\/tournament\/(\d+)\/solo_game$/);
  if (solo_match) {
		console.log('here open solo game');
    openWebSocket(100, 'solo');
  }
	// if (/^\/tournament\/\d+\/lobby$/.test(page)) { // Perform countdown in tournament lobby if the list is full. Otherwise, wait for other players.
	// 	if (document.querySelector('.full')) {
	// 		if (!document.querySelector('.winner')) {
	// 			tournamentLobbyCountdown();
	// 		}
	// 	}
	// }
}


// Change the redirect url in the form and the state of the oauth
function changeRedirectUrlandOauthState(redirectUrl) {
  // Change the redirect url in the form
  document.getElementById("redirectUrl").value = redirectUrl;

  // Change the state of the oauth according to the redirect url
  const login42UrlElement = document.getElementById("login-42-url");

  const updatedLogin42Url = new URL(login42UrlElement.href);
   // Extract the current port number from the window.location object
  const currentPort = window.location.port;

  // Construct the new state parameter with the current port
  const newStateParam = `qwerty|${encodeURIComponent(`https://localhost:${currentPort}${redirectUrl}`)}`;
  updatedLogin42Url.searchParams.set("state", newStateParam);

  login42UrlElement.href = updatedLogin42Url.toString();
}

window.navigate = navigate;
// export { loadPage };
