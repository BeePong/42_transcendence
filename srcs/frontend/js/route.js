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

// Load content based on the path
async function loadPage(path) {
	console.log("loadPage:", path);
	const page = path === '/' ? '/home' : path.replace(/\/$/, '');
	try {
			const response = await fetch(`/page${page}/`);
			if (!response.ok) {
					if (response.status !== 404)
							throw new Error('Network response was not ok');
			}
			const data = await response.text();
			document.getElementById('content').innerHTML = data;
			AuthLogin();
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}

// Load navbar
async function loadNavBar() {
	try {
			const response = await fetch('/page/navbar/');
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
	loadNavBar();
	loadPage(window.location.pathname);
});

/* window.onload = function() {
    const contentHtml = document.getElementById('content');
	console.log("CONTENT:", contentHtml.innerHTML);
	AuthLogin();
}; */

async function authNavigate(authUrl) {
	fetch(`/page${authUrl}`, {
		method: 'POST',
		credentials: 'same-origin',
		headers: {
			"Accept": "application/json",
			"X-Requested-With": "XMLHttpRequest",
			"X-CSRFToken": getCookie("csrftoken"),
		},
	}).then(response => response.json())
	.then(data => {
		console.log(data);
	});
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

function redirAuthPage() {
    const params = {
        'client_id': 'your_client_id',
        'redirect_uri': 'https://localhost/home',
        'response_type': 'code',
        'scope': 'public',
        'state': 'qwerty',
    };
    const base_url = 'https://api.intra.42.fr/oauth/authorize?';
    const query_string = new URLSearchParams(params).toString();
    const url = base_url + query_string;
    window.location.href = url;
}

function AuthLogin() {
    const params = {
        'client_id': "u-s4t2ud-9829b259f513f68a8560685f649592ce78967cbbf74808fc41d7921213795d41",
        'redirect_uri': "https://localhost/page/accounts/oauth_token/",
        'response_type': "code",
        'scope': "public",
        'state': "qwerty",
    };
    const base_url = 'https://api.intra.42.fr/oauth/authorize?';
    const query_string = new URLSearchParams(params).toString();
    const url = base_url + query_string;
    document.getElementById('42_login_button_id').innerHTML = `<a href="${url}">42Login</a>`;
}




// document.getElementById('42_login_button_id').addEventListener('click', redirectToAuthorizationPage);