
import hashlib
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import subprocess
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'bardzosekretnyklucz'

# Inicjalizacja obsługi sesji
app.config['SESSION_TYPE'] = 'filesystem'  # Możesz użyć różnych typów sesji
Session(app)

@app.before_request
def set_default_user_type():
    if 'user_type' not in session:
        session['user_type'] = 'guest'


@app.route('/')
def show_main():
    user_type = session.get('user_type', 'guest')

    return render_template('main.html', user_type=user_type)

@app.route('/teams')
def display_teams():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Wykonaj zapytanie SQL
    query = """
    SELECT
        t.id_team,
        t.team AS Team_Name,
        t.logo AS Team_Logo,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 1
            ELSE NULL
        END) AS Wins,
        COUNT(CASE
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE NULL
        END) AS Draws,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA < m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB < m.scoreA) THEN 1
            ELSE NULL
        END) AS Losses,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA
            ELSE m.scoreB
        END) AS Goals_Scored,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreB
            ELSE m.scoreA
        END) AS Goals_Conceded,
        SUM(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 3
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE 0
        END) AS Points,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA - m.scoreB
            ELSE m.scoreB - m.scoreA
        END) AS Goal_Difference
    FROM
        teams AS t
    JOIN
        matches AS m
    ON
        t.id_team = m.teamA_id OR t.id_team = m.teamB_id
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC
    """

    cursor.execute(query)
    teams = cursor.fetchall()

    # Zamknij połączenie z bazą danych
    conn.close()

    # Przypisz nowe ID
    teams_with_new_id = []
    for i, team in enumerate(teams, start=1):
        team_with_new_id = (i,) + team[1:]
        teams_with_new_id.append(team_with_new_id)

    return render_template('teams.html', teams=teams_with_new_id)

@app.route('/matches')
def show_matches():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    
    # Pobierz mecze nadchodzące
    cursor.execute("""SELECT matches.date, teamsA.team AS teamA, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.scoreA IS NULL AND matches.scoreB IS NULL
        ORDER BY
    CASE
        WHEN SUBSTR(matches.date, 4, 2) IN ('10', '11', '12') THEN 1
        ELSE 2
    END, 
    CAST(SUBSTR(matches.date, 4, 2) AS SIGNED),  -- Sortowanie miesiąca jako liczby
    SUBSTR(matches.date, 1, 2) ASC;  -- Sortowanie dnia
    """)
    upcoming_matches = cursor.fetchall()

    # Pobierz mecze rozegrane
    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE NOT (matches.scoreA IS NULL AND matches.scoreB IS NULL)
    ORDER BY
        SUBSTR(matches.date, 4, 2) DESC,
        SUBSTR(matches.date, 1, 2) DESC; 
    """)

    played_matches = cursor.fetchall()

    
    # Zamknij połączenie z bazą danych
    conn.close()
    
    # Przekaż dane do szablonu HTML i wyświetl go
    return render_template('matches.html', upcoming_matches=upcoming_matches, played_matches=played_matches)

@app.route('/stats')
def show_stats():
    matchID = request.args.get('matchID')
    
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Pobierz dane meczu z bazy danych
    cursor.execute("SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()
    
    if result:
        teamA, teamB = result
    else:
        # Jeśli mecz nie istnieje, obsłuż to zgodnie z własnymi potrzebami
        return "Mecz nie istnieje"
    
    # Pobierz statystyki meczu z bazy danych
    cursor.execute("SELECT category, home_value, away_value FROM stats WHERE match_id = ?", (matchID,))
    stats = cursor.fetchall()
    
    # Zamknij połączenie z bazą danych
    conn.close()

    # Wyświetl szablon HTML z danymi
    return render_template('stats.html', teamA=teamA, teamB=teamB, stats=stats)

@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Sprawdź, czy użytkownik istnieje w bazie danych i hasło jest poprawne
        conn = sqlite3.connect('football_teams.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, user_type FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data and password == user_data[1]:
            # Ustaw sesję, aby oznaczyć użytkownika jako zalogowanego
            session['username'] = username
            session['user_type'] = user_data[2]
            return redirect(url_for('show_main'))

    return render_template('login_register.html')

@app.route('/logout')
def logout():
    # Usuń dane sesji, aby wylogować użytkownika
    session.pop('username', None)
    session.pop('user_type', None)
    return redirect(url_for('show_main'))

# Dodaj pozostałe trasy i funkcje obsługujące operacje, takie jak rejestracja, obsługa sesji itp.
# Należy odpowiednio dostosować te trasy do swoich potrzeb.

if __name__ == '__main__':
    app.run()
