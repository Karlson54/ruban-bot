import sqlite3
from config.bot_config import BotConfig

class CatalogRepository:
    def __init__(self):
        self.db_file = BotConfig.DB_FILE
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS catalog (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def get_all_items(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, description, price FROM catalog')
        items = cursor.fetchall()
        conn.close()
        return items

    def get_item_by_id(self, item_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, description, price FROM catalog WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        conn.close()
        return item

    def add_item(self, name, description, price):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO catalog (name, description, price) VALUES (?, ?, ?)',
                      (name, description, price))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id

    def remove_item(self, item_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM catalog WHERE id = ?', (item_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success