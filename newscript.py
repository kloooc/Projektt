import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

id_team = 18
for player_id in range(425,452):
    cursor.execute("INSERT INTO teams_players (id_team, player_id) VALUES (?, ?)", (id_team, player_id))
# Zatwierdź wszystkie zmiany
conn.commit()

# Zakończenie połączenia z bazą danych
conn.close()
