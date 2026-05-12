function loadLeaderboard() {
    const selectedGame = document.getElementById("gameSelect").value;
    const tableBody = document.getElementById("leaderboardBody");
    tableBody.innerHTML = "<tr><td colspan='4'>Loading...</td></tr>";

    const xhttp = new XMLHttpRequest();
    xhttp.open("GET", `/api/leaderboard?game=${encodeURIComponent(selectedGame)}`, true);
    xhttp.send();

    xhttp.onload = function() {
        const players = JSON.parse(this.responseText);
        tableBody.innerHTML = "";

        if (players.length === 0) {
            tableBody.innerHTML = "<tr><td colspan='4'>No players yet</td></tr>";
            return;
        }

        for (let i = 0; i < players.length; i++) {
            let row = document.createElement("tr");
            let crown = "";

            if (i === 0) {
                row.className = "top-player";
                crown = '<img src="static/crown.png" class="crown-icon" alt="crown">';
            }

            row.innerHTML = `
                <td>${i + 1}</td>
                <td>${players[i].name} ${crown}</td>
                <td>${players[i].game}</td>
                <td>${players[i].wins}</td>
            `;
            tableBody.appendChild(row);
        }
    };
}