import { updateNavBar } from "./navbar.js";

// Handle form submission
async function handleFormSubmit(event) {
  event.preventDefault();

  const form = event.target;
  const url = new URL(form.action);

  try {
    const response = await submitForm(form, url);

    if (!response.ok) {
      if (response.status !== 400)
        throw new Error("Network response was not ok");
    }

    const result = await response.json();

    if (result.success) {
      // Handle redirection
      navigate(result.redirect);
      if (url.pathname.startsWith("/accounts/")) updateNavBar();
    } else {
      // Display error messages
      displayFormErrors(result.errors);
    }
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}

// Submit the form and return the response
async function submitForm(form, url) {
  const urlEncodedData = getFormDataAsUrlEncoded(form);
  return await fetch(`/form${url.pathname}`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: urlEncodedData.toString(),
  });
}

// Extract data from a form and convert it to URL-encoded format
function getFormDataAsUrlEncoded(form) {
  const formData = new FormData(form);
  const urlEncodedData = new URLSearchParams();

  formData.forEach((value, key) => {
    // Append each key-value pair in the FormData object to the URLSearchParams object
    urlEncodedData.append(key, value);
  });

  return urlEncodedData;
}

// Display error messages in the form
function displayFormErrors(errors) {
  const errorContainer = document.querySelector(".form__error-message");
  errorContainer.innerHTML = ""; // Clear previous errors

  if (errors) {
    errorContainer.style.display = "flex"; // Show the error container

    for (const key in errors) {
      if (errors.hasOwnProperty(key)) {
        errors[key].forEach((error) => {
          const errorElement = document.createElement("p");
          errorElement.textContent = error;
          errorContainer.appendChild(errorElement);
        });
      }
    }
  }
}

// Attach handleFormSubmit to the global window object for use in inline event handlers
window.handleFormSubmit = handleFormSubmit;
