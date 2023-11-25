import sqlite3

# Utwórz połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Zapytanie SQL z parametrem player_id
player_id = 1  # Zamiast 123 podaj odpowiednie player_id
query = '''
    SELECT m.matchID, t1.team AS teamA_name, t2.team AS teamB_name, t1.logo AS teamA_logo, t2.logo AS teamB_logo,
           m.ScoreA, m.ScoreB, m.date,
           mp.player_id, mp.time_played, mp.goals, mp.assists, mp.yellow_card, mp.red_card
    FROM matches AS m
    JOIN match_players AS mp ON m.matchID = mp.matchID
    JOIN teams AS t1 ON m.teamA_id = t1.id_team
    JOIN teams AS t2 ON m.teamB_id = t2.id_team
    WHERE m.ScoreA IS NOT NULL AND m.ScoreB IS NOT NULL AND mp.player_id = ?
'''

# Wykonaj zapytanie z parametrem player_id
cursor.execute(query, (player_id,))

# Pobierz wyniki zapytania
matches_and_players = cursor.fetchall()

# Wyświetl pobrane dane
for row in matches_and_players:
    print(row)  # Wypisanie danych każdego rekordu
