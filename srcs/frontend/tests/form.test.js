import {
  handleFormSubmit,
  submitForm,
  getFormDataAsUrlEncoded,
  displayFormErrors,
} from "../js/form";

jest.mock("../js/navbar", () => ({
  updateNavBar: jest.fn(),
}));

// Mock navigate function for redirection
const navigate = jest.fn();
global.navigate = navigate;

global.fetch = jest.fn();

describe("Form Submission Functions", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    document.body.innerHTML = `
      <form action="/test/submit" id="test-form">
        <input type="text" name="username" value="testuser" />
        <input type="password" name="password" value="secret" />
      </form>
      <div class="form__error-message"></div>
    `;
  });

  describe("handleFormSubmit", () => {
    test("should prevent default form submission and call submitForm", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("test-form"),
      };

      // Mock successful fetch response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce({
          success: true,
          redirect: "/redirect/path",
        }),
      });

      await handleFormSubmit(mockEvent);

      expect(mockEvent.preventDefault).toHaveBeenCalled();
      expect(fetch).toHaveBeenCalledWith("/form/test/submit", expect.any(Object));
      expect(navigate).toHaveBeenCalledWith("/redirect/path");
    });

    test("should display form errors when response is not successful", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("test-form"),
      };

      // Mock failed fetch response
      fetch.mockResolvedValueOnce({
        ok: true,
        json: jest.fn().mockResolvedValueOnce({
          success: false,
          errors: {
            username: ["Username is required"],
            password: ["Password is too short"],
          },
        }),
      });

      await handleFormSubmit(mockEvent);

      const errorContainer = document.querySelector(".form__error-message");
      expect(errorContainer.style.display).toBe("flex");
      expect(errorContainer.textContent).toContain("Username is required");
      expect(errorContainer.textContent).toContain("Password is too short");
    });

    test("should log an error when fetch fails", async () => {
      const mockEvent = {
        preventDefault: jest.fn(),
        target: document.getElementById("test-form"),
      };

      const consoleSpy = jest.spyOn(console, "error").mockImplementation();

      // Mock failed fetch
      fetch.mockRejectedValueOnce(new Error("Fetch failed"));

      await handleFormSubmit(mockEvent);

      expect(consoleSpy).toHaveBeenCalledWith(
        "There was a problem with the fetch operation:",
        expect.any(Error)
      );

      consoleSpy.mockRestore();
    });
  });

  describe("submitForm", () => {
    test("should send a form submission via fetch", async () => {
      const form = document.getElementById("test-form");
      const url = new URL("/test/submit", "http://localhost");

      // Mock fetch response
      fetch.mockResolvedValueOnce({ ok: true });

      const response = await submitForm(form, url);

      expect(fetch).toHaveBeenCalledWith("/form/test/submit", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: "username=testuser&password=secret",
      });

      expect(response.ok).toBe(true);
    });
  });

  describe("getFormDataAsUrlEncoded", () => {
    test("should convert form data to URL-encoded format", () => {
      const form = document.getElementById("test-form");
      const urlEncodedData = getFormDataAsUrlEncoded(form);

      expect(urlEncodedData.toString()).toBe("username=testuser&password=secret");
    });
  });

  describe("displayFormErrors", () => {
    test("should display error messages in the form", () => {
      const errors = {
        username: ["Username is required"],
        password: ["Password is too short"],
      };

      displayFormErrors(errors);

      const errorContainer = document.querySelector(".form__error-message");
      expect(errorContainer.style.display).toBe("flex");
      expect(errorContainer.textContent).toContain("Username is required");
      expect(errorContainer.textContent).toContain("Password is too short");
    });

    test("should clear previous error messages", () => {
      const errorContainer = document.querySelector(".form__error-message");
      errorContainer.innerHTML = "<p>Old error message</p>";

      displayFormErrors({});

      expect(errorContainer.innerHTML).toBe("");
    });
  });
});
