//handle form submit for register, login and logout
async function handleFormSubmit(event) {
	event.preventDefault();
	const form = event.target;
	const formData = new FormData(form);

	// Ensure players field is included and not null
	if (!formData.has('players')) {
		formData.append('players', JSON.stringify([]));
	}

	const data = new URLSearchParams();
	formData.forEach((value, key) => {
		data.append(key, value);
	});

	const url = new URL(form.action);
	const relativePath = url.pathname + url.search;

	console.log('Submitting form to:', `/form${relativePath}`);
	console.log('Form data:', data.toString());

	try {
		const response = await fetch(`/form${relativePath}`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: data.toString()
		});

		console.log('Response status:', response.status);
		console.log('Response status text:', response.statusText);

		if (!response.ok) {
			const errorText = await response.text();
			console.error('Error response text:', errorText);
			throw new Error('Network response was not ok');
		}

		const result = await response.json();
		console.log('Response JSON:', result);

		if (result.success) {
			navigate(result.redirect);
			loadNavBar();
		} else {
			const errorContainer = document.querySelector('.form-error-message');
			// Clear any previous errors
			errorContainer.innerHTML = '';

			// Display the error message(s)
			if (result.errors) {
				// Show the error container
				errorContainer.style.display = 'block';

				// Iterate through the errors object to display each error message
				for (const key in result.errors) {
					if (result.errors.hasOwnProperty(key)) {
						result.errors[key].forEach(error => {
							const errorElement = document.createElement('p');
							errorElement.textContent = error;
							errorContainer.appendChild(errorElement);
						});
					}
				}
			}
		}
	} catch (error) {
		console.error('There was a problem with the fetch operation:', error);
	}
}