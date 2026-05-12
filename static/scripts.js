let players = [
    { name: "John", game: "Tekken", wins: 8 },
    { name: "Ryan", game: "Guilty Gear", wins: 7 },
    { name: "Sam", game: "Street Fighter", wins: 6 },
    { name: "Kevin", game: "Tekken", wins: 5 },
    { name: "Alex", game: "Guilty Gear", wins: 5 },
    { name: "Daniel", game: "Street Fighter", wins: 4 },
    { name: "Jordan", game: "Tekken", wins: 4 },
    { name: "Chris", game: "Street Fighter", wins: 3 },
    { name: "Marcus", game: "Guilty Gear", wins: 3 },
    { name: "Leo", game: "Tekken", wins: 3 },
    { name: "Nate", game: "Street Fighter", wins: 2 },
    { name: "Evan", game: "Guilty Gear", wins: 2 },
    { name: "Victor", game: "Tekken", wins: 2 },
    { name: "Adrian", game: "Street Fighter", wins: 2 },
    { name: "Noah", game: "Tekken", wins: 2 },
    { name: "Eli", game: "Guilty Gear", wins: 2 },
    { name: "Omar", game: "Street Fighter", wins: 1 },
    { name: "Jay", game: "Guilty Gear", wins: 1 },
    { name: "Mason", game: "Tekken", wins: 1 },
    { name: "Luis", game: "Street Fighter", wins: 1 },
    { name: "Tyler", game: "Tekken", wins: 1 },
    { name: "Brandon", game: "Guilty Gear", wins: 1 },
    { name: "Eric", game: "Street Fighter", wins: 0 },
    { name: "Sean", game: "Tekken", wins: 0 }
];

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