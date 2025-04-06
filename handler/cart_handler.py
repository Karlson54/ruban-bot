import telebot
from telebot import types
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.cart_service import CartService
from service.user_service import UserService
from service.catalog_service import CatalogService


class CartHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.cart_service = CartService()
        self.user_service = UserService()
        self.catalog_service = CatalogService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Cart command
        self.bot.message_handler(commands=['cart'])(self.cart_command)

        # View cart callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'view_cart')(self.view_cart_callback)

        # Clear cart callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'clear_cart')(self.clear_cart_callback)

        # Change quantity callbacks
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('increase_qty_'))(
            self.increase_quantity_callback)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('decrease_qty_'))(
            self.decrease_quantity_callback)
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('remove_from_cart_'))(
            self.remove_from_cart_callback)

        # Back to orders menu
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_orders')(self.back_to_orders_callback)

    def cart_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get cart items
        cart_items = self.cart_service.get_cart_items(user_id)
        cart_text = self.cart_service.format_cart_for_display(cart_items, lang)

        # Create cart keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=1)

        if cart_items:
            keyboard.add(
                types.InlineKeyboardButton(
                    "💵 " + ("Оформити замовлення" if lang == 'ua' else "Checkout"),
                    callback_data="checkout"
                ),
                types.InlineKeyboardButton(
                    "🗑️ " + ("Очистити кошик" if lang == 'ua' else "Clear Cart"),
                    callback_data="clear_cart"
                )
            )

        keyboard.add(types.InlineKeyboardButton(
            "📋 " + ("Каталог" if lang == 'ua' else "Catalog"),
            callback_data="back_to_catalog"
        ))

        self.bot.send_message(
            user_id,
            cart_text,
            reply_markup=keyboard
        )

    def view_cart_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get cart items
        cart_items = self.cart_service.get_cart_items(user_id)
        cart_text = self.cart_service.format_cart_for_display(cart_items, lang)

        # Create cart keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=3)

        # Add item quantity controls if there are items
        if cart_items:
            for item in cart_items:
                # Add buttons in a single row
                keyboard.row(
                    types.InlineKeyboardButton("-", callback_data=f"decrease_qty_{item['item_id']}"),
                    types.InlineKeyboardButton(f"{item['quantity']}", callback_data=f"item_qty_{item['item_id']}"),
                    types.InlineKeyboardButton("+", callback_data=f"increase_qty_{item['item_id']}")
                )
                keyboard.add(types.InlineKeyboardButton(
                    "❌ " + item['name'],
                    callback_data=f"remove_from_cart_{item['item_id']}"
                ))

            keyboard.add(
                types.InlineKeyboardButton(
                    "💵 " + ("Оформити замовлення" if lang == 'ua' else "Checkout"),
                    callback_data="checkout"
                ),
                types.InlineKeyboardButton(
                    "🗑️ " + ("Очистити кошик" if lang == 'ua' else "Clear Cart"),
                    callback_data="clear_cart"
                )
            )

        keyboard.add(types.InlineKeyboardButton(
            "📋 " + ("Каталог" if lang == 'ua' else "Catalog"),
            callback_data="back_to_catalog"
        ))

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=cart_text,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def clear_cart_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Clear the cart
        self.cart_service.clear_cart(user_id)

        # Get empty cart text
        cart_text = self.cart_service.format_cart_for_display([], lang)

        # Create cart keyboard with only catalog button
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(
            "📋 " + ("Каталог" if lang == 'ua' else "Catalog"),
            callback_data="back_to_catalog"
        ))

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=cart_text,
            reply_markup=keyboard
        )

        # Show notification
        if lang == 'ua':
            notification = "Кошик очищено!"
        else:
            notification = "Cart cleared!"

        self.bot.answer_callback_query(call.id, notification)

    def increase_quantity_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        item_id = int(call.data.split('_')[2])

        # Increase quantity
        success = self.cart_service.update_item_quantity(user_id, item_id, 1)

        if success:
            # Refresh cart view
            self.refresh_cart_view(call)
        else:
            if lang == 'ua':
                notification = "Не вдалося оновити кількість!"
            else:
                notification = "Failed to update quantity!"

            self.bot.answer_callback_query(call.id, notification, show_alert=True)

    def decrease_quantity_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        item_id = int(call.data.split('_')[2])

        # Get current quantity
        cart_items = self.cart_service.get_cart_items(user_id)
        current_item = next((item for item in cart_items if item['item_id'] == item_id), None)

        if not current_item:
            self.bot.answer_callback_query(call.id)
            return

        if current_item['quantity'] <= 1:
            # If quantity is 1, remove item
            self.cart_service.remove_from_cart(user_id, item_id)
        else:
            # Decrease quantity
            self.cart_service.update_item_quantity(user_id, item_id, -1)

        # Refresh cart view
        self.refresh_cart_view(call)

    def remove_from_cart_callback(self, call):
        user_id = call.from_user.id
        item_id = int(call.data.split('_')[3])

        # Remove item from cart
        self.cart_service.remove_from_cart(user_id, item_id)

        # Refresh cart view
        self.refresh_cart_view(call)

    def back_to_orders_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Create orders menu
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton("🛒 " + (
                "Перейти до кошика" if lang == 'ua' else "Go to Cart"
            ), callback_data="view_cart"),
            types.InlineKeyboardButton("📜 " + (
                "Історія замовлень" if lang == 'ua' else "Order History"
            ), callback_data="view_order_history")
        )

        # Get cart count for message
        cart_count = self.cart_service.get_cart_items_count(user_id)

        if lang == 'ua':
            message_text = f"🛍️ Ваші замовлення\n\nУ вашому кошику: {cart_count} товарів"
        else:
            message_text = f"🛍️ Your Orders\n\nItems in your cart: {cart_count}"

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def refresh_cart_view(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get cart items
        cart_items = self.cart_service.get_cart_items(user_id)
        cart_text = self.cart_service.format_cart_for_display(cart_items, lang)

        # Create cart keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=3)

        # Add item quantity controls if there are items
        if cart_items:
            for item in cart_items:
                # Add buttons in a single row
                keyboard.row(
                    types.InlineKeyboardButton("-", callback_data=f"decrease_qty_{item['item_id']}"),
                    types.InlineKeyboardButton(f"{item['quantity']}", callback_data=f"item_qty_{item['item_id']}"),
                    types.InlineKeyboardButton("+", callback_data=f"increase_qty_{item['item_id']}")
                )
                keyboard.add(types.InlineKeyboardButton(
                    "❌ " + item['name'],
                    callback_data=f"remove_from_cart_{item['item_id']}"
                ))

            keyboard.add(
                types.InlineKeyboardButton(
                    "💵 " + ("Оформити замовлення" if lang == 'ua' else "Checkout"),
                    callback_data="checkout"
                ),
                types.InlineKeyboardButton(
                    "🗑️ " + ("Очистити кошик" if lang == 'ua' else "Clear Cart"),
                    callback_data="clear_cart"
                )
            )

        keyboard.add(types.InlineKeyboardButton(
            "📋 " + ("Каталог" if lang == 'ua' else "Catalog"),
            callback_data="back_to_catalog"
        ))

        try:
            self.bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=cart_text,
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Error refreshing cart view: {e}")

        self.bot.answer_callback_query(call.id)