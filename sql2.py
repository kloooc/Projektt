import sqlite3
from datetime import datetime

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()



# Zapytanie SQL z użyciem obecnej daty i dokładnego porównywania dni, miesięcy, godzin i minut
cursor.execute('SELECT username, password, user_type FROM users WHERE username=1111')

# Pobranie wyników zapytania
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)

# Zakończenie połączenia z bazą danych
conn.close()
