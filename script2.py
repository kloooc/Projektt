import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3
import sys

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z wynikami
driver.get("https://www.flashscore.pl/mecz/boyXTEjg/#/szczegoly-meczu/szczegoly-meczu")

# Poczekaj, aż strona się załaduje (możesz dostosować czas)
driver.implicitly_wait(10)

# Pobierz źródło strony
page_source = driver.page_source

# Zamknij przeglądarkę
driver.quit()

# Przetwórz źródło strony za pomocą BeautifulSoup
soup = BeautifulSoup(page_source, 'html.parser')

# Połącz się z bazą danych przed przetwarzaniem strony
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

date_divs = soup.find_all('div', class_='duelParticipant__startTime')

# Przetwarzaj i wydrukowuj zawartość wszystkich znalezionych divów
for date_div in date_divs:
    date_text = date_div.text.strip()
    print("Oryginalny tekst daty:", date_text)

    try:
        # Pobierz nową datę i godzinę z tekstu
        new_date_obj = datetime.datetime.strptime(date_text, "%d.%m.%Y %H:%M")
        print("Przekształcona data:", new_date_obj)
    except ValueError as e:
        print("Błąd konwersji daty:", e)

    # Tutaj zaczynają się zapytania SQL
    teams = []

    participant_divs = soup.find_all('div', class_='participant__participantName participant__overflow')

    for participant_div in participant_divs:
        team_name = participant_div.text.strip() if participant_div else "Brak danych"
        teams.append(team_name)

    for i, team_name in enumerate(teams):
        print(f"Drużyna {i + 1}: {team_name}")

        # Nazwy drużyn
        teamA = teams[0]
        teamB = teams[1]

        cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamA,))
        result = cursor.fetchone()
        if result:
            teamA_id = result[0]
        else:
            teamA_id = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

        cursor.execute("SELECT id_team FROM teams WHERE team = ?", (teamB,))
        result = cursor.fetchone()
        if result:
            teamB_id = result[0]
        else:
            teamB_id = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

        # Tutaj masz teraz identyfikatory drużyn teamA_id i teamB_id
        print(f"Identyfikator drużyny A: {teamA_id}")
        print(f"Identyfikator drużyny B: {teamB_id}")

        cursor.execute("SELECT matchID FROM matches WHERE teamA_id = ? AND teamB_id = ?", (teamA_id, teamB_id))
        result = cursor.fetchone()
        if result:
            matchID = result[0]
        else:
            matchID = None  # Lub coś innego, jeśli drużyna nie istnieje w bazie

        print(f"Match id: {matchID}")

        cursor.execute("UPDATE matches SET date = ? WHERE matchID = ?", (new_date_obj, matchID))

# Zatwierdź zmiany w bazie danych
conn.commit()

# Zamknij połączenie z bazą danych
conn.close()
