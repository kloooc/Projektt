
import base64
import hashlib
import io
import signal
import sys
import bcrypt
from flask import Flask, flash, jsonify, render_template, request, redirect, url_for, session
import sqlite3
import subprocess
from flask_session import Session
import math
from math import exp
import atexit

from matplotlib import pyplot as plt

# Rejestracja funkcji do wywołania przed zakończeniem programu
atexit.register(lambda: session.clear())

def poisson(k, lambd):
    return (lambd**k) * exp(-lambd) / factorial(k)

def factorial(n):
    if n == 0 or n == 1:
        return 1
    return n * factorial(n-1)

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
        # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    username = session.get('username', '')
    user_type = session.get('user_type', 'guest')
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
    WHERE
        m.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC
    LIMIT 6; 
    """

    cursor.execute(query)
    teams = cursor.fetchall()

    # Pobierz mecze nadchodzące
    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.scoreA IS NULL AND matches.scoreB IS NULL
    ORDER BY
        matches.date  -- Sortowanie według daty rosnąco
    LIMIT 4;
    """)
    upcoming_matches = cursor.fetchall()

    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE NOT (matches.scoreA IS NULL AND matches.scoreB IS NULL)
    ORDER BY
        matches.date DESC
    LIMIT 6;
    """)
    played_matches = cursor.fetchall()

    cursor.execute('''
    SELECT
        players.player_id,
        players.full_name,
        teams.logo,
    SUM(match_players.goals) AS total_goals
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    match_players ON players.player_id = match_players.player_id
GROUP BY
        players.player_id,
        players.full_name
    ORDER BY
        total_goals DESC
    LIMIT 6;
''')
    players = cursor.fetchall()

    cursor.execute('''
    SELECT
        players.player_id,
        players.full_name,
        teams.logo,
    SUM(match_players.assists) AS total_assists
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    match_players ON players.player_id = match_players.player_id
GROUP BY
        players.player_id,
        players.full_name
    ORDER BY
        total_assists DESC
    LIMIT 6;
''')
    playersa = cursor.fetchall()

    query = '''
    SELECT distinct teams.id_team, teams.team
    FROM teams
    JOIN matches ON teams.id_team = matches.teamA_id
    WHERE matches.date > '2023-07-01'
    Order by teams.id_team asc;
    '''
    cursor.execute(query)
    teamsc = cursor.fetchall()
    # Zamknij połączenie z bazą danych
    conn.close()

    # Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))
    pindexes = list(range(1, len(players) + 1))
    paindexes = list(range(1, len(playersa) + 1))
    return render_template('main.html', user_type=user_type, teams=teams, teamsc=teamsc, indexes=indexes, upcoming_matches=upcoming_matches, played_matches=played_matches, username=username, players=players, pindexes=pindexes, playersa=playersa, paindexes=paindexes)

@app.route('/teams')
def display_teams():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    user_type = session.get('user_type', 'guest')
    username = session.get('username', '')
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
    WHERE
        m.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()

    query = """
    SELECT
        t.id_team,
        t.team AS Team_Name,
        t.logo AS Team_Logo,
        COUNT(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 1
            ELSE NULL
        END) AS Wins,
        COUNT(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB = m.scoreA) THEN 1
            ELSE NULL
        END) AS Draws,
        COUNT(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB < m.scoreA) THEN 1
            ELSE NULL
        END) AS Losses,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreB
        END) AS Goals_Scored,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreA
        END) AS Goals_Conceded,
        SUM(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 3
            WHEN (m.teamB_id = t.id_team AND m.scoreB = m.scoreA) THEN 1
            ELSE 0
        END) AS Points,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreB - m.scoreA
        END) AS Goal_Difference
    FROM
        teams AS t
    JOIN
        matches AS m
    ON
        t.id_team = m.teamB_id 
    WHERE
        m.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teamsa = cursor.fetchall()

    query = """
    SELECT
        t.id_team,
        t.team AS Team_Name,
        t.logo AS Team_Logo,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) THEN 1
            ELSE NULL
        END) AS Wins,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA = m.scoreB) THEN 1
            ELSE NULL
        END) AS Draws,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA < m.scoreB) THEN 1
            ELSE NULL
        END) AS Losses,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA
        END) AS Goals_Scored,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreB
        END) AS Goals_Conceded,
        SUM(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) THEN 3
            WHEN (m.teamA_id = t.id_team AND m.scoreA = m.scoreB) THEN 1
            ELSE 0
        END) AS Points,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA - m.scoreB
        END) AS Goal_Difference
    FROM
        teams AS t
    JOIN
        matches AS m
    ON
        t.id_team = m.teamA_id 
    WHERE
        m.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teamsh = cursor.fetchall()

    # Zamknij połączenie z bazą danych
    conn.close()

    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))
    #Utwórz listę indeksów
    indexesa = list(range(1, len(teamsa) + 1))
    #Utwórz listę indeksów
    indexesh = list(range(1, len(teamsh) + 1))

    return render_template('teams.html', teams=teams, user_type=user_type, teamsa=teamsa, teamsh=teamsh, indexes=indexes,indexesa=indexesa, indexesh=indexesh, username=username)

@app.route('/matches')
def show_matches():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    username = session.get('username', '')

    user_type = session.get('user_type', 'guest')

    
     # Pobierz mecze nadchodzące
    cursor.execute("""SELECT matches.date, teamsA.team AS teamA, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
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




    
    # Zamknij połączenie z bazą danych
    conn.close()
    
    # Przekaż dane do szablonu HTML i wyświetl go
    return render_template('matches.html', upcoming_matches=upcoming_matches, user_type=user_type, username=username)

@app.route('/stats')
def show_stats():
    matchID = request.args.get('matchID')
    
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Pobierz dane meczu z bazy danych
    cursor.execute("SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()
    

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()


    if result:
        teamA, teamB = result
    else:
        # Jeśli mecz nie istnieje, obsłuż to zgodnie z własnymi potrzebami
        return "Mecz nie istnieje"
    
    # Pobierz statystyki meczu z bazy danych
    cursor.execute("SELECT c.category_name, s.home_value, s.away_value FROM stats s JOIN categories c ON s.categoryid = c.categoryid WHERE s.match_id = ?", (matchID,))
    stats = cursor.fetchall()
    
    cursor.execute("SELECT logo from teams where team=?",(teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?",(teamB,))
    logoB = cursor.fetchone()

    # Zamknij połączenie z bazą danych
    conn.close()

    # Wyświetl szablon HTML z danymi
    return render_template('stats.html', teamA=teamA, teamB=teamB, stats=stats,match=match, logoA=logoA, logoB=logoB)


@app.route('/statsUP')
def show_stats_upcoming():
    matchID = request.args.get('matchID')

    if matchID is None:
        print('Brak matchID w zapytaniu!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak matchID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    cursor.execute("SELECT distinct teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()

    if result is None:
        print('Brak meczu o podanym matchID!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak meczu o podanym matchID"

    teamA, teamB = result

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamA,))
    teamA_id = cursor.fetchone()[0]

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB,))
    teamB_id = cursor.fetchone()[0]

    cursor.execute("SELECT logo from teams where team=?", (teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?", (teamB,))
    logoB = cursor.fetchone()

    cursor.execute("SELECT scoreA FROM matches WHERE teamA_id = ? AND scoreA IS NOT NULL", (teamA_id,))
    scores_teamA = cursor.fetchall()

    scores_teamA = [score[0] for score in scores_teamA if score[0] is not None]

    print("Scores TeamA:", scores_teamA)

    cursor.execute("SELECT scoreB FROM matches WHERE teamB_id = ? AND scoreB IS NOT NULL", (teamB_id,))
    scores_teamB = cursor.fetchall()

    scores_teamB = [score[0] for score in scores_teamB if score[0] is not None]

    print("Scores TeamB:", scores_teamB)

    lambda_teamA = max(0.1, sum(scores_teamA) / len(scores_teamA))
    lambda_teamB = max(0.1, sum(scores_teamB) / len(scores_teamB))

    print(lambda_teamA)
    print(lambda_teamB)

    szanse_teamA = [poisson(k, lambda_teamA) for k in range(4)]
    szanse_teamB = [poisson(k, lambda_teamB) for k in range(4)]

    print(szanse_teamA)
    print(szanse_teamB)

    # Oblicz średnią liczbę bramek dla drużyn
    srednia_teamA = sum(scores_teamA) / len(scores_teamA)
    srednia_teamB = sum(scores_teamB) / len(scores_teamB)

    conn.close()
    return render_template('statsUP.html', teamA=teamA, teamB=teamB, logoA=logoA, match=match, logoB=logoB, srednia_teamA=srednia_teamA, srednia_teamB=srednia_teamB, prawdopodobienstwa_teamA=szanse_teamA, prawdopodobienstwa_teamB=szanse_teamB)




@app.route('/login_register', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('football_teams.db')
        cursor = conn.cursor()
        cursor.execute("SELECT password, user_type, confirmed FROM users WHERE username=?", (username,))
        user_data = cursor.fetchone()
        conn.close()

        if user_data:
            hashed_password = user_data[0]

            if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                session['username'] = username
                session['user_type'] = user_data[1]
                
                if user_data[2] != 1:  # Sprawdź wartość kolumny confirmed
                    flash('Twoje konto oczekuje na akceptację.')
                    return redirect(url_for('login_register'))
                    
                
                return redirect(url_for('show_main'))

        flash('Nieprawidłowa nazwa użytkownika lub hasło.')

    return render_template('login_register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['regUsername']  # Update to use 'regUsername'
        password = request.form['regPassword']  # Update to use 'regPassword'
        confirm_password = request.form['confirmPassword']  # Update to use 'confirmPassword'

        # Sprawdzenie, czy wszystkie pola formularza są wypełnione
        if not (username and password and confirm_password):
            flash('Wszystkie pola są wymagane!')
            return redirect(url_for('login_register'))

        # Sprawdzenie, czy hasła się zgadzają
        if password != confirm_password:
            flash('Hasła nie pasują do siebie!')
            return redirect(url_for('login_register'))

        # Sprawdzenie, czy użytkownik o danej nazwie już istnieje w bazie danych
        conn = sqlite3.connect('football_teams.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            flash('Nazwa użytkownika już istnieje. Wybierz inną nazwę.')
            return redirect(url_for('login_register'))

        # Haszowanie hasła przed zapisaniem go do bazy danych
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Dodanie nowego użytkownika do bazy danych
        cursor.execute("INSERT INTO users (username, password, user_type, confirmed) VALUES (?, ?, ?, ?)",
                       (username, hashed_password.decode('utf-8'), 'user', False))
        conn.commit()
        conn.close()

        flash('Pomyślnie zarejestrowano! Możesz się teraz zalogować.')
        return redirect(url_for('login_register'))

    return render_template('login_register.html')

@app.route('/admin')
def admin():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    username = session.get('username', '')

    # Pobierz mecze nadchodzące
    cursor.execute("""SELECT matches.date, teamsA.team AS teamA, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
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
    SUBSTR(matches.date, 1, 2) ASC  -- Sortowanie dnia
    LIMIT 20;
    """)
    upcoming_matches = cursor.fetchall()

# Pobierz użytkowników oczekujących na akceptację
    cursor.execute("SELECT * FROM users WHERE confirmed = 0")
    users_waiting_approval = cursor.fetchall()

    # Pobierz użytkowników premium
    cursor.execute("SELECT * FROM users WHERE user_type = 'user_premium'")
    premium_users = cursor.fetchall()

    # Pobierz wszystkich pozostałych użytkowników
    cursor.execute("SELECT * FROM users WHERE confirmed = 1")
    other_users = cursor.fetchall()

    conn.close()

                           
    # Zamknij połączenie z bazą danych
    conn.close()
    
    # Przekaż dane do szablonu HTML i wyświetl go
    return render_template('admin.html', upcoming_matches=upcoming_matches, username=username, users_waiting_approval=users_waiting_approval,
                           premium_users=premium_users,
                           other_users=other_users)
    

@app.route('/update')
def update():
    matchID = request.args.get('matchID')

    if matchID is None:
        print('Brak matchID w zapytaniu!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak matchID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    cursor.execute("SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()

    if result is None:
        print('Brak meczu o podanym matchID!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak meczu o podanym matchID"

    teamA, teamB = result

    # Pobierz statystyki meczu z bazy danych
    cursor.execute("SELECT distinct category FROM stats ")
    stats = cursor.fetchall()
    
    # Zamknij połączenie z bazą danych
    conn.close()

    
    return render_template('update.html',teamA=teamA, teamB=teamB,stats=stats)

@app.route('/download_stats', methods=['POST'])
def download_stats():
    link = request.form['link']

    # Tutaj możesz użyć pobrania linku do uruchomienia skryptu z linkiem
    subprocess.run(["python", "pobieraniestats.py", link])

    return redirect(url_for('show_main'))

@app.route('/logout')
def logout():
    # Usuń dane sesji, aby wylogować użytkownika
    session.pop('username', None)
    session.pop('user_type', None)
    session.clear()
    return redirect(url_for('show_main'))

@app.route('/prematch')
def show_prematch():
    matchID = request.args.get('matchID')

    if matchID is None:
        print('Brak matchID w zapytaniu!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak matchID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()

    cursor.execute("SELECT distinct teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()
    
    if result is None:
        print('Brak danych dla teamA i teamB')
        return "Brak danych dla teamA i teamB"

    teamA, teamB = result  # Przypisanie wartości do zmiennych teamA i teamB po pobraniu z bazy danych

    cursor.execute("SELECT logo from teams where team=?", (teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?", (teamB,))
    logoB = cursor.fetchone()

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamA,))
    teamA_id = cursor.fetchone()[0]

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB,))
    teamB_id = cursor.fetchone()[0]

    cursor.execute("SELECT scoreA FROM matches WHERE teamA_id = ? AND scoreA IS NOT NULL", (teamA_id,))
    scores_teamA = cursor.fetchall()

    scores_teamA = [score[0] for score in scores_teamA if score[0] is not None]

    print("Scores TeamA:", scores_teamA)

    cursor.execute("SELECT scoreB FROM matches WHERE teamB_id = ? AND scoreB IS NOT NULL", (teamB_id,))
    scores_teamB = cursor.fetchall()

    scores_teamB = [score[0] for score in scores_teamB if score[0] is not None]

    print("Scores TeamB:", scores_teamB)

    lambda_teamA = max(0.1, sum(scores_teamA) / len(scores_teamA))
    lambda_teamB = max(0.1, sum(scores_teamB) / len(scores_teamB))

    print(lambda_teamA)
    print(lambda_teamB)

    szanse_teamA = [poisson(k, lambda_teamA) for k in range(4)]
    szanse_teamB = [poisson(k, lambda_teamB) for k in range(4)]

    print(szanse_teamA)
    print(szanse_teamB)

    # Oblicz średnią liczbę bramek dla drużyn
    srednia_teamA = sum(scores_teamA) / len(scores_teamA)
    srednia_teamB = sum(scores_teamB) / len(scores_teamB)

    conn.close()
    return render_template('prematch.html', teamA=teamA, teamB=teamB, logoA=logoA, logoB=logoB, srednia_teamA=srednia_teamA, match=match, srednia_teamB=srednia_teamB, prawdopodobienstwa_teamA=szanse_teamA, prawdopodobienstwa_teamB=szanse_teamB)
    
@app.route('/wyniki')
def show_wyniki():
    # Połącz się z bazą danych
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    user_type = session.get('user_type', 'guest')
    username = session.get('username', '')

    
         # Pobierz mecze rozegrane
    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE NOT (matches.scoreA IS NULL AND matches.scoreB IS NULL)
    AND matches.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'  -- Dodany warunek WHERE dla daty
    ORDER BY matches.date DESC;
""")
    played_matches = cursor.fetchall()


    
    # Zamknij połączenie z bazą danych
    conn.close()
    
    # Przekaż dane do szablonu HTML i wyświetl go
    return render_template('wyniki.html', played_matches=played_matches, user_type=user_type, username=username)

@app.route('/h2h')
def show_H2H():
    matchID = request.args.get('matchID')

    if matchID is None:
        print('Brak matchID w zapytaniu!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak matchID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    cursor.execute("SELECT distinct teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()

    if result is None:
        print('Brak meczu o podanym matchID!')
        # Możesz obsłużyć ten przypadek, np. przekierowując użytkownika gdzie indziej
        return "Brak meczu o podanym matchID"

    teamA, teamB = result

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamA,))
    teamA_id = cursor.fetchone()[0]

    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB,))
    teamB_id = cursor.fetchone()[0]

    cursor.execute("SELECT logo from teams where team=?", (teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?", (teamB,))
    logoB = cursor.fetchone()

    cursor.execute("SELECT scoreA FROM matches WHERE teamA_id = ? AND scoreA IS NOT NULL", (teamA_id,))
    scores_teamA = cursor.fetchall()

    scores_teamA = [score[0] for score in scores_teamA if score[0] is not None]

    print("Scores TeamA:", scores_teamA)

    cursor.execute("SELECT scoreB FROM matches WHERE teamB_id = ? AND scoreB IS NOT NULL", (teamB_id,))
    scores_teamB = cursor.fetchall()

    scores_teamB = [score[0] for score in scores_teamB if score[0] is not None]

    print("Scores TeamB:", scores_teamB)

    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE (matches.teamA_id = ? AND matches.teamB_id = ?) OR (matches.teamA_id = ? AND matches.teamB_id = ?)
    AND NOT (matches.scoreA IS NULL AND matches.scoreB IS NULL)
    ORDER BY matches.date DESC;
    """, (teamA_id, teamB_id, teamB_id, teamA_id))
    played_matches = cursor.fetchall()

    conn.close()
    return render_template('h2h.html', teamA=teamA, teamB=teamB, logoA=logoA, match=match, logoB=logoB, played_matches=played_matches)

@app.route('/team')
def show_team():
    teamID = request.args.get('teamID')

    if teamID is None:
        print('Brak teamID w zapytaniu!')
        return "Brak teamID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT logo, team, id_team FROM teams WHERE id_team = ?', (teamID,))
    team = cursor.fetchall()

    if not team:
        print('Brak teamu o podanym teamID!')
        return "Brak meczu o podanym teamID"
    
    cursor.execute('''
    SELECT
    players.player_id,
    players.full_name,
    teams.team,
    SUM(match_players.time_played) AS total_time_played,
    SUM(match_players.goals) AS total_goals,
    SUM(match_players.assists) AS total_assists,
    SUM(match_players.yellow_card) AS total_yellow_cards,
    SUM(match_players.red_card) AS total_red_cards,
    COUNT(CASE WHEN match_players.time_played > 0 THEN match_players.matchid END) AS matches_played
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    player_positions ON players.player_id = player_positions.player_id
LEFT JOIN
    match_players ON players.player_id = match_players.player_id
WHERE
    player_positions.position_id = 1 AND teams.id_team = ?
GROUP BY
    players.player_id, teams.team;
''', (teamID,))
    bramkarze = cursor.fetchall()

    cursor.execute('''
    SELECT
    players.player_id,
    players.full_name,
    teams.team,
    SUM(match_players.time_played) AS total_time_played,
    SUM(match_players.goals) AS total_goals,
    SUM(match_players.assists) AS total_assists,
    SUM(match_players.yellow_card) AS total_yellow_cards,
    SUM(match_players.red_card) AS total_red_cards,
    COUNT(CASE WHEN match_players.time_played > 0 THEN match_players.matchid END) AS matches_played
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    player_positions ON players.player_id = player_positions.player_id
LEFT JOIN
    match_players ON players.player_id = match_players.player_id
WHERE
    player_positions.position_id = 2 AND teams.id_team = ?
GROUP BY
    players.player_id, teams.team;
''', (teamID,))
    obroncy = cursor.fetchall()

    cursor.execute('''
    SELECT
    players.player_id,
    players.full_name,
    teams.team,
    SUM(match_players.time_played) AS total_time_played,
    SUM(match_players.goals) AS total_goals,
    SUM(match_players.assists) AS total_assists,
    SUM(match_players.yellow_card) AS total_yellow_cards,
    SUM(match_players.red_card) AS total_red_cards,
    COUNT(CASE WHEN match_players.time_played > 0 THEN match_players.matchid END) AS matches_played
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    player_positions ON players.player_id = player_positions.player_id
LEFT JOIN
    match_players ON players.player_id = match_players.player_id
WHERE
    player_positions.position_id = 3 AND teams.id_team = ?
GROUP BY
    players.player_id, teams.team;
''', (teamID,))
    pomocnicy = cursor.fetchall()

    cursor.execute('''
    SELECT
    players.player_id,
    players.full_name,
    teams.team,
    SUM(match_players.time_played) AS total_time_played,
    SUM(match_players.goals) AS total_goals,
    SUM(match_players.assists) AS total_assists,
    SUM(match_players.yellow_card) AS total_yellow_cards,
    SUM(match_players.red_card) AS total_red_cards,
    COUNT(CASE WHEN match_players.time_played > 0 THEN match_players.matchid END) AS matches_played
FROM
    players
JOIN
    teams_players ON players.player_id = teams_players.player_id
JOIN
    teams ON teams_players.id_team = teams.id_team
JOIN
    player_positions ON players.player_id = player_positions.player_id
LEFT JOIN
    match_players ON players.player_id = match_players.player_id
WHERE
    player_positions.position_id = 4 AND teams.id_team = ?
GROUP BY
    players.player_id, teams.team;
''', (teamID,))

    napastnicy = cursor.fetchall()

    cursor.execute('''
    SELECT
        players.player_id,
        players.full_name,
        teams.team,
        SUM(match_players.time_played) AS total_time_played,
        SUM(match_players.goals) AS total_goals,
        SUM(match_players.assists) AS total_assists,
        SUM(match_players.yellow_card) AS total_yellow_cards,
        SUM(match_players.red_card) AS total_red_cards,
        COUNT(CASE WHEN match_players.time_played > 0 THEN match_players.matchid END) AS matches_played
    FROM
        players
    JOIN
        teams_players ON players.player_id = teams_players.player_id
    JOIN
        teams ON teams_players.id_team = teams.id_team
    JOIN
        player_positions ON players.player_id = player_positions.player_id
    LEFT JOIN
        match_players ON players.player_id = match_players.player_id
    WHERE
        player_positions.position_id = 5 AND teams.id_team = ?
    GROUP BY
        players.player_id, teams.team;
''', (teamID,))

    trener = cursor.fetchall()

    conn.close()

    return render_template('team.html', teams=team, bramkarze=bramkarze, obroncy=obroncy, pomocnicy=pomocnicy,napastnicy=napastnicy,trener=trener)

@app.route('/team_matches')
def show_teamMatches():
    teamID = request.args.get('teamID')

    if teamID is None:
        print('Brak teamID w zapytaniu!')
        return "Brak teamID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT logo, team, id_team FROM teams WHERE id_team = ?', (teamID,))
    team = cursor.fetchall()

    if not team:
        print('Brak teamu o podanym teamID!')
        return "Brak meczu o podanym teamID"
    
    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.scoreA IS NULL AND matches.scoreB IS NULL AND (matches.teamA_id = ? or matches.teamB_id=?)
    ORDER BY
        matches.date;
    """, (teamID, teamID))
    upcoming_matches = cursor.fetchall()

    return render_template('team_matches.html', teams=team, upcoming_matches=upcoming_matches)

@app.route('/team_wyniki')
def show_teamWyniki():
    teamID = request.args.get('teamID')

    if teamID is None:
        print('Brak teamID w zapytaniu!')
        return "Brak teamID"

    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT logo, team, id_team FROM teams WHERE id_team = ?', (teamID,))
    team = cursor.fetchall()

    if not team:
        print('Brak teamu o podanym teamID!')
        return "Brak meczu o podanym teamID"
    
    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE NOT (matches.scoreA IS NULL AND matches.scoreB IS NULL) AND (matches.teamA_id = ? or matches.teamB_id=?)
    ORDER BY
        matches.date;
    """, (teamID, teamID))
    played_matches = cursor.fetchall()

    return render_template('team_wyniki.html', teams=team, played_matches=played_matches)

@app.route('/player', methods=['GET', 'POST'])
def show_player():
    playerID = request.args.get('playerID')

    if playerID is None:
        print('Brak playerID w zapytaniu!')
        return "Brak playerID"
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    query = '''
    SELECT player_id
    FROM players 
    WHERE player_id = ?
'''

# Wykonaj zapytanie z parametrem player_id
    cursor.execute(query, (playerID,))
    playera = cursor.fetchone() 
    query = '''
    SELECT m.matchID, t1.team AS teamA_name, t2.team AS teamB_name, t1.logo AS teamA_logo, t2.logo AS teamB_logo,
           m.ScoreA, m.ScoreB, m.date,
           mp.player_id, mp.time_played, mp.goals, mp.assists, mp.yellow_card, mp.red_card,
           p.full_name
    FROM matches AS m
    JOIN match_players AS mp ON m.matchID = mp.matchID
    JOIN players as p ON mp.player_id = p.player_id
    JOIN teams AS t1 ON m.teamA_id = t1.id_team
    JOIN teams AS t2 ON m.teamB_id = t2.id_team
    WHERE m.ScoreA IS NOT NULL AND m.ScoreB IS NOT NULL AND mp.player_id = ?
'''

# Wykonaj zapytanie z parametrem player_id
    cursor.execute(query, (playerID,))

# Pobierz wyniki zapytania
    matches_and_players = cursor.fetchall()
    

    query = '''
    SELECT p.full_name, t.id_team, t.logo
    FROM players AS p
    JOIN teams_players AS tp ON p.player_id = tp.player_id
    JOIN teams AS t ON tp.id_team = t.id_team
    Where p.player_id = ?
'''
    cursor.execute(query, (playerID,))
    player = cursor.fetchone()

    query = '''
    SELECT
        players.player_id,
        players.full_name,
        match_players.time_played,
        match_players.matchid, match_players.goals, match_players.assists, match_players.yellow_card, match_players.red_card
    FROM
        players
    LEFT JOIN
        match_players ON players.player_id = match_players.player_id
    WHERE players.player_id = ?
    Order by match_players.matchid asc
'''

# Wykonanie zapytania z parametrem playerID
    cursor.execute(query, (playerID,))
    results = cursor.fetchall()  # Pobranie wszystkich wierszy wyniku

# Sprawdzenie czy wyniki nie są puste
    if results:
        match_ids = [row[3] for row in results]  # Pobranie wszystkich numerów meczów
        unique_match_ids = sorted(set(match_ids))  # Utworzenie unikalnej listy numerów meczów
        match_number_dict = {match_id: index + 1 for index, match_id in enumerate(unique_match_ids)}  # Słownik przypisujący numerom meczów ich kolejne wartości

    # Wyświetlenie wyników z numerami meczów od 1 do x
        for row in results:
            match_id = row[3]
            match_number = match_number_dict[match_id]
    else:
        print("Brak danych dla tego gracza")

    match_numbers = []
    total_time_played = []

    for row in results:
        match_id = row[3]
        match_number = match_number_dict[match_id]
        match_numbers.append(match_number)
        total_time_played.append(row[2])
    plt.figure(figsize=(8, 6))  # Ustalenie rozmiaru wykresu
    plt.plot(match_numbers, total_time_played, linestyle='-')  # Wygenerowanie wykresu
    plt.title('Czas gry w poszczególnych meczach')  # Tytuł wykresu
    plt.xlabel('Numer meczu')  # Oś X
    plt.ylabel('Czas gry')  # Oś Y
    plt.grid(True)  # Dodanie siatki

 # Zapisanie wygenerowanego wykresu do pamięci jako strumień binarny
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    time_played = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.figure(figsize=(8, 6))

    plt.scatter(match_numbers, [row[4] for row in results], label='Goals', color='blue')
    plt.scatter(match_numbers, [row[5] for row in results], label='Assists', color='green')
    plt.scatter(match_numbers, [row[6] for row in results], label='Yellow Cards', color='yellow')


    plt.title('Statystyki meczowe')
    plt.xlabel('Numer meczu')
    plt.ylabel('Wartość')
    plt.legend()
    plt.grid(True)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    statistics = base64.b64encode(buffer.getvalue()).decode('utf-8')

    query = '''
    SELECT distinct teams.id_team, teams.team
    FROM teams
    JOIN matches ON teams.id_team = matches.teamA_id
    WHERE matches.date > '2023-07-01'
    Order by teams.id_team asc;
    '''
    cursor.execute(query)
    teams = cursor.fetchall()



    return render_template('player.html', matches_and_players=matches_and_players, player=player, playera=playera, statistics=statistics, time_played=time_played, teams=teams)


@app.route('/playercompare', methods=['GET', 'POST'])
def show_playerCompare():
    playerID = request.args.get('playerID')

    if playerID is None:
        print('Brak playerID w zapytaniu!')
        return "Brak playerID"
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    query = '''
    SELECT player_id
    FROM players 
    WHERE player_id = ?
'''

# Wykonaj zapytanie z parametrem player_id
    cursor.execute(query, (playerID,))
    playera = cursor.fetchone() 

    query = '''
    SELECT p.full_name, t.id_team, t.logo
    FROM players AS p
    JOIN teams_players AS tp ON p.player_id = tp.player_id
    JOIN teams AS t ON tp.id_team = t.id_team
    Where p.player_id = ?
'''
    cursor.execute(query, (playerID,))
    player = cursor.fetchone()

    query = '''
    SELECT
        players.player_id,
        players.full_name,
        match_players.time_played,
        match_players.matchid, match_players.goals, match_players.assists, match_players.yellow_card, match_players.red_card
    FROM
        players
    LEFT JOIN
        match_players ON players.player_id = match_players.player_id
    WHERE players.player_id = ?
    Order by match_players.matchid asc
'''

# Wykonanie zapytania z parametrem playerID
    cursor.execute(query, (playerID,))
    results = cursor.fetchall()  # Pobranie wszystkich wierszy wyniku

# Sprawdzenie czy wyniki nie są puste
    if results:
        match_ids = [row[3] for row in results]  # Pobranie wszystkich numerów meczów
        unique_match_ids = sorted(set(match_ids))  # Utworzenie unikalnej listy numerów meczów
        match_number_dict = {match_id: index + 1 for index, match_id in enumerate(unique_match_ids)}  # Słownik przypisujący numerom meczów ich kolejne wartości

    # Wyświetlenie wyników z numerami meczów od 1 do x
        for row in results:
            match_id = row[3]
            match_number = match_number_dict[match_id]
    else:
        print("Brak danych dla tego gracza")


    match_numbers = []


    for row in results:
        match_id = row[3]
        match_number = match_number_dict[match_id]
        match_numbers.append(match_number)
        

    total_time_played = []  # Lista przechowująca sumę czasu gry dla każdego meczu
    cumulative_time = 0  # Inicjalizacja zmiennej przechowującej sumę czasu gry

    for row in results:
        time_played = row[2]  # Zmienna przechowująca czas gry z bazy danych (wynik z kolumny match_players.time_played)
        cumulative_time += time_played  # Dodaj czas gry do sumy czasu gry
        total_time_played.append(cumulative_time)  # Dodaj sumę czasu gry do listy

    # Wygenerowanie wykresu
    plt.figure(figsize=(8, 6))
    plt.plot(match_numbers, total_time_played, linestyle='-')
    plt.title('Czas gry w poszczególnych meczach')
    plt.xlabel('Numer meczu')
    plt.ylabel('Suma minut możliwych do rozegrania')
    plt.grid(True)

 # Zapisanie wygenerowanego wykresu do pamięci jako strumień binarny
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    time_played = base64.b64encode(buffer.getvalue()).decode('utf-8')



    query = '''
    SELECT distinct teams.id_team, teams.team
    FROM teams
    JOIN matches ON teams.id_team = matches.teamA_id
    WHERE matches.date > '2023-07-01'
    Order by teams.id_team asc;
    '''
    cursor.execute(query)
    teams = cursor.fetchall()

    return render_template('playercompare.html',playerID=playerID, player=player, playera=playera, time_played=time_played, teams=teams)

@app.route('/get_players', methods=['POST'])
def get_players():
    team_id = request.json.get('teamId')  # Pobranie ID wybranej drużyny z żądania POST
    playerID = request.json.get('playerID')
    print(team_id)
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()
    query = '''
    SELECT p.player_id, p.full_name, t.id_team, pos.position_name
    FROM players AS p
    JOIN player_positions AS pp ON p.player_id = pp.player_id
    JOIN positions AS pos ON pp.position_id = pos.position_id
    JOIN teams_players AS tp ON p.player_id = tp.player_id
    JOIN teams AS t ON tp.id_team = t.id_team
    Where t.id_team = ? AND pos.position_name != "trener" AND p.player_id != ?
'''
    cursor.execute(query, (team_id,playerID))

    results = cursor.fetchall()

    players = []  # Inicjalizacja listy graczy

    # Przetwarzanie wyników zapytania i dodanie do listy players
    for row in results:
        player_data = {
            'player_id': row[0],
            'full_name': row[1],
            'position_name': row[3]
        }
        players.append(player_data)

    # Zamykanie połączenia z bazą danych
    conn.close()

    return jsonify({'players': players})  # Zwrócenie listy zawodników jako odpowiedź JSON

@app.route('/get_player_data', methods=['POST'])
def get_player_data():
    player_id = request.json.get('player_id')
    playerID = request.json.get('playerID')
    
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Zapytanie dla zawodnika A
    query_player_a = '''
        SELECT
            players.player_id,
            players.full_name,
            match_players.time_played,
            match_players.matchid,
            match_players.goals,
            match_players.assists,
            match_players.yellow_card,
            match_players.red_card
        FROM
            players
        LEFT JOIN
            match_players ON players.player_id = match_players.player_id
        WHERE players.player_id = ?
        ORDER BY match_players.matchid ASC
    '''

    # Zapytanie dla zawodnika B
    query_player_b = '''
        SELECT
            players.player_id,
            players.full_name,
            match_players.time_played,
            match_players.matchid,
            match_players.goals,
            match_players.assists,
            match_players.yellow_card,
            match_players.red_card
        FROM
            players
        LEFT JOIN
            match_players ON players.player_id = match_players.player_id
        WHERE players.player_id = ?
        ORDER BY match_players.matchid ASC
    '''

    # Wykonanie zapytania dla zawodnika A
    cursor.execute(query_player_a, (player_id,))
    results_player_a = cursor.fetchall()

    # Wykonanie zapytania dla zawodnika B
    cursor.execute(query_player_b, (playerID,))
    results_player_b = cursor.fetchall()

    if results_player_a and results_player_b:
        match_ids_a = [row[3] for row in results_player_a]
        unique_match_ids_a = sorted(set(match_ids_a))
        match_number_dict_a = {match_id: index + 1 for index, match_id in enumerate(unique_match_ids_a)}

        match_numbers_a = [match_number_dict_a[row[3]] for row in results_player_a]

        total_time_played_p1 = [0]  # Czas gry dla zawodnika A
        total_time_played_p2 = [0]  # Czas gry dla zawodnika B

        for row in results_player_a:
            time_played = row[2]
            total_time_played_p1.append(total_time_played_p1[-1] + time_played)

        total_time_played_p1.pop(0)

        for row in results_player_b:
            time_played = row[2]
            total_time_played_p2.append(total_time_played_p2[-1] + time_played)

        total_time_played_p2.pop(0)
        
        player_name_a = results_player_a[0][1]  # Nazwa zawodnika A
        player_name_b = results_player_b[0][1]  # Nazwa zawodnika B
        
        plt.figure(figsize=(8, 6))
        plt.plot(match_numbers_a, total_time_played_p1, label=player_name_a, linestyle='-')
        plt.plot(match_numbers_a, total_time_played_p2, label=player_name_b, linestyle='-')

        plt.title('Czas gry')
        plt.xlabel('Numer meczu')
        plt.ylabel('Suma minut możliwych do rozegrania')
        plt.grid(True)
        plt.legend()  # Dodanie legendy

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        time_played = base64.b64encode(buffer.getvalue()).decode('utf-8')

        conn.close()

        return jsonify({'time_played': time_played})

    return jsonify({'error': 'Brak danych dla obu graczy'})

@app.route('/composition')
def show_composition():
    matchID = request.args.get('matchID')
    
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Pobierz dane meczu z bazy danych
    cursor.execute("SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()
    

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()


    if result:
        teamA, teamB = result
    else:
        # Jeśli mecz nie istnieje, obsłuż to zgodnie z własnymi potrzebami
        return "Mecz nie istnieje"
    
    
    cursor.execute("SELECT logo from teams where team=?",(teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?",(teamB,))
    logoB = cursor.fetchone()

    cursor.execute("SELECT id_team from teams where team=?", (teamA,))
    teamA_id = cursor.fetchone()
    if teamA_id:
        teamA_id = teamA_id[0]  # Pobranie wartości z krotki

    cursor.execute("SELECT id_team from teams where team=?", (teamB,))
    teamB_id = cursor.fetchone()
    if teamB_id:
        teamB_id = teamB_id[0]  # Pobranie wartości z krotki


    cursor.execute("""
        SELECT p.full_name
        FROM players p
        INNER JOIN match_players mp ON p.player_id = mp.player_id
        INNER JOIN matches m ON mp.matchid = m.matchid
        INNER JOIN teams_players tp ON p.player_id = tp.player_id
        WHERE tp.id_team = ? AND mp.time_played > 0 AND m.matchid = ?
        """, (teamA_id, matchID)) 
    playerh = cursor.fetchall()

    cursor.execute("""
        SELECT p.full_name
        FROM players p
        INNER JOIN match_players mp ON p.player_id = mp.player_id
        INNER JOIN matches m ON mp.matchid = m.matchid
        INNER JOIN teams_players tp ON p.player_id = tp.player_id
        WHERE tp.id_team = ? AND mp.time_played > 0 AND m.matchid = ?
        """, (teamB_id, matchID)) 
    playera = cursor.fetchall()

    # Zamknij połączenie z bazą danych
    conn.close()

    # Wyświetl szablon HTML z danymi
    return render_template('composition.html', teamA=teamA, teamB=teamB, match=match, logoA=logoA, logoB=logoB, playerh=playerh, playera=playera)

@app.route('/archiwum')
def archiwum():
    username = session.get('username', '')
    user_type = session.get('user_type', 'guest')
    return render_template('archiwum.html', user_type=user_type, username=username)

@app.route('/archiwum/sezon23-24')
def sezon_23_24():
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
    WHERE
        m.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()



    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))


    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.date BETWEEN '2023-07-20 00:00:00' AND '2024-05-26 00:00:00'
    ORDER BY
        matches.date DESC
    """)
    matches = cursor.fetchall()


        # Zamknij połączenie z bazą danych
    conn.close()
    return render_template('sezon23-24.html', teams=teams, indexes=indexes, matches=matches)
@app.route('/archiwum/sezon22-23')
def sezon_22_23():
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
    WHERE
        m.date BETWEEN '2022-07-20 00:00:00' AND '2023-05-28 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()



    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))


    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.date BETWEEN '2022-07-20 00:00:00' AND '2023-05-28 00:00:00'
    ORDER BY
        matches.date DESC
    """)
    matches = cursor.fetchall()


        # Zamknij połączenie z bazą danych
    conn.close()
    return render_template('sezon22-23.html', teams=teams, indexes=indexes, matches=matches)
@app.route('/archiwum/sezon21-22')
def sezon_21_22():
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
    WHERE
        m.date BETWEEN '2021-07-20 00:00:00' AND '2022-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()



    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))


    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.date BETWEEN '2021-07-20 00:00:00' AND '2022-05-26 00:00:00'
    ORDER BY
        matches.date DESC
    """)
    matches = cursor.fetchall()


        # Zamknij połączenie z bazą danych
    conn.close()
    return render_template('sezon21-22.html', teams=teams, indexes=indexes, matches=matches)
@app.route('/archiwum/sezon20-21')
def sezon_20_21():
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
    WHERE
        m.date BETWEEN '2020-07-20 00:00:00' AND '2021-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()



    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))


    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.date BETWEEN '2020-07-20 00:00:00' AND '2021-05-26 00:00:00'
    ORDER BY
        matches.date DESC
    """)
    matches = cursor.fetchall()


        # Zamknij połączenie z bazą danych
    conn.close()
    return render_template('sezon20-21.html', teams=teams, indexes=indexes, matches=matches)
@app.route('/archiwum/sezon19-20')
def sezon_19_20():
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
    WHERE
        m.date BETWEEN '2019-07-20 00:00:00' AND '2020-05-26 00:00:00'
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """

    cursor.execute(query)
    teams = cursor.fetchall()



    #Utwórz listę indeksów
    indexes = list(range(1, len(teams) + 1))


    cursor.execute("""
    SELECT matches.date, teamsA.team AS teamA, matches.scoreA, matches.scoreB, teamsB.team AS teamB, teamsA.logo AS logoA, teamsB.logo AS logoB, matches.matchID
    FROM matches
    INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team
    INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team
    WHERE matches.date BETWEEN '2019-07-20 00:00:00' AND '2020-05-26 00:00:00'
    ORDER BY
        matches.date DESC
    """)
    matches = cursor.fetchall()


        # Zamknij połączenie z bazą danych
    conn.close()
    return render_template('sezon19-20.html', teams=teams, indexes=indexes, matches=matches)

@app.route('/statsA')
def show_statsA():
    matchID = request.args.get('matchID')
    
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Pobierz dane meczu z bazy danych
    cursor.execute("SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = ?", (matchID,))
    result = cursor.fetchone()
    

    cursor.execute("SELECT date, scoreA, scoreB, matchID from matches where matchID=?",(matchID,))
    match = cursor.fetchone()


    if result:
        teamA, teamB = result
    else:
        # Jeśli mecz nie istnieje, obsłuż to zgodnie z własnymi potrzebami
        return "Mecz nie istnieje"
    
    # Pobierz statystyki meczu z bazy danych
    cursor.execute("SELECT c.category_name, s.home_value, s.away_value FROM stats s JOIN categories c ON s.categoryid = c.categoryid WHERE s.match_id = ?", (matchID,))
    stats = cursor.fetchall()
    
    cursor.execute("SELECT logo from teams where team=?",(teamA,))
    logoA = cursor.fetchone()

    cursor.execute("SELECT logo from teams where team=?",(teamB,))
    logoB = cursor.fetchone()

    # Zamknij połączenie z bazą danych
    conn.close()

    # Wyświetl szablon HTML z danymi
    return render_template('statsA.html', teamA=teamA, teamB=teamB, stats=stats, match=match, logoA=logoA, logoB=logoB)
@app.route('/get_teams', methods=['POST'])
def get_teams():
    team_id = request.json.get('teamId')  # Pobranie ID wybranej drużyny z żądania POST
    print(team_id)
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    query = '''
    SELECT distinct teams.id_team, teams.team
    FROM teams
    JOIN matches ON teams.id_team = matches.teamA_id
    WHERE matches.date > '2023-07-01' AND teams.id_team != ?
    Order by teams.id_team asc;
    '''
    cursor.execute(query, (team_id))

    results = cursor.fetchall()

    teamsb = []  # Inicjalizacja listy graczy

    # Przetwarzanie wyników zapytania i dodanie do listy players
    for row in results:
        player_data = {
            'id': row[0],
            'name': row[1],
        }
        teamsb.append(player_data)

    # Zamykanie połączenia z bazą danych
    conn.close()

    return jsonify({'teamsb': teamsb}) 

@app.route('/generate_charts', methods=['POST'])
def generate_charts():
    team_id = request.json.get('teamId')
    team_id2 = request.json.get('teamId2')
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Zapytanie SQL do pobrania liczby bramek zdobytych i straconych przez wybrane drużyny
    query_teamA = f'''
        SELECT
            SUM(CASE
                WHEN m.teamA_id = {team_id} THEN m.scoreA
                ELSE m.scoreB
            END) AS Goals_Scored,
            SUM(CASE
                WHEN m.teamA_id = {team_id} THEN m.scoreB
                ELSE m.scoreA
            END) AS Goals_Conceded
        FROM matches m
        WHERE m.teamA_id = {team_id} OR m.teamB_id = {team_id}
    '''
    
    query_teamB = f'''
        SELECT
            SUM(CASE
                WHEN m.teamA_id = {team_id2} THEN m.scoreA
                ELSE m.scoreB
            END) AS Goals_Scored,
            SUM(CASE
                WHEN m.teamA_id = {team_id2} THEN m.scoreB
                ELSE m.scoreA
            END) AS Goals_Conceded
        FROM matches m
        WHERE m.teamA_id = {team_id2} OR m.teamB_id = {team_id2}
    '''

    cursor.execute(query_teamA)
    data_teamA = cursor.fetchone()

    cursor.execute(query_teamB)
    data_teamB = cursor.fetchone()

    conn.close()

    # Przygotowanie danych do wyświetlenia na wykresie kołowym dla drużyny A
    bramki_zdobyte_A = data_teamA[0]
    bramki_stracone_A = data_teamA[1]
    data_for_pie_chart_A = {
        'labels': ['Bramki Zdobyte', 'Bramki stracone'],
        'values': [bramki_zdobyte_A, bramki_stracone_A]
    }

    # Przygotowanie danych do wyświetlenia na wykresie kołowym dla drużyny B
    bramki_zdobyte_B = data_teamB[0]
    bramki_stracone_B = data_teamB[1]
    data_for_pie_chart_B = {
        'labels': ['Bramki Zdobyte', 'Bramki stracone'],
        'values': [bramki_zdobyte_B, bramki_stracone_B]
    }

    return jsonify({'teamA': data_for_pie_chart_A, 'teamB': data_for_pie_chart_B})

@app.route('/handle_user_action', methods=['POST'])
def handle_user_action():
    if request.method == 'POST':
        data = request.json  # Odbierz dane przesłane przez fetch
        user_id = data.get('userId')
        action = data.get('action')

        # Połączenie z bazą danych
        conn = sqlite3.connect('football_teams.db')
        cursor = conn.cursor()

        if action == 'x':
            cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
            conn.commit()
            conn.close()
            return jsonify({'message': f'Użytkownik o ID {user_id} został usunięty'})

        elif action == 'tick':
            cursor.execute("UPDATE users SET confirmed=? WHERE id=?", (1, user_id))
            conn.commit()
            conn.close()
            return jsonify({'message': f'Potwierdzono użytkownika o ID {user_id}'})

        else:
            conn.close()
            return jsonify({'message': 'Niepoprawna akcja'})
        
    return redirect(url_for('admin'))  

if __name__ == '__main__':
    app.run(debug=True)