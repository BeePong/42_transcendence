// Load navbar
export async function updateNavBar() {
<<<<<<< HEAD
	try {
			const response = await fetch('/page/navbar/');
			if (!response.ok)
				throw new Error('Network response was not ok');

			const data = await response.text();
			document.getElementById('navbar-user-actions').innerHTML = data;
	} catch (error) {
			console.error('There was a problem with the fetch operation:', error);
	}
}
=======
  try {
    const response = await fetch("/page/navbar/");
    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.text();
    document.getElementById("navbar-user-actions").innerHTML = data;
  } catch (error) {
    console.error("There was a problem with the fetch operation:", error);
  }
}
>>>>>>> 010-server-side-pong
