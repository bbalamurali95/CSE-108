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
            crown = '<img src="img/crown.png" class="crown-icon" alt="crown">';
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

function showBracket(game) {
    let bracketArea = document.getElementById("bracketArea");
    let title = "";
    let p = [];

    if (game == "street") {
        title = "Street Fighter Bracket";
        p = ["Sam", "Daniel", "Chris", "Nate", "Omar", "Adrian", "Luis", "Eric", "John", "Alex", "Jordan", "Kevin", "Ryan", "Marcus", "Leo", "Victor"];
    }

    if (game == "tekken") {
        title = "Tekken Bracket";
        p = ["John", "Kevin", "Jordan", "Leo", "Victor", "Mason", "Noah", "Tyler", "Sam", "Alex", "Ryan", "Chris", "Daniel", "Marcus", "Nate", "Omar"];
    }

    if (game == "guilty") {
        title = "Guilty Gear Bracket";
        p = ["Ryan", "Alex", "Marcus", "Evan", "Jay", "Eli", "Brandon", "Chris", "John", "Sam", "Kevin", "Jordan", "Daniel", "Leo", "Nate", "Victor"];
    }

    bracketArea.innerHTML = `
        <h2>${title}</h2>
        <div class="bracket-board">
            <h3 class="bracket-title">Upper Bracket</h3>

            <div class="grid-bracket upper-grid">
                <h4 class="round-label col1-label">Round 1</h4>
                <h4 class="round-label col2-label">Round 2</h4>
                <h4 class="round-label col3-label">Semifinals</h4>
                <h4 class="round-label col4-label">Upper Final</h4>
                <h4 class="round-label col5-label">Grand Finals</h4>

                <div class="bracket-match u-r1-m1"><div>${p[0]}</div><div>${p[1]}</div></div>
                <div class="bracket-match u-r1-m2"><div>${p[2]}</div><div>${p[3]}</div></div>
                <div class="bracket-match u-r1-m3"><div>${p[4]}</div><div>${p[5]}</div></div>
                <div class="bracket-match u-r1-m4"><div>${p[6]}</div><div>${p[7]}</div></div>
                <div class="bracket-match u-r1-m5"><div>${p[8]}</div><div>${p[9]}</div></div>
                <div class="bracket-match u-r1-m6"><div>${p[10]}</div><div>${p[11]}</div></div>
                <div class="bracket-match u-r1-m7"><div>${p[12]}</div><div>${p[13]}</div></div>
                <div class="bracket-match u-r1-m8"><div>${p[14]}</div><div>${p[15]}</div></div>

                <div class="bracket-match u-r2-m1"><div>${p[0]}</div><div>${p[2]}</div></div>
                <div class="bracket-match u-r2-m2"><div>${p[5]}</div><div>${p[6]}</div></div>
                <div class="bracket-match u-r2-m3"><div>${p[8]}</div><div>${p[10]}</div></div>
                <div class="bracket-match u-r2-m4"><div>${p[12]}</div><div>${p[14]}</div></div>

                <div class="bracket-match u-r3-m1"><div>${p[0]}</div><div>${p[5]}</div></div>
                <div class="bracket-match u-r3-m2"><div>${p[8]}</div><div>${p[12]}</div></div>

                <div class="bracket-match u-r4-m1"><div>${p[0]}</div><div>${p[8]}</div></div>
                <div class="bracket-match grand-match u-gf"><div>${p[0]}</div><div>${p[10]}</div></div>
                <div class="champion-box u-champion">Champion: ${p[0]}</div>
            </div>

            <div class="lower-bracket-area">
                <h3 class="bracket-title lower-title">Lower Bracket</h3>

                <div class="grid-bracket lower-grid">
                    <h4 class="round-label l-col1-label">Lower R1</h4>
                    <h4 class="round-label l-col2-label">Lower R2</h4>
                    <h4 class="round-label l-col3-label">Lower R3</h4>
                    <h4 class="round-label l-col4-label">Lower Semi</h4>
                    <h4 class="round-label l-col5-label">Lower Final</h4>

                    <div class="bracket-match lower-match l-r1-m1"><div>${p[1]}</div><div>${p[3]}</div></div>
                    <div class="bracket-match lower-match l-r1-m2"><div>${p[4]}</div><div>${p[7]}</div></div>
                    <div class="bracket-match lower-match l-r1-m3"><div>${p[9]}</div><div>${p[11]}</div></div>
                    <div class="bracket-match lower-match l-r1-m4"><div>${p[13]}</div><div>${p[15]}</div></div>

                    <div class="bracket-match lower-match l-r2-m1"><div>${p[3]}</div><div>${p[4]}</div></div>
                    <div class="bracket-match lower-match l-r2-m2"><div>${p[9]}</div><div>${p[13]}</div></div>
                    <div class="bracket-match lower-match l-r2-m3"><div>${p[2]}</div><div>${p[6]}</div></div>
                    <div class="bracket-match lower-match l-r2-m4"><div>${p[10]}</div><div>${p[14]}</div></div>

                    <div class="bracket-match lower-match l-r3-m1"><div>${p[4]}</div><div>${p[13]}</div></div>
                    <div class="bracket-match lower-match l-r3-m2"><div>${p[6]}</div><div>${p[10]}</div></div>

                    <div class="bracket-match lower-match l-r4-m1"><div>${p[13]}</div><div>${p[10]}</div></div>
                    <div class="bracket-match lower-match l-r5-m1"><div>${p[8]}</div><div>${p[10]}</div></div>
                </div>
            </div>
        </div>
    `;
}