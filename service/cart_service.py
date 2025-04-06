import sqlite3
from config.bot_config import BotConfig
from service.catalog_service import CatalogService


class CartService:
    def __init__(self):
        self.db_file = BotConfig.DB_FILE
        self.catalog_service = CatalogService()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

    def add_to_cart(self, user_id, item_id, quantity=1):
        # Check if item exists
        item = self.catalog_service.get_item_by_id(item_id)
        if not item:
            return False

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Check if item is already in cart
            cursor.execute(
                'SELECT quantity FROM cart WHERE user_id = ? AND item_id = ?',
                (user_id, item_id)
            )
            result = cursor.fetchone()

            if result:
                # Update quantity
                new_quantity = result[0] + quantity
                cursor.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND item_id = ?',
                    (new_quantity, user_id, item_id)
                )
            else:
                # Add new item to cart
                cursor.execute(
                    'INSERT INTO cart (user_id, item_id, quantity) VALUES (?, ?, ?)',
                    (user_id, item_id, quantity)
                )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding to cart: {e}")
            return False

    def remove_from_cart(self, user_id, item_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM cart WHERE user_id = ? AND item_id = ?',
                (user_id, item_id)
            )
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error removing from cart: {e}")
            return False

    def update_item_quantity(self, user_id, item_id, quantity_change):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            # Get current quantity
            cursor.execute(
                'SELECT quantity FROM cart WHERE user_id = ? AND item_id = ?',
                (user_id, item_id)
            )
            result = cursor.fetchone()

            if not result:
                conn.close()
                return False

            current_quantity = result[0]
            new_quantity = current_quantity + quantity_change

            if new_quantity <= 0:
                # Remove item if quantity becomes 0 or negative
                cursor.execute(
                    'DELETE FROM cart WHERE user_id = ? AND item_id = ?',
                    (user_id, item_id)
                )
            else:
                # Update quantity
                cursor.execute(
                    'UPDATE cart SET quantity = ? WHERE user_id = ? AND item_id = ?',
                    (new_quantity, user_id, item_id)
                )

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating cart quantity: {e}")
            return False

    def get_cart_items(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
            SELECT c.item_id, cat.name, cat.price, c.quantity
            FROM cart c
            JOIN catalog cat ON c.item_id = cat.id
            WHERE c.user_id = ?
            ''', (user_id,))

            items = []
            for row in cursor.fetchall():
                item_id, name, price, quantity = row
                items.append({
                    'item_id': item_id,
                    'name': name,
                    'price': price,
                    'quantity': quantity
                })

            conn.close()
            return items
        except Exception as e:
            print(f"Error getting cart items: {e}")
            return []

    def get_cart_items_count(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()

            cursor.execute('''
            SELECT SUM(quantity) FROM cart WHERE user_id = ?
            ''', (user_id,))

            result = cursor.fetchone()[0]
            conn.close()

            return result if result else 0
        except Exception as e:
            print(f"Error getting cart count: {e}")
            return 0

    def clear_cart(self, user_id):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM cart WHERE user_id = ?', (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing cart: {e}")
            return False

    def format_cart_for_display(self, cart_items, lang='ua'):
        if not cart_items:
            if lang == 'ua':
                return "🛒 Ваш кошик порожній"
            else:
                return "🛒 Your cart is empty"

        total = sum(item['price'] * item['quantity'] for item in cart_items)

        if lang == 'ua':
            message = "🛒 Ваш кошик:\n\n"
            for item in cart_items:
                message += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} грн\n"
            message += f"\n💰 Загальна сума: {total} грн"
        else:
            message = "🛒 Your cart:\n\n"
            for item in cart_items:
                message += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} UAH\n"
            message += f"\n💰 Total amount: {total} UAH"

        return message