import sqlite3
from config import DATABASE_PATH
from .token_crypto import encrypt_token, decrypt_token

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            encrypted_refresh_token BLOB,
            expiry TEXT,
            timezone TEXT DEFAULT 'Europe/Moscow'
        )
    ''')
    conn.commit()
    conn.close()

def save_tokens(user_id, refresh_token, expiry):
    encrypted = encrypt_token(refresh_token)
    conn = get_connection()
    conn.execute('''
        INSERT OR REPLACE INTO users (user_id, encrypted_refresh_token, expiry, timezone)
        VALUES (?, ?, ?, COALESCE((SELECT timezone FROM users WHERE user_id=?), 'Europe/Moscow'))
    ''', (user_id, encrypted, expiry, user_id))
    conn.commit()
    conn.close()

def get_refresh_token(user_id):
    conn = get_connection()
    row = conn.execute('SELECT encrypted_refresh_token FROM users WHERE user_id=?', (user_id,)).fetchone()
    conn.close()
    if row and row['encrypted_refresh_token']:
        return decrypt_token(row['encrypted_refresh_token'])
    return None

def get_timezone(user_id):
    conn = get_connection()
    row = conn.execute('SELECT timezone FROM users WHERE user_id=?', (user_id,)).fetchone()
    conn.close()
    return row['timezone'] if row else 'Europe/Moscow'

def set_timezone(user_id, tz):
    conn = get_connection()
    conn.execute('UPDATE users SET timezone=? WHERE user_id=?', (tz, user_id))
    conn.commit()
    conn.close()

def has_token(user_id):
    return get_refresh_token(user_id) is not None