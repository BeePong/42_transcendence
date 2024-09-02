import { mockWebSocket } from "./tournament.js";
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
							return loadPage('/accounts/oauth_error'); // Handle oauth error response by fetching the error page
						else
							return navigate('/accounts/login', redirectUrl); // Redirect to login page if the user is not authenticated	
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
	else if (/^\/tournament\/\d+\/lobby$/.test(page)) { // Perform countdown in tournament lobby if the list is full. Otherwise, wait for other players.
		if (document.querySelector('.full')) {
			if (!document.querySelector('.winner')) {
				tournamentLobbyCountdown();
			}
		} else {
			mockWebSocket(); // TODO: open websocket
		}
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

// Attach navigate to the global window object for use in inline event handlers
window.navigate = navigate;