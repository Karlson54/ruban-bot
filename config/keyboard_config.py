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
                'view_orders': 'Перегляд замовлень'
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
                'view_orders': 'View Orders'
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
            types.KeyboardButton(f"/info - {self.get_text('info')}"),
            types.KeyboardButton(f"/help - {self.get_text('help')}")
        )
        return keyboard

    def admin_keyboard(self):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(self.get_text('add_item'), callback_data='admin_add_item'),
            types.InlineKeyboardButton(self.get_text('remove_item'), callback_data='admin_remove_item'),
            types.InlineKeyboardButton(self.get_text('view_orders'), callback_data='admin_view_orders')
        )
        return keyboard

    def catalog_item_keyboard(self, item_id):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(self.get_text('order'), callback_data=f'order_{item_id}'),
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