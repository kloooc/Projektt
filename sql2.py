import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Wykonanie zapytania SQL wybierającego wszystkie dane z tabeli users
cursor.execute("SELECT * FROM users")

# Pobranie wszystkich rekordów z wyniku zapytania
users = cursor.fetchall()

# Wyświetlenie wszystkich rekordów z tabeli users
for user in users:
    print(user)

# Zakończenie połączenia z bazą danych
conn.close()
