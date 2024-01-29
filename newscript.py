
import sqlite3
import hashlib

# Połączenie z bazą danych
conn = sqlite3.connect('football_teams.db')
cursor = conn.cursor()




# Dane do dodania
user_data = [
    ('john_doe', 'secure_password1', 'user', None, 1),
    ('jane_smith', 'strong_password2', 'user', None, 1),
    ('alex_walker', 'safe_password3', 'user', None, 0),
    ('emily_jones', 'secret_password4', 'user', None, 1),
    ('michael_davis', 'password123', 'user', None, 0),
    ('sarah_miller', 'pass_secure12', 'user', None, 1),
    ('chris_williams', 'mypassword567', 'user', None, 0),
    ('olivia_brown', 'p@ssword890', 'user', None, 1),
    ('daniel_jackson', 'securepass789', 'user', None, 1),
    ('lily_anderson', 'safe_pass432', 'user', None, 1),
    ('premium_user1', 'premiumpass1', 'user_premium', '2024-01-31', 1),
    ('premium_user2', 'premiumpass2', 'user_premium', '2024-02-15', 1),
    ('premium_user3', 'premiumpass3', 'user_premium', '2024-03-20', 1),
    ('premium_user4', 'premiumpass4', 'user_premium', '2024-04-10', 1)
]

# Haszowanie haseł i dodawanie danych do bazy
for user in user_data:
    username, password, user_type, premium_expiration_date, confirmed = user
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password, user_type, premium_expiration_date, confirmed) VALUES (?, ?, ?, ?, ?)",
                   (username, hashed_password, user_type, premium_expiration_date, confirmed))

# Zatwierdzenie zmian i zamknięcie połączenia z bazą danych
conn.commit()
conn.close()
