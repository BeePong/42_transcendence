// Handle navigation based on path or event 
function navigate(eventOrPath, redirectUrl = '/') {
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
async function loadPage(path, redirectUrl = '/', fromNavigate = false) {
	// If the path is '/', set page to '/home'.
	// Otherwise, remove the trailing slash from the path and set page to the resulting string.
	const page = path === '/' ? '/home' : path.replace(/\/$/, '');
	try {
			const response = await fetch(`/page${page}/`);

			if (!response.ok) {
					if (!(response.status === 401 || response.status === 404))
							throw new Error('Network response was not ok');
			}

			// If the navigation was triggered programmatically (fromNavigate is true) and the response status is not 401 (unauthorized),
			// update the browser's history to the new path without reloading the page.
			if (fromNavigate === true && response.status !== 401)
				history.pushState(null, null, path);

			// Redirect to login page if the user is not login
			if (response.status === 401) {
				const data = await response.json();
				if (data.authenticated === false) {
					redirectToLoginPage(redirectUrl);
				}
			}
			else {
				const data = await response.text();
				document.getElementById('content').innerHTML = data;

				// Add the redirect url for login and register page 
				if (page === '/accounts/login' || page === '/accounts/register')
					document.getElementById('redirectUrl').value = redirectUrl;

				//perform countdown in tournmament lobby
				// const regex = /^\/tournament\/\d+\/lobby$/;
				// if (regex.test(page))
				// 	tournamentLobbyCountDown();
			}
	} catch (error) {
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
		document.getElementById('redirectUrl').value = redirectUrl;
	}
	catch (error) {
		console.error('There was a problem with the fetch operation:', error);
	}
}

// Countdown in lobby page and navigate to the game page after countdown
function tournamentLobbyCountDown() {
	let countdownValue = 3;
	const countdownElement = document.getElementById('countdown');

	const countdownInterval = setInterval(() => {
			if (countdownValue > 1) {
					countdownValue--;
					countdownElement.textContent = `${countdownValue}`;
			} else {
					clearInterval(countdownInterval);
					navigate('/game');
			}
	}, 1000);
}

// Load navbar
async function loadNavBar() {
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
	loadPage(window.location.pathname);
});