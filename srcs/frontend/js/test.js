async function fetchTestData() {
	const response = await fetch('/api/');
	const data = await response.text(); // or response.json() if the API returns JSON
	document.getElementById('test').innerHTML = data;
}