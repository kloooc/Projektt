from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z wynikami
url = "https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa/wyniki/"
driver.get(url)

# Znajdź przycisk "Zobacz wszystkie" (zmień selektor na odpowiedni)
zobacz_button = driver.find_element(By.CSS_SELECTOR, 'event__more event__more--static')

# Kliknij przycisk "Zobacz wszystkie"
zobacz_button.click()


# Poczekaj, aż strona się załaduje (możesz dostosować czas)
driver.implicitly_wait(10)

# Pobierz źródło strony
page_source = driver.page_source

# Zamknij przeglądarkę
driver.quit()

# Przetwórz źródło strony za pomocą BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Znajdź divy o określonych klasach
match_divs = soup.find_all('div', class_='event__match event__match--static event__match--last event__match--twoLine')

# Przygotuj puste listy na daty, drużyny gości, drużyny przyjezdne, gole gości i gole przyjezdnych
dates = []
home_teams = []
away_teams = []
home_scores = []
away_scores = []

for match_div in match_divs:
    date_element = match_div.find('div', class_='event__time')
    date = date_element.text.strip() if date_element else "Brak daty"

    home_team_element = match_div.find('div', class_='event__participant event__participant--home') or match_div.find('div', class_='event__participant event__participant--home fontExtraBold')
    home_team = home_team_element.text.strip() if home_team_element else "Brak danych"

    # Znajdź drużynę gości w divie z klasami "event__participant" i "event__participant--away"
    away_team_element = match_div.find('div', class_='event__participant event__participant--away') or match_div.find('div', class_='event__participant event__participant--away fontExtraBold')
    away_team = away_team_element.text.strip() if away_team_element else "Brak danych"

    home_score_element = match_div.find('div', class_='event__score event__score--home')
    home_score = home_score_element.text.strip() if home_score_element else "Brak wyniku"

    away_score_element = match_div.find('div', class_='event__score event__score--away')
    away_score = away_score_element.text.strip() if away_score_element else "Brak wyniku"

    dates.append(date)
    home_teams.append(home_team)
    away_teams.append(away_team)
    home_scores.append(home_score)
    away_scores.append(away_score)


# Po zebraniu danych, możesz je teraz uporządkować i wydrukować
for i in range(len(dates)):
    print("Data:", dates[i])
    print("Drużyna gospodarzy:", home_teams[i])
    print("Drużyna przyjezdna:", away_teams[i])
    print("Gole gospodarzy:", home_scores[i])
    print("Gole przyjezdnych:", away_scores[i])
    print("\n")

#Otwórz połączenie do bazy danych
conn = sqlite3.connect('football_teams.db')

# Utwórz kursor do wykonywania zapytań SQL
cursor = conn.cursor()
cursor.execute('drop table matches')
# Utwórz tabelę "matches" z unikalnym identyfikatorem (matchID) i relacją do drużyn (teamA_id i teamB_id)
cursor.execute('''CREATE TABLE IF NOT EXISTS matches (
                  matchID INTEGER PRIMARY KEY,
                  teamA_id INTEGER,
                  teamB_id INTEGER,
                  scoreA INTEGER,
                  scoreB INTEGER,
                  date TEXT)''')

# Zatwierdź zmiany w bazie danych
conn.commit()

# Zamknij połączenie z bazą danych
conn.close()

# Po zebraniu danych, możesz teraz dodać je do tabeli "matches"
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Przygotuj puste listy na identyfikatory drużyn
team_ids = []

# Pobierz identyfikatory drużyn z bazy danych na podstawie ich nazw
for home_team_name in home_teams:
    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (home_team_name,))
    result = cursor.fetchone()
    if result:
        team_ids.append(result[0])
    else:
        team_ids.append(None)  # Lub coś innego, jeśli drużyna nie istnieje w bazie

# Po zebraniu identyfikatorów drużyn, możesz teraz wstawić dane do tabeli "matches"
for i in range(len(dates)):
    teamA_id = team_ids[i]
    teamB_name = away_teams[i]

    # Pobierz identyfikator drużyny B na podstawie jej nazwy
    cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB_name,))
    result = cursor.fetchone()
    if result:
        teamB_id = result[0]
    else:
        teamB_id = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

    match_values = (teamA_id, teamB_id, home_scores[i], away_scores[i], dates[i])

    # Wstaw dane do tabeli "matches"
    cursor.execute("INSERT INTO matches (teamA_id, teamB_id, scoreA, scoreB, date) VALUES (?, ?, ?, ?, ?)", match_values)


# Zatwierdź zmiany w bazie danych
conn.commit()

# Zamknij połączenie z bazą danych
conn.close()