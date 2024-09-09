import { openWebSocket } from "./websockets.js";
import { tournamentLobbyCountdown } from "./tournament.js";

const allowedRoutes = [
  "/home",
  "/about",
  "/accounts/login",
  "/accounts/register",
  "/tournament",
  "/tournament/create",
  "/accounts/oauth_error",
];

const tournamentLobbyPattern = /^\/tournament\/\d+\/lobby$/;
const soloGamePattern = /^\/tournament\/\d+\/solo_game$/;

// Handle navigation based on path or event
function navigate(eventOrPath, redirectUrl = "/") {
  console.log("navigate");
  console.log("navigate window.location.pathname: ", window.location.pathname);
  const path =
    typeof eventOrPath === "string"
      ? eventOrPath
      : (eventOrPath.preventDefault(),
        eventOrPath.currentTarget.getAttribute("href"));
  console.log("navigate path: ", path);
  if (window.location.pathname !== path) {
    const match = window.location.pathname.match(
      /^\/tournament\/(\d+)\/lobby\/?$/
    );
    console.log("navigate match: ", match);
    if (match) {
      console.log("URL matched websocket");
      const event = new CustomEvent("navigateAwayFromTournamentLobby");
      window.dispatchEvent(event);
    }
    loadPage(path, redirectUrl, true);
  }
}

// Load content based on the path
export async function loadPage(
  path,
  redirectUrl = "/",
  fromNavigate = false,
  queryString = "",
  fromWebsocket = false
) {
  // If the path is '/', set page to '/home'.
  // Otherwise, remove the trailing slash from the path and set page to the resulting string.
  const page = path === "/" ? "/home" : path.replace(/\/$/, "");
  const isAllowed =
    allowedRoutes.includes(page) ||
    tournamentLobbyPattern.test(page) ||
    soloGamePattern.test(page);
  try {
    let response;
    if (isAllowed) response = await fetch(`/page${page}/${queryString}`);
    else response = await fetch("/page/custom_404/");

    if (!response.ok && response.status !== 404) {
      if (
        response.status === 400 ||
        response.status === 401 ||
        response.status === 302
      ) {
        if (response.status === 302) {
          const data = await response.json();
          return navigate(data.redirect);
        } else if (response.status === 400)
          return loadPage("/accounts/oauth_error/");
        // Handle oauth error response by fetching the error page
        else return navigate("/accounts/login/", redirectUrl); // Redirect to login page if the user is not authenticated
      } else {
        throw new Error("Network response was not ok");
      }
    }
    if (fromNavigate === true)
      // If this function is called by navigate(), update the browser's history to the new path without reloading the page
      history.pushState(null, null, path);

    const data = await response.text();
    updatePageContent(data, page, redirectUrl, fromWebsocket); // Handle content updates
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// Update page content and handle specific actions based on the page
function updatePageContent(data, page, redirectUrl, fromWebsocket) {
  document.getElementById("content").innerHTML = data;

  // Add the redirect URL for login and register pages
  if (
    (page === "/accounts/login" || page === "/accounts/register") &&
    redirectUrl !== "/"
  )
    changeRedirectUrlandOauthState(redirectUrl);
  if (!fromWebsocket) {
    console.log("open websocket function");
    var match = page.match(/^\/tournament\/(\d+)\/lobby$/);
    if (match) {
      console.log("URL matched websocket");
      var tournament_id = match[1];
      openWebSocket(tournament_id);
    }
    var solo_match = page.match(/^\/tournament\/(\d+)\/solo_game$/);
    if (solo_match) {
      console.log("here open solo game");
      var tournament_id = solo_match[1];
      openWebSocket(tournament_id, "solo");
    }
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
  const newStateParam = `qwerty|${encodeURIComponent(
    `https://localhost:${currentPort}${redirectUrl}`
  )}`;
  updatedLogin42Url.searchParams.set("state", newStateParam);

  login42UrlElement.href = updatedLogin42Url.toString();
}

window.navigate = navigate;
// export { loadPage };
