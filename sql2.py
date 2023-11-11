import sqlite3
from datetime import datetime

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()



# Zapytanie SQL z użyciem obecnej daty i dokładnego porównywania dni, miesięcy, godzin i minut
cursor.execute('SELECT teamsA.team AS teamA, teamsB.team AS teamB FROM matches INNER JOIN teams AS teamsA ON matches.teamA_id = teamsA.id_team INNER JOIN teams AS teamsB ON matches.teamB_id = teamsB.id_team WHERE matchID = 303')

# Pobranie wyników zapytania
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)

# Zakończenie połączenia z bazą danych
conn.close()
