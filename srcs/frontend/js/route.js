import { mockWebSocket } from "./tournament.js";
import { tournamentLobbyCountdown } from "./tournament.js";

// Handle navigation based on path or event 
function navigate(eventOrPath, redirectUrl = '/') {
	let path;
	if (typeof eventOrPath === 'string')
			path = eventOrPath;
	else {
			eventOrPath.preventDefault();
			path = eventOrPath.currentTarget.getAttribute('href');
	}

	if (window.location.pathname === path) // Do not render again for the same path
			return;

	loadPage(path, redirectUrl, true);
}

// Load content based on the path
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

			// If this function is called by navigate() and the response status is not 400 or 401,
			// update the browser's history to the new path without reloading the page.
			if (fromNavigate === true && response.status !== 400 && response.status !== 401)
				history.pushState(null, null, path);

			if (page === '/accounts/oauth_error' && response.status === 400) // Handle oauth error response by fetching the error page
				loadPage('/accounts/oauth_error');
			else if (response.status === 401)  // Redirect to login page if the user is not authenticated
				navigate('/accounts/login', redirectUrl);
			else {
				const data = await response.text();
				updatePageContent(data, page, redirectUrl); // Handle content updates
			}
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

	// Perform countdown in tournament lobby if the list is full. Otherwise, wait for other players.
	if (/^\/tournament\/\d+\/lobby$/.test(page)) {
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

// Ensure `navigate` is accessible in the global scope
window.navigate = navigate;