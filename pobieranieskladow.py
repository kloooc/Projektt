import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import sqlite3
import sys

# Inicjalizacja przeglądarki (np. Google Chrome)
driver = webdriver.Chrome()

# Otwarcie strony z wynikami
driver.get("https://www.flashscore.pl/druzyna/lks-lodz/ShUKWHDG/sklad/")

# Poczekaj, aż strona się załaduje (możesz dostosować czas)
driver.implicitly_wait(10)

# Pobierz źródło strony
page_source = driver.page_source

# Zamknij przeglądarkę
driver.quit()

data = BeautifulSoup(page_source, 'html.parser')

# Znajdź div o klasie 'lineup lineup--soccer'
div_lineup = data.find('div', class_='lineup lineup--soccer')

# Nawiązanie połączenia z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Pobranie zawartości kolumny 'position_name' z tabeli 'positions'
cursor.execute("SELECT position_name FROM positions")
positions_data = cursor.fetchall()

# Mapowanie tytułów sekcji na nazwy pozycji
positions_mapping = {
    'Bramkarze': 'bramkarz',
    'Obrońcy': 'obronca',
    'Pomocnicy': 'pomocnik',
    'Napastnicy': 'napastnik',
    'Trener': 'trener'
}

if div_lineup:
    div_row_elements = div_lineup.find_all('div', class_='lineup__row')

    for div_row in div_row_elements:
        lineup_title = div_row.find_previous_sibling('div', class_='lineup__title')
        links = div_row.find_all('a', class_='lineup__cell lineup__cell--name')

        for link in links:
            player_position = None
            if lineup_title:
                lineup_text = lineup_title.text.strip()
                if lineup_text in positions_mapping:
                    player_position = positions_mapping[lineup_text]

                    # Pobranie imienia i nazwiska z linku
                    full_name = link.text.strip()
                    
                    print(f"Dodaję zawodnika: {full_name} na pozycji: {player_position}")

                    cursor.execute("INSERT INTO players (full_name) VALUES (?)", (full_name,))
                    conn.commit()  # Zatwierdź transakcję

                    player_id = cursor.lastrowid

                    cursor.execute("SELECT position_id FROM positions WHERE position_name = ?", (player_position,))
                    position_id = cursor.fetchone()[0]

                    cursor.execute("INSERT INTO player_positions (player_id, position_id) VALUES (?, ?)", (player_id, position_id))
                    conn.commit()  # Zatwierdź transakcję

                    if player_position:
                        print(f"Pozycja znaleziona: {player_position}")
                    else:
                        print("Brak pasującej pozycji w bazie danych")
                print(f"Zawodnik: {full_name} dodany")

else:
    print('Nie znaleziono diva lineup lineup--soccer')

# Zamknięcie połączenia z bazą danych
conn.close()
