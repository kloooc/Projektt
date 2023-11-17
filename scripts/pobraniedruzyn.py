import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z tabelą
url = "https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa-2019-2020/tabela/#/v5p2SRke/table/overall"
driver.get(url)

# Poczekaj, aż strona się załaduje (możesz dostosować czas)
driver.implicitly_wait(10)

# Znajdź elementy <a> z klasą "tableCellParticipant__name"
elements = driver.find_elements(By.CSS_SELECTOR, '.tableCellParticipant__name')

# Znajdź również elementy <img> z klasą "participant__image" dla logo drużyn
logo_elements = driver.find_elements(By.CSS_SELECTOR, '.participant__image')

# Pobierz tekst z elementów <a> i linki do logo z elementów <img>
# Pobierz tekst z elementów <a> i linki do logo z elementów <img>
team_data = [(element[0].text, element[1].get_attribute('src')) for element in zip(elements, logo_elements)]

# Zamknij przeglądarkę
driver.quit()

for data in team_data:
    team_name, logo_url = data
    print("Nazwa drużyny:", team_name)
    print("URL logo:", logo_url)
    print("\n")

# Utworzenie bazy danych (jeśli nie istnieje)
conn = sqlite3.connect('football_teams.db')

# Utworzenie kursora do pracy z bazą danych
cursor = conn.cursor()



# Utworzenie tabeli "teams" (jeśli nie istnieje) z polem "team" jako unikalnym kluczem
cursor.execute('''CREATE TABLE IF NOT EXISTS teams (
                  id_team INTEGER PRIMARY KEY,
                  team TEXT UNIQUE,
                  logo TEXT)''')


# Wstawienie nazw drużyn i linków do logo do tabeli
# Wstaw nazwy drużyn i linki do logo do tabeli "teams"
for team_name, logo_url in team_data:
    cursor.execute("INSERT OR IGNORE INTO teams (team, logo) VALUES (?, ?)", (team_name, logo_url))


# Zatwierdzenie zmian w bazie danych
conn.commit()

# Zakończenie pracy z bazą danych
conn.close()

# Otwórz połączenie do bazy danych
conn = sqlite3.connect('football_teams.db')

# Utwórz kursor do wykonywania zapytań SQL
cursor = conn.cursor()

# Wykonaj zapytanie SQL, aby wyświetlić zawartość tabeli
cursor.execute("SELECT * FROM teams")

# Pobierz wszystkie wiersze z wyników zapytania
rows = cursor.fetchall()

# Wyświetl wyniki
for row in rows:
    print(row)

# Zamknij połączenie do bazy danych
conn.close()
