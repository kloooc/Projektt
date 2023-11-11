import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

try:
    # Usuń rekordy z tabeli stats, gdzie matchID=113
    cursor.execute('DELETE FROM stats WHERE match_id = ?', (113,))
    conn.commit()
    print("Usunięto rekordy z tabeli stats dla matchID=113.")
except sqlite3.Error as e:
    print("Wystąpił błąd SQLite:", e)

# Zakończenie połączenia z bazą danych
conn.close()