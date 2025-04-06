import telebot
from telebot import types
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.order_service import OrderService
from service.user_service import UserService
from service.cart_service import CartService
from service.catalog_service import CatalogService


class OrderHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.order_service = OrderService()
        self.user_service = UserService()
        self.cart_service = CartService()
        self.catalog_service = CatalogService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Order command
        self.bot.message_handler(commands=['order', 'orders'])(self.order_command)

        # View order history
        self.bot.callback_query_handler(func=lambda call: call.data == 'view_order_history')(
            self.view_order_history_callback)

        # Checkout callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'checkout')(self.checkout_callback)

        # Confirm order callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'confirm_order')(self.confirm_order_callback)

        # Cancel order callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'cancel_order')(self.cancel_order_callback)

    def order_command(self, message):
        user_id = message.from_user.id
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

        self.bot.send_message(
            user_id,
            message_text,
            reply_markup=keyboard
        )

    def view_order_history_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get user orders
        orders = self.order_service.get_user_orders(user_id)
        orders_text = self.order_service.format_user_orders(orders, lang)

        # Create back button
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(
            self.keyboards.get_text('back'),
            callback_data="back_to_orders"
        ))

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=orders_text,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def checkout_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Get cart items
        cart_items = self.cart_service.get_cart_items(user_id)

        if not cart_items:
            if lang == 'ua':
                notification = "Ваш кошик порожній!"
            else:
                notification = "Your cart is empty!"

            self.bot.answer_callback_query(call.id, notification, show_alert=True)
            return

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Format checkout message
        if lang == 'ua':
            message_text = "📋 Підтвердження замовлення\n\n"
            for item in cart_items:
                message_text += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} грн\n"
            message_text += f"\n💰 Загальна сума: {total} грн"
        else:
            message_text = "📋 Order Confirmation\n\n"
            for item in cart_items:
                message_text += f"• {item['name']} x{item['quantity']} - {item['price'] * item['quantity']} UAH\n"
            message_text += f"\n💰 Total amount: {total} UAH"

        # Create confirmation keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton(
                self.keyboards.get_text('confirm'),
                callback_data="confirm_order"
            ),
            types.InlineKeyboardButton(
                self.keyboards.get_text('cancel'),
                callback_data="cancel_order"
            )
        )

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=message_text,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)

    def confirm_order_callback(self, call):
        user_id = call.from_user.id
        username = call.from_user.username or f"user_{user_id}"
        lang = self.user_service.get_user_language(user_id)

        # Get cart items
        cart_items = self.cart_service.get_cart_items(user_id)

        if not cart_items:
            if lang == 'ua':
                notification = "Ваш кошик порожній!"
            else:
                notification = "Your cart is empty!"

            self.bot.answer_callback_query(call.id, notification, show_alert=True)
            return

        # Create orders for each cart item
        order_ids = []

        for item in cart_items:
            for _ in range(item['quantity']):
                success, order_id = self.order_service.create_order(
                    user_id,
                    username,
                    item['item_id']
                )
                if success:
                    order_ids.append(order_id)

        # Clear cart after order
        self.cart_service.clear_cart(user_id)

        # Send order confirmation
        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=self.messages.get_message('order_created', lang),
            reply_markup=None
        )

        self.bot.answer_callback_query(call.id)

    def cancel_order_callback(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Just go back to cart view
        cart_items = self.cart_service.get_cart_items(user_id)
        cart_text = self.cart_service.format_cart_for_display(cart_items, lang)

        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            types.InlineKeyboardButton(
                "💵 " + ("Оформити замовлення" if lang == 'ua' else "Checkout"),
                callback_data="checkout"
            ),
            types.InlineKeyboardButton(
                "🗑️ " + ("Очистити кошик" if lang == 'ua' else "Clear Cart"),
                callback_data="clear_cart"
            ),
            types.InlineKeyboardButton(
                "📋 " + ("Каталог" if lang == 'ua' else "Catalog"),
                callback_data="back_to_catalog"
            )
        )

        self.bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=cart_text,
            reply_markup=keyboard
        )

        self.bot.answer_callback_query(call.id)