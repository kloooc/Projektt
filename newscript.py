
import sqlite3
import hashlib

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()



# Wykonanie zapytania SQL
cursor.execute("SELECT * FROM matches WHERE teamA_id = 15 AND teamB_id = 4")

# Pobranie wyników
results = cursor.fetchall()

# Wypisanie wyników
for row in results:
    matchID, teamA_id, teamB_id, scoreA, scoreB, date = row
    print(f"Match ID: {matchID}, Team A ID: {teamA_id}, Team B ID: {teamB_id}, Score A: {scoreA}, Score B: {scoreB}, Date: {date}")

# Zamknięcie połączenia
conn.close()