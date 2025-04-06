import sqlite3
from config.bot_config import BotConfig


class UserRepository:
    def __init__(self):
        self.db_file = BotConfig.DB_FILE
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT DEFAULT 'ru',
            is_waiting_feedback INTEGER DEFAULT 0,
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    def get_user(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, first_name, last_name, language FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user

    def create_or_update_user(self, user_id, username, first_name, last_name, language='ru'):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO users (id, username, first_name, last_name, language)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, language))
        conn.commit()
        conn.close()

    def set_language(self, user_id, language):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET language = ? WHERE id = ?', (language, user_id))
        conn.commit()
        conn.close()

    def set_waiting_feedback(self, user_id, is_waiting=True):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET is_waiting_feedback = ? WHERE id = ?', (1 if is_waiting else 0, user_id))
        conn.commit()
        conn.close()

    def is_waiting_feedback(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT is_waiting_feedback FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result and result[0] == 1

    def get_user_language(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT language FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        conn.close()
        if result:
            return result[0]
        return BotConfig.DEFAULT_LANGUAGE