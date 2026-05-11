function createUser(event) {
    event.preventDefault();

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

        if (this.status === 201) {
            document.getElementById("signupForm").reset();
            window.location.href = "/login";
        }
    }
}

function handleLogin(event) {
    event.preventDefault();

    const xhttp = new XMLHttpRequest();
    const username = document.getElementById("usernameBox").value;
    const password = document.getElementById("passwordBox").value;
    const body = {"username": username, "password": password};
    xhttp.open("POST", "/login", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.send(JSON.stringify(body));
    xhttp.onload = function() {
        //const data = JSON.parse(this.responseText);
        //console.log(data);
        console.log("Raw response:", this.responseText);  // add this

        console.log("Status: ", this.status);
        //console.log("Responsse: ", this.data);


        if (this.status === 200) {
            window.location.href = "/";
        } else {
            alert(this.responseText);
        }
    }

    
}