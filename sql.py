import sqlite3

# Połącz się z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()

# Wykonaj zapytanie SQL
cursor.execute("""
    SELECT
        t.id_team,
        t.team AS Team_Name,
        t.logo AS Team_Logo,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 1
            ELSE NULL
        END) AS Wins,
        COUNT(CASE
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE NULL
        END) AS Draws,
        COUNT(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA < m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB < m.scoreA) THEN 1
            ELSE NULL
        END) AS Losses,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA
            ELSE m.scoreB
        END) AS Goals_Scored,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreB
            ELSE m.scoreA
        END) AS Goals_Conceded,
        SUM(CASE
            WHEN (m.teamA_id = t.id_team AND m.scoreA > m.scoreB) OR (m.teamB_id = t.id_team AND m.scoreB > m.scoreA) THEN 3
            WHEN m.scoreA = m.scoreB THEN 1
            ELSE 0
        END) AS Points,
        SUM(CASE
            WHEN m.teamA_id = t.id_team THEN m.scoreA - m.scoreB
            ELSE m.scoreB - m.scoreA
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
        Points DESC, Goal_Difference DESC
    """)

# Pobierz wyniki z kursora
results = cursor.fetchall()

# Zamknij połączenie z bazą danych
conn.close()

# Wyświetl wyniki w konsoli
for row in results:
    print("Team ID:", row[0])
    print("Team Name:", row[1])
    print("Team Logo:", row[2])
    print("Wins:", row[3])
    print("Draws:", row[4])
    print("Losses:", row[5])
    print("Goals Scored:", row[6])
    print("Goals Conceded:", row[7])
    print("Points:", row[8])
    print("Goal Difference:", row[9])
    print("Goal Difference:", row[3]+row[4]+row[5])
    print("\n")
