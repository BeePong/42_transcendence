//handle form submit for register, login and logout
async function handleFormSubmit(event) {
	event.preventDefault();
	const form = event.target;
	const formData = new FormData(form);

	const data = new URLSearchParams();
	formData.forEach((value, key) => {
		data.append(key, value);
	});

	const url = new URL(form.action);
	const relativePath = url.pathname + url.search;

	try {
		const response = await fetch(`/form${relativePath}`, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/x-www-form-urlencoded'
				},
				body: data.toString()
		});

		if (!response.ok) {
				throw new Error('Network response was not ok');
		}

		const result = await response.json();

		if (result.success) {
				navigate('/home');
				loadNavBar();
		} else {
				console.error('Form submission error:', result.errors);
		}
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}