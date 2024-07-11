 // Define routes
 const routes = {
	'/': 'home',
	'/home': 'home',
	'/about': 'about',
	'/accounts/register': 'accounts/register',
	'/accounts/login' : 'accounts/login'
};

// Handle navigation
function navigate(eventOrPath) {
	let path;
	if (typeof eventOrPath === 'string') {
			path = eventOrPath;
	} else {
			eventOrPath.preventDefault();
			path = eventOrPath.target.getAttribute('href');
	}

	if (window.location.pathname === path)
			return;

	history.pushState(null, null, path);
	loadPage(path);
}

// Load content based on the route
async function loadPage(route) {
	let path = route.endsWith('/') && route !== '/' ? route.slice(0, -1) : route;
	const page = routes[path] || window.location.pathname.slice(1);
	try {
			const response = await fetch(`/page/${page}/`);
			if (!response.ok) {
					if (response.status !== 404)
							throw new Error('Network response was not ok');
			}
			const data = await response.text();
			document.getElementById('content').innerHTML = data;
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}

// Load navbar
async function loadNavBar() {
	try {
			const response = await fetch(`/page/navbar/`);
			if (!response.ok) {
				throw new Error('Network response was not ok');
			}
			const data = await response.text();
			document.getElementById('navbar').innerHTML = data;
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
	loadPage(window.location.pathname);
	loadNavBar();
});