import sqlite3
from config.bot_config import BotConfig


class OrderRepository:
    def __init__(self):
        self.db_file = BotConfig.DB_FILE
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            user_name TEXT,
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            price REAL NOT NULL,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        conn.close()

    def create_order(self, user_id, user_name, item_id, item_name, price):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO orders (user_id, user_name, item_id, item_name, price)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, user_name, item_id, item_name, price))
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return order_id

    def get_all_orders(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, user_id, user_name, item_name, price, status, created_at 
        FROM orders ORDER BY created_at DESC
        ''')
        orders = cursor.fetchall()
        conn.close()
        return orders

    def get_user_orders(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
        SELECT id, item_name, price, status, created_at 
        FROM orders WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        orders = cursor.fetchall()
        conn.close()
        return orders
