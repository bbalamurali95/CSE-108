function createUser() {
    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("").value;
    const password = document.getElementById("").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/register", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        register();
    }
}