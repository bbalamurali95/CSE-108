function loadLeaderboard() {
    let selectedGame = document.getElementById("gameSelect").value;
    let tableBody = document.getElementById("leaderboardBody");
    tableBody.innerHTML = "";
    let filteredPlayers = [];

    for (let i = 0; i < players.length; i++) {
        if (selectedGame == "Overall" || players[i].game == selectedGame) {
            filteredPlayers.push(players[i]);
        }
    }

    filteredPlayers.sort(function(a, b) {
        return b.wins - a.wins;
    });

    for (let i = 0; i < filteredPlayers.length; i++) {
        let row = document.createElement("tr");
        let crown = "";

        if (i == 0) {
            row.className = "top-player";
            crown = '<img src="static/crown.png" class="crown-icon" alt="crown">';
        }

        row.innerHTML = `
            <td>${i + 1}</td>
            <td>${filteredPlayers[i].name} ${crown}</td>
            <td>${filteredPlayers[i].game}</td>
            <td>${filteredPlayers[i].wins}</td>
        `;

        tableBody.appendChild(row);
    }
}