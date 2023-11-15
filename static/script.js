function openStatsUMA(matchID, matchDate) {
    console.log('Otwieram update.html dla matchID:', matchID);

    var currentDate = new Date();
    var day = matchDate.substring(0, 2); // Pobierz pierwsze dwa znaki
    var month = matchDate.substring(3, 5); // Pobierz kolejne dwa znaki
    var hour = matchDate.substring(7, 9); // Pobierz godzinę
    var minute = matchDate.substring(10, 12); // Pobierz minutę


    var matchDateTime = new Date(currentDate.getFullYear(), month - 1, day, hour, minute);
    if (matchDateTime < currentDate) {
        window.open('/update?matchID=' + matchID, 'update', 'width=800,height=800');
    } else {
        alert("Mecz jeszcze się nie odbył");
    }


}
// Funkcja do przełączania widoczności listy
function toggleList(id) {
    var list = document.getElementById(id);
    list.style.display = list.style.display === 'none' ? 'block' : 'none';
}

function openStats(matchID) {
    // Otwórz stronę 'stats.html' z parametrem 'matchID' w nowym oknie lub karcie przeglądarki
    window.open('/stats?matchID=' + matchID, 'Stats', 'width=800,height=800');
}

function openStatsUM(matchID) {
    console.log('Otwieram statsUP.html dla matchID:', matchID);
    window.open('/statsUP?matchID=' + matchID, 'StatsUP', 'width=800,height=800');
}

function showMatchAnalysis(matchID) {

    window.location.href = '/prematch?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}
function showStatsUM(matchID) {

    window.location.href = '/statsUP?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}