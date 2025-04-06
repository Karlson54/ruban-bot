from telebot import types


class Keyboards:
    def __init__(self, lang='ua'):
        self.lang = lang
        self.button_texts = {
            'ua': {
                'catalog': 'Каталог',
                'info': 'Інформація',
                'help': 'Допомога',
                'order': 'Замовити',
                'back': 'Назад',
                'confirm': 'Підтвердити',
                'cancel': 'Скасувати',
                'add_item': 'Додати товар',
                'remove_item': 'Видалити товар',
                'view_orders': 'Перегляд замовлень',
                'cart': 'Кошик',
                'my_orders': 'Мої замовлення',
                'feedback': 'Залишити відгук',
                'settings': 'Налаштування'
            },
            'en': {
                'catalog': 'Catalog',
                'info': 'Info',
                'help': 'Help',
                'order': 'Order',
                'back': 'Back',
                'confirm': 'Confirm',
                'cancel': 'Cancel',
                'add_item': 'Add Item',
                'remove_item': 'Remove Item',
                'view_orders': 'View Orders',
                'cart': 'Cart',
                'my_orders': 'My Orders',
                'feedback': 'Leave Feedback',
                'settings': 'Settings'
            }
        }

    def set_language(self, lang):
        if lang in ['ua', 'en']:
            self.lang = lang

    def get_text(self, key):
        return self.button_texts.get(self.lang, self.button_texts['ua']).get(key, key)

    def main_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        keyboard.add(
            types.KeyboardButton(f"/catalog - {self.get_text('catalog')}"),
            types.KeyboardButton(f"/info - {self.get_text('info')}")
        )
        keyboard.add(
            types.KeyboardButton(f"/cart - {self.get_text('cart')}"),
            types.KeyboardButton(f"/orders - {self.get_text('my_orders')}")
        )
        keyboard.add(
            types.KeyboardButton(f"/help - {self.get_text('help')}"),
            types.KeyboardButton(f"/feedback - {self.get_text('feedback')}")
        )
        return keyboard

    def admin_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(self.get_text('add_item'), callback_data='admin_add'),
            types.InlineKeyboardButton(self.get_text('remove_item'), callback_data='admin_remove'),
            types.InlineKeyboardButton(self.get_text('view_orders'), callback_data='admin_view')
        )
        return keyboard

    def catalog_item_keyboard(self, item_id):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(self.get_text('order'), callback_data=f'order_{item_id}'),
            types.InlineKeyboardButton("🛒 " + self.get_text('cart'), callback_data='view_cart'),
            types.InlineKeyboardButton(self.get_text('back'), callback_data='back_to_catalog')
        )
        return keyboard

    def confirm_order_keyboard(self, item_id):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(self.get_text('confirm'), callback_data=f'confirm_order_{item_id}'),
            types.InlineKeyboardButton(self.get_text('cancel'), callback_data='cancel_order')
        )
        return keyboard
        
    def feedback_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("⭐ " + self.get_text('feedback'), callback_data='start_feedback'),
            types.InlineKeyboardButton(self.get_text('back'), callback_data='back_to_main')
        )
        return keyboard
        
    def cart_quick_access_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🛒 " + self.get_text('cart'), callback_data='view_cart'),
            types.InlineKeyboardButton("📜 " + self.get_text('my_orders'), callback_data='view_order_history')
        )
        return keyboard
        
    def settings_keyboard(self):
        languages = {
            'ua': '🇺🇦 Українська',
            'en': '🇬🇧 English'
        }
        
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for lang_code, lang_name in languages.items():
            keyboard.add(
                types.InlineKeyboardButton(lang_name, callback_data=f'set_lang_{lang_code}')
            )
        return keyboard