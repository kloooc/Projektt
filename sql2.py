import sqlite3

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Wykonanie zapytania SQL
cursor.execute("""
    SELECT
        t.id_team,
        t.team AS Team_Name,
        t.logo AS Team_Logo,
        COUNT(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 1
            ELSE NULL
        END) AS Wins,
        COUNT(CASE
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE NULL
        END) AS Draws,
        COUNT(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB < m.scoreA) THEN 1
            ELSE NULL
        END) AS Losses,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreB
        END) AS Goals_Scored,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreA
        END) AS Goals_Conceded,
        SUM(CASE
            WHEN (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 3
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE 0
        END) AS Points,
        SUM(CASE
            WHEN m.teamB_id = t.id_team THEN m.scoreB - m.scoreA
        END) AS Goal_Difference
    FROM
        teams AS t
    JOIN
        matches AS m
    ON
        t.id_team = m.teamA_id OR t.id_team = m.teamB_id
    GROUP BY
        t.id_team
    ORDER BY
        Points DESC, Goal_Difference DESC;
    """)

# Pobranie wyników zapytania
results = cursor.fetchall()

# Wyświetlenie wyników w konsoli
for row in results:
    print(row)  # Wyświetl każdy wiersz wynikowy w oddzielnym wierszu konsoli

# Zakończenie połączenia z bazą danych
conn.close()
