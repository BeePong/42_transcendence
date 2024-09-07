import { updateNavBar } from "../js/navbar";

global.fetch = jest.fn();

describe("updateNavBar", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();

    // Mock DOM element
    document.body.innerHTML = `
      <div id="navbar-user-actions"></div>
    `;
  });

  test("should update the navbar content when fetch is successful", async () => {
    // Mock successful fetch response
    const mockResponseData = "<nav>Navbar Content</nav>";
    fetch.mockResolvedValueOnce({
      ok: true,
      text: jest.fn().mockResolvedValueOnce(mockResponseData),
    });

    // Call the function
    await updateNavBar();

    expect(fetch).toHaveBeenCalledWith("/page/navbar/");

    const navbarElement = document.getElementById("navbar-user-actions");
    expect(navbarElement.innerHTML).toBe(mockResponseData);
  });

  test("should log an error when fetch fails", async () => {
    // Mock failed fetch response
    const mockError = new Error("Network response was not ok");
    fetch.mockResolvedValueOnce({
      ok: false,
      text: jest.fn(),
    });

    // Spy on console.error to check if the error is logged
    const consoleSpy = jest.spyOn(console, "error").mockImplementation();

    // Call the function
    await updateNavBar();

    expect(fetch).toHaveBeenCalledWith("/page/navbar/");

    expect(consoleSpy).toHaveBeenCalledWith(
      "There was a problem with the fetch operation:",
      mockError
    );

    // Clean up the console.error mock
    consoleSpy.mockRestore();
  });
});
