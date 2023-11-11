from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3
import sys

# Pobierz link z argumentów wiersza polecenia
link = sys.argv[1]

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z wynikami
driver.get(link)

# Poczekaj, aż strona się załaduje (możesz dostosować czas)
driver.implicitly_wait(10)

# Pobierz źródło strony
page_source = driver.page_source

# Zamknij przeglądarkę
driver.quit()
# Przetwórz źródło strony za pomocą BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')
score_divs = soup.find_all('div', class_='detailScore__wrapper')

score=[]

# Iteracja po elementach score_divs i dodawanie przyciętych wyników do listy score
for score_div in score_divs:
    score_text = score_div.text.strip() if score_div else "Brak danych"
    # Rozdzielenie wyniku na dwie liczby
    scores = score_text.split('-')
    # Dodaj wyniki do listy
    score.extend(scores)

# Wydrukuj zebrane wyniki
for i, result in enumerate(score):
    print(f"Wynik {i+1}: {result}")



# Znajdź divy o określonych klasach
participant_divs = soup.find_all('div', class_='participant__participantName participant__overflow')

# Przygotuj puste listy na nazwy drużyn
teams = []

for participant_div in participant_divs:
    team_name = participant_div.text.strip() if participant_div else "Brak danych"
    teams.append(team_name)

# Wydrukuj zebrane dane
for i, team_name in enumerate(teams):
    print(f"Drużyna {i+1}: {team_name}")

category_divs = soup.find_all('div', {'class': '_categoryName_11si3_5'})
home_divs = soup.find_all('div', {'class': '_value_v26p1_5 _homeValue_v26p1_10'})
away_divs = soup.find_all('div', {'class': '_value_v26p1_5 _awayValue_v26p1_14'})

# Przetwarzaj i wydrukowuj zawartość wszystkich znalezionych divów
for category_div, home_div, away_div in zip(category_divs, home_divs, away_divs):
    print("Kategoria:", category_div.text.strip())
    print("Home:", home_div.text.strip())
    print("Away:", away_div.text.strip())
    print("\n")


# Połącz się z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()



cursor.execute('''CREATE TABLE IF NOT EXISTS stats (
    match_id INTEGER,
    category TEXT ,
    home_value TEXT,
    away_value TEXT,
    FOREIGN KEY (match_id) REFERENCES matches (matchID)
)''')


# Nazwy drużyn
teamA = teams[0]
teamB = teams[1]

# Pobierz identyfikator drużyny A na podstawie jej nazwy
cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamA,))
result = cursor.fetchone()
if result:
    teamA_id = result[0]
else:
    teamA_id = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

# Pobierz identyfikator drużyny B na podstawie jej nazwy
cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB,))
result = cursor.fetchone()
if result:
    teamB_id = result[0]
else:
    teamB_id = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

# Tutaj masz teraz identyfikatory drużyn teamA_id i teamB_id
print(f"Identyfikator drużyny A: {teamA_id}")
print(f"Identyfikator drużyny B: {teamB_id}")

cursor.execute("SELECT matchID FROM matches WHERE teamA_id = ? AND teamB_id = ?", (teamA_id,teamB_id))
result = cursor.fetchone()
if result:
    matchID = result[0]
else:
    matchID = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

print(f"Match id: {matchID}")


for category, home_value, away_value in zip(category_divs, home_divs, away_divs):
    category_text = category.text.strip()
    home_value_text = home_value.text.strip()
    away_value_text = away_value.text.strip()


    # Aktualizacja tabeli stats 
    cursor.execute("INSERT INTO stats (match_id, category, home_value, away_value) VALUES (?, ?, ?, ?)",
                   (matchID, category_text, home_value_text, away_value_text))
    conn.commit
    print("Aktualizacja została pomyślnie wykonana.")

    # Aktualizacja tabeli matches o wyniki
    cursor.execute('UPDATE matches SET scoreA = ?, scoreB = ? WHERE matchID = ?', (score[0], score[1], matchID))
    conn.commit()

# Zatwierdź zmiany w bazie danych
conn.commit()

# Zamknij połączenie z bazą danych
conn.close()

