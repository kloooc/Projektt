import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT p.full_name
    FROM players p
    INNER JOIN match_players mp ON p.player_id = mp.player_id
    INNER JOIN matches m ON mp.matchid = m.matchid
    WHERE m.teamA_id = 2 AND mp.time_played > 0 AND m.matchid = 141
    """)

# Pobranie wyników zapytania
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row[0])  # Wyświetlenie wartości z kolumny full_name

# Zamknięcie połączenia z bazą danych
conn.close()
