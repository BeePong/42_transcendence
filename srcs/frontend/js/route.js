import { openWebSocket } from "./websockets.js";

// Handle navigation based on path or event
window.navigate = function navigate(eventOrPath, redirectUrl = "/") {
  let path;
  if (typeof eventOrPath === "string") path = eventOrPath;
  else {
    eventOrPath.preventDefault();
    path = eventOrPath.currentTarget.getAttribute("href");
  }

  // Do not render again for the same path
  if (window.location.pathname === path) return;

  loadPage(path, redirectUrl, true);
};

// Load content based on the path, and add the redirect url for login and register page
async function loadPage(
  path,
  redirectUrl = "/",
  fromNavigate = false,
  queryString = ""
) {
  // If the path is '/', set page to '/home'.
  // Otherwise, remove the trailing slash from the path and set page to the resulting string.
  const page = path === "/" ? "/home" : path.replace(/\/$/, "");
  try {
    const response = await fetch(`/page${page}/${queryString}`);

    if (!response.ok) {
      if (
        !(
          response.status === 400 ||
          response.status === 401 ||
          response.status === 404
        )
      )
        throw new Error("Network response was not ok");
    }

    // If the navigation was triggered programmatically (fromNavigate is true) and the response status is not 401 (unauthorized),
    // update the browser's history to the new path without reloading the page.
    if (
      fromNavigate === true &&
      response.status !== 400 &&
      response.status !== 401
    )
      history.pushState(null, null, path);

    // Handle 42 authorization error by fetching the error page
    if (page === "/accounts/oauth_error" && response.status === 400)
      fetchOauthErrorPage();
    // Redirect to login page if the user is not login
    else if (response.status === 401) {
      const data = await response.json();
      if (data.authenticated === false) {
        redirectToLoginPage(redirectUrl);
      }
    } else {
      const data = await response.text();
      document.getElementById("content").innerHTML = data;

      // Add the redirect url for login and register page
      if (
        (page === "/accounts/login" || page === "/accounts/register") &&
        redirectUrl !== "/"
      )
        changeRedirectUrlandOauthState(redirectUrl);

      // perform countdown in tournmament lobby if the list is full. Otherwise, wait for other players.
      // if (/^\/tournament\/\d+\/lobby$/.test(page)) {
      //   if (document.querySelector(".full")) {
      //     if (!document.querySelector(".winner")) tournamentLobbyCountdown();
      //   } else mockWebSocket(); //TODO: open websocket
      // }

      // if url contains "lobby", start mockWebSocket
      var match = page.match(/^\/tournament\/(\d+)\/lobby$/);
      console.log("URL matched websocket");
      if (match) {
        var tournament_id = match[1];
        openWebSocket(tournament_id);
      }
      var solo_match = page.match(/^\/tournament\/solo_game$/);
      console.log("solo_game match", solo_match);
      if (solo_match) {
        openWebSocket("solo");
      }
    }
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// Fetching the error page for 42 authorization error
async function fetchOauthErrorPage() {
  try {
    const response = await fetch("/page/accounts/oauth_error/");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.text();
    document.getElementById("content").innerHTML = data;
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// redirect to login page
async function redirectToLoginPage(redirectUrl) {
  // update the browser's history to the login path
  history.pushState(null, null, "/accounts/login");

  try {
    const response = await fetch("/page/accounts/login/");
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    const data = await response.text();
    document.getElementById("content").innerHTML = data;

    changeRedirectUrlandOauthState(redirectUrl);
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// Change the redirect url in the form and the state of the oauth
function changeRedirectUrlandOauthState(redirectUrl) {
  // Change the redirect url in the form
  document.getElementById("redirectUrl").value = redirectUrl;

  // Change the state of the oauth according to the redirect url
  const login42UrlElement = document.getElementById("login-42-url");

  const updatedLogin42Url = new URL(login42UrlElement.href);
  const newStateParam = `qwerty|${encodeURIComponent(
    `https://localhost${redirectUrl}`
  )}`;
  updatedLogin42Url.searchParams.set("state", newStateParam);

  login42UrlElement.href = updatedLogin42Url.toString();
}

// Handle full tournament lobby
function handleFullTournamentLobby() {
  setTimeout(() => {
    if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
      document.getElementById("tournament-lobby-section").classList.add("full");
      document.querySelector(".tournament_lobby__header").innerHTML =
        'BEEPONG CUP IS STARTING IN <span id="countdown">3</span>...';
      document.querySelector(".tournament_lobby__description").textContent =
        "dummy vs dummy";
      document.querySelector(".tournament_lobby__player-count").remove();
      document.getElementById("leave-button").remove();
      tournamentLobbyCountdown();
    }
  }, 1000);
}

// Countdown in lobby page and navigate to the game page after countdown
function tournamentLobbyCountdown() {
  let countdownValue = 3;
  const countdownElement = document.getElementById("countdown");

  setTimeout(() => {
    const countdownInterval = setInterval(() => {
      if (/^\/tournament\/\d+\/lobby$/.test(window.location.pathname)) {
        if (countdownValue > 1) {
          countdownValue--;
          countdownElement.textContent = `${countdownValue}`;
        } else {
          clearInterval(countdownInterval);
          navigate("/game");
        }
      } else clearInterval(countdownInterval);
    }, 1000);
  }, 500);
}

export { loadPage };
