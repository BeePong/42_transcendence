// Load navbar
export async function loadNavBar() {
	try {
			const response = await fetch('/page/navbar/');
			if (!response.ok)
				throw new Error('Network response was not ok');

			const data = await response.text();
			document.getElementById('navbar-content').innerHTML = data;
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}