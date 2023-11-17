from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import sqlite3

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z wynikami
url = "https://www.flashscore.pl/pilka-nozna/polska/pko-bp-ekstraklasa/mecze/"
driver.get(url)

# Oczekiwanie na załadowanie strony
driver.implicitly_wait(10)

# Zamknij lub akceptuj komunikat o plikach cookie (jeśli istnieje)
try:
    cookie_button = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    cookie_button.click()
except:
    pass

# Przesuń stronę w dół, aż dojdziesz do przycisku "Zobacz wszystkie"
while True:
    try:
        zobacz_button = driver.find_element(By.CLASS_NAME, 'event__more.event__more--static')
        break
    except:
        actions = ActionChains(driver)
        actions.send_keys(Keys.PAGE_DOWN)
        actions.perform()

# Spróbuj kliknąć przycisk "Zobacz wszystkie" z pominięciem innych elementów, które mogą go zasłaniać
driver.execute_script("arguments[0].click();", zobacz_button)

# Oczekiwanie na załadowanie strony
driver.implicitly_wait(10)

# Pobierz źródło strony
page_source = driver.page_source

# Zamknij przeglądarkę
driver.quit()

# Przetwórz źródło strony za pomocą BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Znajdź divy o określonych klasach (jedna z dwóch klas)
match_divs = soup.find_all('div', class_=['event__match event__match--static event__match--scheduled event__match--twoLine'])

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

    match_values = (teamA_id, teamB_id, dates[i])

    # Wstaw dane do tabeli "matches"
    cursor.execute("INSERT INTO matches (teamA_id, teamB_id, date) VALUES (?, ?, ?)", match_values)


# Zatwierdź zmiany w bazie danych
conn.commit()

# Zamknij połączenie z bazą danych
conn.close()