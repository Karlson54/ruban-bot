class Messages:
    def __init__(self):
        self.messages = {
            'ua': {
                'start': 'Ласкаво просимо до нашого магазину! Використовуйте /help для списку команд.',
                'help': 'Доступні команди:\n'
                        '/start - Почати роботу з ботом\n'
                        '/help - Список команд\n'
                        '/info - Інформація про бота\n'
                        '/catalog - Каталог товарів\n'
                        '/order - Оформити замовлення\n'
                        '/feedback - Залишити відгук',
                'info': 'Цей бот створений для демонстрації інтернет-магазину в Telegram. Тут ви можете переглядати каталог товарів і оформляти замовлення.',
                'catalog_empty': 'Каталог порожній.',
                'item_not_found': 'Товар не знайдено.',
                'order_created': 'Ваше замовлення успішно оформлене! Дякуємо за покупку.',
                'feedback_prompt': 'Будь ласка, напишіть ваш відгук у наступному повідомленні:',
                'feedback_received': 'Дякуємо за ваш відгук!',
                'admin_menu': 'Меню адміністратора:',
                'not_admin': 'У вас немає прав адміністратора.',
                'add_item_prompt': 'Введіть дані про товар у форматі:\nНазва|Опис|Ціна',
                'item_added': 'Товар успішно додано.',
                'remove_item_prompt': 'Виберіть товар для видалення:',
                'item_removed': 'Товар успішно видалено.',
                'invalid_format': 'Невірний формат введення.',
                'orders_empty': 'Список замовлень порожній.',
                'hello': 'Привіт! Чим я можу допомогти вам сьогодні?',
                'available_items': 'Скористайтеся командою /catalog щоб побачити доступні товари.',
                'how_to_order': 'Щоб зробити замовлення, виберіть товар у каталозі і натисніть кнопку "Замовити".'
            },
            'en': {
                'start': 'Welcome to our store! Use /help for a list of commands.',
                'help': 'Available commands:\n'
                        '/start - Start working with the bot\n'
                        '/help - List of commands\n'
                        '/info - Bot information\n'
                        '/catalog - Product catalog\n'
                        '/order - Place an order\n'
                        '/feedback - Leave feedback',
                'info': 'This bot is created to demonstrate an online store in Telegram. Here you can browse the product catalog and place orders.',
                'catalog_empty': 'Catalog is empty.',
                'item_not_found': 'Item not found.',
                'order_created': 'Your order has been successfully placed! Thank you for your purchase.',
                'feedback_prompt': 'Please write your feedback in the next message:',
                'feedback_received': 'Thank you for your feedback!',
                'admin_menu': 'Admin menu:',
                'not_admin': 'You do not have admin rights.',
                'add_item_prompt': 'Enter item data in the format:\nName|Description|Price',
                'item_added': 'Item successfully added.',
                'remove_item_prompt': 'Select an item to remove:',
                'item_removed': 'Item successfully removed.',
                'invalid_format': 'Invalid input format.',
                'orders_empty': 'Order list is empty.',
                'hello': 'Hello! How can I help you today?',
                'available_items': 'Use the /catalog command to see available items.',
                'how_to_order': 'To place an order, select an item in the catalog and click the "Order" button.'
            }
        }

    def get_message(self, key, lang='ua'):
        if lang not in self.messages:
            lang = 'ua'
        return self.messages[lang].get(key, f"Message '{key}' not found")
