import telebot
from telebot import types
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.catalog_service import CatalogService
from service.user_service import UserService
from service.cart_service import CartService


class CatalogHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.catalog_service = CatalogService()
        self.user_service = UserService()
        self.cart_service = CartService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Catalog command
        self.bot.message_handler(commands=['catalog'])(self.catalog_command)

        # Item view callback
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('view_item_'))(self.view_item_callback)

        # Back to catalog callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_catalog')(self.back_to_catalog_callback)

        # Add to cart callback
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))(
            self.add_to_cart_callback)

    def catalog_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get all catalog items
        items = self.catalog_service.get_all_items()

        if not items:
            self.bot.send_message(
                user_id,
                self.messages.get_message('catalog_empty', lang),
                reply_markup=self.keyboards.main_keyboard(user_id)
            )
            return

        # Create catalog keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for item in items:
            item_id, name, _, price = item
            keyboard.add(types.InlineKeyboardButton(
                f"{name} - {price} грн",
                callback_data=f"view_item_{item_id}"
            ))

        self.bot.send_message(
            user_id,
            self.messages.get_message('available_items', lang),
            reply_markup=keyboard
        )

    def view_item_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        item_id = int(call.data.split('_')[2])
        item = self.catalog_service.get_item_by_id(item_id)

        if not item:
            self.bot.answer_callback_query(call.id, self.messages.get_message('item_not_found', lang))
            return

        # Format item details
        item_details = self.catalog_service.format_item_details(item, lang)

        # Create item view keyboard with Add to Cart button
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(
                self.keyboards.get_text('order'),
                callback_data=f"add_to_cart_{item_id}"
            ),
            types.InlineKeyboardButton(
                self.keyboards.get_text('back'),
                callback_data="back_to_catalog"
            )
        )

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=item_details,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def back_to_catalog_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get all catalog items
        items = self.catalog_service.get_all_items()

        # Create catalog keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        for item in items:
            item_id, name, _, price = item
            keyboard.add(types.InlineKeyboardButton(
                f"{name} - {price} грн",
                callback_data=f"view_item_{item_id}"
            ))

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=self.messages.get_message('available_items', lang),
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def add_to_cart_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        item_id = int(call.data.split('_')[3])
        item = self.catalog_service.get_item_by_id(item_id)

        if not item:
            self.bot.answer_callback_query(call.id, self.messages.get_message('item_not_found', lang))
            return

        # Add item to cart
        success = self.cart_service.add_to_cart(user_id, item_id, 1)  # Default quantity 1

        if success:
            # Get total items in cart for notification
            cart_items_count = self.cart_service.get_cart_items_count(user_id)

            if lang == 'ua':
                notification = f"✅ Товар додано до кошика! У кошику {cart_items_count} товарів."
            else:
                notification = f"✅ Item added to cart! You have {cart_items_count} items in your cart."

            self.bot.answer_callback_query(call.id, notification, show_alert=True)
        else:
            if lang == 'ua':
                notification = "❌ Не вдалося додати товар до кошика."
            else:
                notification = "❌ Failed to add item to cart."

            self.bot.answer_callback_query(call.id, notification, show_alert=True)