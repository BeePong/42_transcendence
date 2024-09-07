import { updateNavBar } from "./navbar.js";
import { loadPage } from "./route.js";

// Initial page load
document.addEventListener("DOMContentLoaded", () => {
  updateNavBar();
  loadPage(window.location.pathname, "/", false, window.location.search);
});

// Listen to popstate events for back/forward navigation
window.addEventListener("popstate", () => {
  const match = window.location.pathname.match(
    /^\/tournament\/(\d+)\/lobby\/?$/
  );
  if (match) {
    const event = new CustomEvent("navigateAwayFromTournamentLobby");
    window.dispatchEvent(event);
  }
  // TODO: add custom navigation event here, which will be listened to in websocket as well
  loadPage(window.location.pathname);
});
