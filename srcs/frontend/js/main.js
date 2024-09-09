import { updateNavBar } from "./navbar.js";
import { loadPage } from "./route.js";

// Initial page load
document.addEventListener("DOMContentLoaded", () => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("login") === "success")
    localStorage.setItem("isLoggedIn", "true");
  updateNavBar();
  loadPage(window.location.pathname, "/", false, window.location.search);
});

// Listen to popstate events for back/forward navigation
window.addEventListener("popstate", () => {
  const match = window.location.pathname.match(
    /^\/tournament\/(\d+)\/lobby\/?$/
  );
  const solo_match = window.location.pathname.match(
    /^\/tournament\/(\d+)\/solo_game\/?$/
  );
  if (match || solo_match) {
    const event = new CustomEvent("navigateAwayFromTournamentLobby");
    window.dispatchEvent(event);
  }
  // TODO: add custom navigation event here, which will be listened to in websocket as well
  loadPage(window.location.pathname);
});

// Force reload if the page is loaded from the cache
window.addEventListener("pageshow", function (event) {
  if (event.persisted) {
    updateNavBar();
    loadPage(window.location.pathname);
  }
});

// Listen for localStorage changes (for login/logout events across tabs)
window.addEventListener("storage", (event) => {
  // Check for login event
  if (event.key === "isLoggedIn" && event.newValue === "true") {
    updateNavBar();
    navigate("/tournament/");
  }

  // Check for logout event
  if (event.key === "isLoggedIn" && event.newValue === "false") {
    updateNavBar();
    navigate("/");
  }
});
