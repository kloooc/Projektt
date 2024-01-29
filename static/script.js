function openStatsUMA(matchID) {
    console.log('Otwieram update.html dla matchID:', matchID);

    
    window.open('/update?matchID=' + matchID, 'update', 'width=800,height=800');
    


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

function openStatsA(matchID) {
    // Otwórz stronę 'stats.html' z parametrem 'matchID' w nowym oknie lub karcie przeglądarki
    window.open('/statsA?matchID=' + matchID, 'Stats', 'width=800,height=800');
}

function openStatsUM(matchID) {
    window.open('/statsUP?matchID=' + matchID, 'StatsUP', 'width=800,height=800');
}

function openTeam(teamID) {
    window.open('/team?teamID=' + teamID, 'team', 'width=800,height=800');
}

function openTeamMatches(teamID) {
    window.location.href = '/team_matches?teamID=' + teamID;
}
function openTeamWyniki(teamID) {
    window.location.href = '/team_wyniki?teamID=' + teamID;
}
function openTeamsklad(teamID) {
    window.location.href = '/team?teamID=' + teamID;
}
function openComposition(matchID) {
    window.location.href = '/composition?matchID=' + matchID;
}

function showMatchAnalysis(matchID) {

    window.location.href = '/prematch?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}
function showStatsUM(matchID) {

    window.location.href = '/statsUP?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}
function showH2H(matchID) {

    window.location.href = '/h2h?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}

function showPlayer(playerID) {

    window.location.href = '/player?playerID=' + playerID; // Przekierowanie do strony analizy meczu
}

function showPlayerForm(playerID) {

    window.location.href = '/playerform?playerID=' + playerID; // Przekierowanie do strony analizy meczu
}

function showPlayerCompare(playerID) {

    window.location.href = '/playercompare?playerID=' + playerID; // Przekierowanie do strony analizy meczu
}

function showHomeTable() {
    var homeTable = document.getElementById("homeTable");
    var awayTable = document.getElementById("awayTable");
    var wholeTable = document.getElementById("wholeTable");

    homeTable.style.display = "";
    awayTable.style.display = "none";
    wholeTable.style.display = "none";
}
function showgoalsTable() {
    var goalsTable = document.getElementById("goalsTable");
    var assistsTable = document.getElementById("assistsTable");

    goalsTable.style.display = "";
    assistsTable.style.display = "none";
}

function showassistsTable() {
    var goalsTable = document.getElementById("goalsTable");
    var assistsTable = document.getElementById("assistsTable");

    goalsTable.style.display = "none";
    assistsTable.style.display = "";
}

function showAdminMatches() {
    var adminUsers = document.getElementById("adminUsers");
    var adminMatches = document.getElementById("adminMatches");
    var adminMatches1 = document.getElementById("adminMatches1");

    adminUsers.style.display = "none";
    adminMatches.style.display = "";
    adminMatches1.style.display = "";

}

function showAdminUsers() {
    var adminUsers = document.getElementById("adminUsers");
    var adminMatches = document.getElementById("adminMatches");
    var adminMatches1 = document.getElementById("adminMatches1");

    adminUsers.style.display = "";
    adminMatches.style.display = "none";
    adminMatches1.style.display = "none";
}

function showAwayTable() {
    var homeTable = document.getElementById("homeTable");
    var awayTable = document.getElementById("awayTable");
    var wholeTable = document.getElementById("wholeTable");

    homeTable.style.display = "none";
    awayTable.style.display = "";
    wholeTable.style.display = "none";
}

function showWholeTable() {
    var homeTable = document.getElementById("homeTable");
    var awayTable = document.getElementById("awayTable");
    var wholeTable = document.getElementById("wholeTable");

    homeTable.style.display = "none";
    awayTable.style.display = "none";
    wholeTable.style.display = "";
}
function showMatchAnalysisArchive(matchID) {

    window.location.href = '/prematchA?matchID=' + matchID; // Przekierowanie do strony analizy meczu
}