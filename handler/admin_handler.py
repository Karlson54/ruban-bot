import telebot
from telebot import types
from config.bot_config import BotConfig
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.catalog_service import CatalogService
from service.order_service import OrderService
from service.user_service import UserService


class AdminHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.catalog_service = CatalogService()
        self.order_service = OrderService()
        self.user_service = UserService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Admin command
        self.bot.message_handler(commands=['admin'])(self.admin_command)

        # Admin callback handlers
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))(self.admin_callback)

        # Admin item management callbacks
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('add_item'))(self.process_add_item)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('remove_item_'))(
            self.remove_item_callback)

    def admin_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self.user_service.is_admin(user_id):
            self.bot.send_message(user_id, self.messages.get_message('not_admin', lang))
            return

        self.bot.send_message(
            user_id,
            self.messages.get_message('admin_menu', lang),
            reply_markup=self.keyboards.admin_keyboard()
        )

    def admin_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self.user_service.is_admin(user_id):
            self.bot.answer_callback_query(call.id, self.messages.get_message('not_admin', lang))
            return

        if call.data == 'admin_add_item':
            self.bot.send_message(user_id, self.messages.get_message('add_item_prompt', lang))
            self.bot.register_next_step_handler(call.message, self.process_add_item)

        elif call.data == 'admin_remove_item':
            items = self.catalog_service.get_all_items()
            if not items:
                self.bot.send_message(user_id, self.messages.get_message('catalog_empty', lang))
                return

            keyboard = types.InlineKeyboardMarkup(row_width=1)
            for item in items:
                item_id, name, _, price = item
                keyboard.add(types.InlineKeyboardButton(
                    f"{name} - {price}",
                    callback_data=f"remove_item_{item_id}"
                ))

            self.bot.send_message(
                user_id,
                self.messages.get_message('remove_item_prompt', lang),
                reply_markup=keyboard
            )

        elif call.data == 'admin_view_orders':
            orders = self.order_service.get_all_orders()
            message_text = self.order_service.format_orders_for_admin(orders, lang)
            self.bot.send_message(user_id, message_text)

        self.bot.answer_callback_query(call.id)

    def process_add_item(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self.user_service.is_admin(user_id):
            self.bot.send_message(user_id, self.messages.get_message('not_admin', lang))
            return

        try:
            parts = message.text.split('|')
            if len(parts) != 3:
                self.bot.send_message(user_id, self.messages.get_message('invalid_format', lang))
                return

            name, description, price_str = [p.strip() for p in parts]
            success, result = self.catalog_service.add_item(name, description, price_str)

            if success:
                self.bot.send_message(user_id, self.messages.get_message('item_added', lang))
            else:
                self.bot.send_message(user_id, result)  # Error message

        except Exception as e:
            self.bot.send_message(user_id, f"Error: {str(e)}")

    def remove_item_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self.user_service.is_admin(user_id):
            self.bot.answer_callback_query(call.id, self.messages.get_message('not_admin', lang))
            return

        item_id = int(call.data.split('_')[2])
        success = self.catalog_service.remove_item(item_id)

        if success:
            self.bot.send_message(user_id, self.messages.get_message('item_removed', lang))
        else:
            self.bot.send_message(user_id, self.messages.get_message('item_not_found', lang))

        self.bot.answer_callback_query(call.id)