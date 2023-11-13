import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

try:
    # Usuń wszystkie rekordy z tabeli stats
    cursor.execute('DELETE FROM stats')
    conn.commit()
    print("Wyczyszczono tabelę stats.")
except sqlite3.Error as e:
    print("Wystąpił błąd SQLite:", e)

# Zakończenie połączenia z bazą danych
conn.close()
