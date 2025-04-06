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
        self.admin_states = {}  # To track what admin is doing

    def register_handlers(self):
        # Admin command
        self.bot.message_handler(commands=['admin'])(self.admin_command)

        # Admin callback handlers
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('admin_'))(self.admin_callback_router)

        # Admin item management callbacks
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('remove_item_'))(
            self.handle_remove_item)
            
        # Admin feedback management callbacks
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('feedback_'))(
            self.handle_feedback_callback)

    def admin_command(self, message):
        """Handle /admin command - display admin menu if user has admin rights"""
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.keyboards.set_language(lang)

        if not self._check_admin_rights(user_id):
            return

        admin_menu_text = self.messages.get_message('admin_menu', lang)
        self.bot.send_message(
            user_id,
            admin_menu_text,
            reply_markup=self._get_admin_keyboard(lang)
        )

    def admin_callback_router(self, call):
        """Route admin callbacks to appropriate handlers"""
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.keyboards.set_language(lang)

        if not self._check_admin_rights(user_id, call_id=call.id):
            return

        action = call.data.split('_')[1]
        
        # Route to appropriate handler
        if action == 'add':
            self._handle_add_item(call, lang)
        elif action == 'remove':
            self._handle_remove_item_list(call, lang)
        elif action == 'view':
            self._handle_view_orders(call, lang)
        elif action == 'feedback':
            self._handle_view_feedback(call, lang)
        
        self.bot.answer_callback_query(call.id)

    def _check_admin_rights(self, user_id, call_id=None):
        """Check if user has admin rights"""
        lang = self.user_service.get_user_language(user_id)
        
        if not self.user_service.is_admin(user_id):
            not_admin_msg = self.messages.get_message('not_admin', lang)
            if call_id:
                self.bot.answer_callback_query(call_id, not_admin_msg)
            else:
                self.bot.send_message(user_id, not_admin_msg)
            return False
        return True

    def _get_admin_keyboard(self, lang):
        """Create admin keyboard with localized buttons"""
        self.keyboards.set_language(lang)
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        
        keyboard.add(
            types.InlineKeyboardButton(self.keyboards.get_text('add_item'), callback_data='admin_add'),
            types.InlineKeyboardButton(self.keyboards.get_text('remove_item'), callback_data='admin_remove'),
            types.InlineKeyboardButton(self.keyboards.get_text('view_orders'), callback_data='admin_view'),
            types.InlineKeyboardButton("📊 " + ("Відгуки" if lang == 'ua' else "Feedback"), callback_data='admin_feedback')
        )
        
        return keyboard

    def _handle_add_item(self, call, lang):
        """Handle add item request"""
        user_id = call.from_user.id
        add_prompt = self.messages.get_message('add_item_prompt', lang)
        
        self.bot.send_message(user_id, add_prompt)
        self.bot.register_next_step_handler(call.message, self._process_add_item)
        
    def _process_add_item(self, message):
        """Process add item data received from user"""
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self._check_admin_rights(user_id):
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
                # Return to admin menu
                self.bot.send_message(
                    user_id,
                    self.messages.get_message('admin_menu', lang),
                    reply_markup=self._get_admin_keyboard(lang)
                )
            else:
                self.bot.send_message(user_id, result)  # Error message

        except Exception as e:
            self.bot.send_message(user_id, f"Error: {str(e)}")

    def _handle_remove_item_list(self, call, lang):
        """Handle remove item request - show list of items to remove"""
        user_id = call.from_user.id
        
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
            
        # Add back button
        keyboard.add(types.InlineKeyboardButton(
            self.keyboards.get_text('back'),
            callback_data="admin_back"
        ))

        self.bot.send_message(
            user_id,
            self.messages.get_message('remove_item_prompt', lang),
            reply_markup=keyboard
        )

    def handle_remove_item(self, call):
        """Handle remove item callback"""
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)

        if not self._check_admin_rights(user_id, call_id=call.id):
            return

        item_id = int(call.data.split('_')[2])
        success = self.catalog_service.remove_item(item_id)

        if success:
            self.bot.send_message(user_id, self.messages.get_message('item_removed', lang))
            
            # Return to admin menu
            self.bot.send_message(
                user_id,
                self.messages.get_message('admin_menu', lang),
                reply_markup=self._get_admin_keyboard(lang)
            )
        else:
            self.bot.send_message(user_id, self.messages.get_message('item_not_found', lang))

        self.bot.answer_callback_query(call.id)

    def _handle_view_orders(self, call, lang):
        """Handle view orders request"""
        user_id = call.from_user.id
        
        orders = self.order_service.get_all_orders()
        
        if not orders:
            self.bot.send_message(user_id, self.messages.get_message('orders_empty', lang))
            return
            
        message_text = self.order_service.format_orders_for_admin(orders, lang)
        
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(
            self.keyboards.get_text('back'),
            callback_data="admin_back"
        ))
        
        self.bot.send_message(user_id, message_text, reply_markup=keyboard)

    def _handle_view_feedback(self, call, lang):
        """Handle view feedback request"""
        user_id = call.from_user.id
        
        # Placeholder for feedback service
        # In a real implementation, you'd have a feedback_service.get_all_feedback() method
        
        # For now, just show a placeholder message
        if lang == 'ua':
            message_text = "📊 Відгуки користувачів\n\nПоки що немає відгуків."
        else:
            message_text = "📊 User Feedback\n\nNo feedback yet."
            
        # Create keyboard with back button
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton(
            self.keyboards.get_text('back'),
            callback_data="admin_back"
        ))
        
        self.bot.send_message(user_id, message_text, reply_markup=keyboard)
        
    def handle_feedback_callback(self, call):
        """Handle feedback related callbacks"""
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)
        
        if not self._check_admin_rights(user_id, call_id=call.id):
            return
            
        # Implement feedback actions here
        feedback_action = call.data.split('_')[1]
        
        # Example actions:
        # - Reply to feedback
        # - Delete feedback
        # - Mark as read
        
        self.bot.answer_callback_query(call.id)