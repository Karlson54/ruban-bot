import sqlite3
import os
from config.bot_config import BotConfig


def init_database():
    """Initialize all database tables"""

    # Create database file if it doesn't exist
    if not os.path.exists(BotConfig.DB_FILE):
        conn = sqlite3.connect(BotConfig.DB_FILE)
        conn.close()
        print(f"Created database file: {BotConfig.DB_FILE}")

    conn = sqlite3.connect(BotConfig.DB_FILE)
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        language TEXT DEFAULT 'ua',
        is_waiting_feedback INTEGER DEFAULT 0,
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create catalog table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS catalog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price REAL NOT NULL
    )
    ''')

    # Create orders table
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

    # Create cart table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        item_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, item_id)
    )
    ''')

    # Create feedback table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Insert sample products if catalog is empty
    cursor.execute('SELECT COUNT(*) FROM catalog')
    count = cursor.fetchone()[0]

    if count == 0:
        sample_products = [
            ('Смартфон XiaoPro', 'Потужний смартфон з 8 Гб RAM та 128 Гб пам\'яті', 8999.99),
            ('Навушники AirBeats', 'Бездротові навушники з шумопоглинанням', 2499.50),
            ('Смарт-годинник FitTime', 'Водонепроникний годинник з моніторингом здоров\'я', 1899.00),
            ('Ноутбук UltraSlim', 'Легкий і потужний ноутбук для роботи', 22999.00),
            ('Зовнішній акумулятор PowerMax', 'Потужність 20000 mAh, швидка зарядка', 999.99)
        ]

        cursor.executemany(
            'INSERT INTO catalog (name, description, price) VALUES (?, ?, ?)',
            sample_products
        )
        print(f"Added {len(sample_products)} sample products to catalog")

    conn.commit()
    conn.close()
    print("Database initialization completed successfully")