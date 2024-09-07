import { updateNavBar } from "../js/navbar";
import { loadPage } from "../js/route";

jest.mock("../js/navbar");
jest.mock("../js/route");

describe("Initial Page Load and Navigation Events", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();

    // Simulate adding the event listener in DOMContentLoaded and popstate
    require('../js/main');
  });

  test("should call updateNavBar and loadPage on DOMContentLoaded", () => {
    // Simulate the DOMContentLoaded event after the event listener has been set up
    const event = new Event("DOMContentLoaded");
    document.dispatchEvent(event);

    expect(updateNavBar).toHaveBeenCalledTimes(1);

    expect(loadPage).toHaveBeenCalledWith(
      window.location.pathname,
      "/",
      false,
      window.location.search
    );
  });

  test("should call loadPage on popstate event", () => {
    // Simulate the popstate event after the listener has been set up
    const popStateEvent = new PopStateEvent("popstate");
    window.dispatchEvent(popStateEvent);

    expect(loadPage).toHaveBeenCalledWith(
      window.location.pathname
    );
  });
});