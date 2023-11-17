from selenium import webdriver
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import time
from selenium.webdriver.common.by import By

# Przygotowanie i otwarcie strony z informacjami o zawodniku
driver = webdriver.Chrome()
driver.get("https://www.flashscore.pl/zawodnik/zohore-kenneth/p44hk6oi/")
time.sleep(3)

# Kliknięcie przycisku "ZOBACZ WSZYSTKIE MECZE"
see_all_button = driver.find_element(By.CLASS_NAME, 'lmTable__href')
see_all_button.click()
time.sleep(3)

# Pobranie źródła strony
page_source = driver.page_source

# Zamknięcie przeglądarki
driver.quit()

# Analiza źródła strony za pomocą BeautifulSoup
data = BeautifulSoup(page_source, 'html.parser')

# Znalezienie listy meczów w divie z odpowiednią klasą
matches_div = data.find('div', class_='lmTable')
matches_data = []
if matches_div:
    # Znalezienie wszystkich meczów wewnątrz diva z listą meczów
    all_matches = matches_div.find_all('div', class_='lmTable__row lmTable__row--soccer')

    for match in all_matches:
        # Sprawdzenie warunku dla <a> o klasie lmTable__competitionHref
        competition = match.find('a', class_='lmTable__competitionHref')
        if competition and competition.text.strip() == "EKS":
            # Sprawdzenie warunku dla diva o klasie lmTable__date
            date_element = match.find('div', class_='lmTable__date')
            if date_element:
                match_date = date_element.text.strip()
                
                # Konwersja daty do obiektu typu datetime
                parsed_date = datetime.strptime(match_date, "%d.%m.%y")
                
                # Utworzenie daty granicznej (1 lipca 2023)
                boundary_date = datetime(2023, 7, 1)
                
                # Warunek dla daty - sprawdzenie czy data meczu jest po 1 lipca 2023
                if parsed_date > boundary_date:
                    # Znalezienie drużyn teamA i teamB wewnątrz diva z pojedynczym meczem
                    teams_info = match.find_all('div', class_='lmTable__team')

                    if len(teams_info) >= 2:
                        team_a_name = teams_info[0].text.strip()
                        team_b_name = teams_info[1].text.strip()

                    

                        # Pozostała część kodu pozostaje bez zmian
                        # Połączenie z bazą danych
                        conn = sqlite3.connect('football_teams.db')
                        cursor = conn.cursor()

                        # Pobranie id_teamu dla teamA
                        cursor.execute("SELECT id_team FROM teams WHERE team=?", (team_a_name,))
                        team_a_id = cursor.fetchone()

                        # Pobranie id_teamu dla teamB
                        cursor.execute("SELECT id_team FROM teams WHERE team=?", (team_b_name,))
                        team_b_id = cursor.fetchone()

                        # Sprawdzenie znalezienia id_teamu dla teamA i teamB
                        if team_a_id and team_b_id:
                            team_a_id = team_a_id[0]
                            team_b_id = team_b_id[0]
                            
                            # Znalezienie matchID z tabeli matches porównując teamA_id i teamB_id
                            cursor.execute("SELECT matchID FROM matches WHERE teamA_id=? AND teamB_id=?", (team_a_id, team_b_id))
                            match_id = cursor.fetchone()

                            if match_id:
                                print(f"Data meczu: {match_date}")
                                print(f"Znaleziono matchID dla teamA: {team_a_name}, teamB: {team_b_name} - MatchID: {match_id[0]}")
                                time_played = 0
                                goals = 0
                                assists = 0
                                yellow_card = 0
                                red_card = 0

                                icons = match.find_all('div', class_='lmTable__iconText')

                                # Znalezienie dodatkowych informacji z divów o klasie lmTable__icon
                                if len(icons) >= 5:
                                    time_played = icons[0].text.strip()  # Pobranie wartości
                                    time_played = time_played[:-1]  # Usunięcie ostatniego znaku
                                    goals = icons[1].text.strip() 
                                    assists = icons[2].text.strip() 
                                    yellow_card = icons[3].text.strip() 
                                    red_card = icons[4].text.strip() 
                                    # Dodawanie danych meczu do listy matches_data
                                    matches_data.append((match_id[0], 25, time_played, goals, assists, yellow_card, red_card))

                                    print(f"time_played: {time_played}, goals: {goals}, assists: {assists}, yellow_card: {yellow_card}, red_card: {red_card}")
                                absence = match.find_all('div', class_='lmTable__absence')
                                if absence:
                                    time_played = 0
                                    oals = 0
                                    assists= 0
                                    yellow_card=0
                                    red_card=0
                                    matches_data.append((match_id[0], 25, time_played, goals, assists, yellow_card, red_card))

                                    print(f"time_played: {time_played}, goals: {goals}, assists: {assists}, yellow_card: {yellow_card}, red_card: {red_card}")

                            else:
                                print("Nie znaleziono pasującego MatchID")
                        else:
                            print("Nie znaleziono id_teamu dla teamA lub teamB")

                        # Zamknięcie połączenia z bazą danych
                        conn.close()
                    else:
                        print("Nie znaleziono wystarczającej liczby informacji o drużynach w meczu")
                else:
                    print("Mecz znajduje się przed 01.07.23")
            else:
                print("Brak danych o dacie dla meczu")
        else:
            print("Mecz nie spełnia warunków dotyczących ligi")
    conn = sqlite3.connect('football_teams.db')
    cursor = conn.cursor()

    # Wstawienie danych z matches_data do tabeli match_players
    query = "INSERT INTO match_players (matchid, player_id, time_played, goals, assists, yellow_card, red_card) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.executemany(query, matches_data)
    conn.commit()

    print("Dane zostały dodane do tabeli match_players.")

    # Zamknięcie połączenia z bazą danych
    conn.close()
else:
    print("Nie znaleziono diva z listą meczów")
