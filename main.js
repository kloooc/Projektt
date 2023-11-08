// Czekaj, aż zawartość strony zostanie załadowana
document.addEventListener("DOMContentLoaded", function () {
    // Pobieranie elementów DOM
    var elapsedTime = document.querySelector("#elapsed");
    var homeTeamImage = document.querySelector("#homeLogo");
    var homeTeamName = document.querySelector("#homeName");
    var awayTeamImage = document.querySelector("#awayLogo");
    var awayTeamName = document.querySelector("#awayName");
    var lastMatchGoal = document.querySelector("#goals");
    var matchTable = document.querySelector("#matchTable");

    // Funkcja do tworzenia elementu meczu
    function addMatchTile(data) {
        // Tworzenie elementu div dla meczu
        var matchTile = document.createElement('div');
        matchTile.classList.add("match-tile");

        // Tworzenie sekcji drużyny gospodarzy
        var homeTeam = document.createElement('div');
        homeTeam.classList.add("team");
        // Tworzenie obrazka i tekstu
        var homeTileTeamName = document.createElement('p');
        homeTileTeamName.innerHTML = data['teams']['home']['name'];
        var homeTileTeamLogo = document.createElement('img');
        homeTileTeamLogo.src = data['teams']['home']['logo'];
        homeTeam.appendChild(homeTileTeamLogo);
        homeTeam.appendChild(homeTileTeamName);

        // Tworzenie sekcji drużyny gości
        var awayTeam = document.createElement('div');
        awayTeam.classList.add("team");
        // Tworzenie obrazka i tekstu
        var awayTileTeamName = document.createElement('p');
        awayTileTeamName.innerHTML = data['teams']['away']['name'];
        var awayTileTeamLogo = document.createElement('img');
        awayTileTeamLogo.src = data['teams']['away']['logo'];
        awayTeam.appendChild(awayTileTeamLogo);
        awayTeam.appendChild(awayTileTeamName);

        // Tworzenie wyniku
        var score = document.createElement('p');
        score.innerHTML = data['goals']['home'] + " - " + data['goals']['away'];

        // Dodawanie elementów do meczu
        matchTile.appendChild(homeTeam);
        matchTile.appendChild(score);
        matchTile.appendChild(awayTeam);

        matchTable.appendChild(matchTile);
    }

    // Pobieranie danych
    fetch("https://api-football-v1.p.rapidapi.com/fixtures/live", {
        "method": "GET",
        "headers": {
            "x-rapidapi-host": "api-football-v1.p.rapidapi.com",
            "x-rapidapi-key": "61ff913e58mshdaa152f0f02cec1p145e79jsnbb4af2c8cda5"
        }
    })
    .then(response => response.json().then(data => {
        var matchesList = data['response'];
        var fixture = matchesList[0]['fixture'];
        var goals = matchesList[0]['goals'];
        var teams = matchesList[0]['teams'];
        console.log(matchesList.length);
        // Ustawianie pierwszego meczu
        elapsedTime.innerHTML = fixture['status']['elapsed'] + "'";
        homeTeamImage.src = teams['home']['logo'];
        homeTeamName.innerHTML = teams['home']['name'];
        awayTeamImage.src = teams['away']['logo'];
        awayTeamName.innerHTML = teams['away']['name'];
        lastMatchGoal.innerHTML = goals['home'] + " - " + goals['away'];

        for (var i = 1; i < matchesList.length; i++) {
            addMatchTile(matchesList[i]);
        }

    }))
    .catch(err => {
        console.log(err);
    });
});
