import { loadNavBar } from "./route.js";

//handle form submit for register, login and logout
window.handleFormSubmit = async function handleFormSubmit(event) {
  event.preventDefault();
  const form = event.target;
  // Create a FormData object from the form element, which captures all form input values
  const formData = new FormData(form);

  // Initialize a URLSearchParams object to handle URL-encoded data
  const data = new URLSearchParams();
  // Iterate over each key-value pair in the FormData object
  // Append each key-value pair to the URLSearchParams object
  formData.forEach((value, key) => {
    data.append(key, value);
  });

  // Create a new URL object from the form's action attribute, which provides the URL for form submission
  const url = new URL(form.action);
  // Combine the URL's pathname (the path part of the URL) with its search parameters (query string)
  // This results in the relative path of the form's action URL, including any query parameters
  const relativePath = url.pathname + url.search;

  try {
    const response = await fetch(`/form${relativePath}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: data.toString(),
    });

    if (!response.ok) {
      if (response.status !== 400)
        throw new Error("Network response was not ok");
    }

    const result = await response.json();

    if (result.success) {
      // Handle redirection
      if (relativePath === "/accounts/logout/") navigate("/");
      else navigate(result.redirect);
      loadNavBar();
    } else {
      const errorContainer = document.querySelector(".form-error-message");
      // Clear any previous errors
      errorContainer.innerHTML = "";

      // Display the error message(s)
      if (result.errors) {
        // Show the error container
        errorContainer.style.display = "block";

        // Iterate through the errors object to display each error message
        for (const key in result.errors) {
          if (result.errors.hasOwnProperty(key)) {
            result.errors[key].forEach((error) => {
              const errorElement = document.createElement("p");
              errorElement.textContent = error;
              errorContainer.appendChild(errorElement);
            });
          }
        }
      }
    }
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
};
