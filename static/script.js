function createUser() {
    console.log("We're gonna make a user");
    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("usernameBox").value;
    const password = document.getElementById("passwordBox").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/register", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        console.log(data);
    }
}

function login() {
    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("usernameBox").value;
    const password = document.getElementById("passwordBox").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/login", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        const data = JSON.parse(this.responseText);
        console.log(data);
    }
}