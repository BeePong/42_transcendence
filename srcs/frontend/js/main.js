import { updateNavBar } from "./navbar.js";
import { loadPage } from "./route.js";

// Initial page load
document.addEventListener("DOMContentLoaded", () => {
  updateNavBar();
  loadPage(window.location.pathname, "/", false, window.location.search);
});

// Listen to popstate events for back/forward navigation
window.addEventListener("popstate", () => {
  loadPage(window.location.pathname);
});
