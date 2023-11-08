import sqlite3
from datetime import datetime

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Uzyskanie obecnej daty i godziny w formacie "dd.mm. HH:MM"
current_datetime = datetime.now().strftime('%d.%m. %H:%M')

# Wyodrębnienie dnia, miesiąca, godziny i minut z obecnej daty
current_day = datetime.now().strftime('%d')
current_month = datetime.now().strftime('%m')
current_hour = datetime.now().strftime('%H')
current_minute = datetime.now().strftime('%M')

# Zapytanie SQL z użyciem obecnej daty i dokładnego porównywania dni, miesięcy, godzin i minut
cursor.execute("SELECT * from stats")

# Pobranie wyników zapytania
results = cursor.fetchall()

# Wyświetlenie wyników
for row in results:
    print(row)

# Zakończenie połączenia z bazą danych
conn.close()
