import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Usunięcie ograniczenia unikalności dla kolumn matchid i player_id w tabeli match_players
cursor.execute("DROP INDEX IF EXISTS idx_unique_match_players")
conn.commit()
# Usunięcie rekordów dla konkretnego player_id
player_id_to_delete = 1
cursor.execute("DELETE FROM match_players WHERE player_id = ?", (player_id_to_delete,))
conn.commit()

# Zamknięcie połączenia z bazą danych
conn.close()
