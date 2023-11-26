import sqlite3

# Tworzenie połączenia z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Zapytanie SQL z złączeniem tabel i warunkiem daty meczu
query = '''
    SELECT distinct teams.id_team, teams.team
    FROM teams
    JOIN matches ON teams.id_team = matches.teamA_id
    WHERE matches.date > '2023-07-01'
    Order by teams.id_team asc;
'''

# Wykonanie zapytania
cursor.execute(query)

# Pobranie wszystkich wierszy wyniku
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)  # Wyświetlenie każdego wiersza (id_team, team, match_date)

# Zamknięcie połączenia z bazą danych
conn.close()
