import telebot
from telebot import types
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.user_service import UserService


class SettingsHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.keyboards = Keyboards()
        self.user_service = UserService()

    def register_handlers(self):
        # Settings command
        self.bot.message_handler(commands=['settings'])(self.settings_command)
        
        # Language selection callback
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))(
            self.handle_language_selection)
            
        # Back to settings callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_settings')(
            self.back_to_settings)

    def settings_command(self, message):
        """Handle /settings command - show settings menu"""
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.keyboards.set_language(lang)
        
        settings_text = self._get_settings_text(lang)
        self.bot.send_message(
            user_id,
            settings_text,
            reply_markup=self._get_settings_keyboard(lang),
            parse_mode='Markdown'
        )
        
    def _get_settings_text(self, lang):
        """Get localized settings menu text"""
        if lang == 'ua':
            return "*⚙️ Налаштування*\n\nОберіть мову інтерфейсу:"
        else:
            return "*⚙️ Settings*\n\nSelect interface language:"
    
    def _get_settings_keyboard(self, lang):
        """Get settings keyboard with language options"""
        self.keyboards.set_language(lang)
        return self.keyboards.settings_keyboard()
        
    def handle_language_selection(self, call):
        """Handle language selection callback"""
        user_id = call.from_user.id
        lang_code = call.data.split('_')[2]  # Extract language code from 'set_lang_XX'
        
        # Save user language preference
        self.user_service.set_user_language(user_id, lang_code)
        
        # Update keyboard language
        self.keyboards.set_language(lang_code)
        
        # Prepare confirmation message
        if lang_code == 'ua':
            confirmation_text = "✅ Мову змінено на українську"
        else:
            confirmation_text = "✅ Language changed to English"
            
        # Create keyboard with button to return to main menu
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        back_text = "Назад до меню" if lang_code == 'ua' else "Back to menu"
        keyboard.add(types.InlineKeyboardButton(back_text, callback_data='back_to_main'))
        
        # Edit the message with confirmation
        self.bot.edit_message_text(
            confirmation_text,
            user_id,
            call.message.message_id,
            reply_markup=keyboard
        )
        
        self.bot.answer_callback_query(call.id)
        
    def back_to_settings(self, call):
        """Handle back to settings callback"""
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.keyboards.set_language(lang)
        
        # Edit message with settings menu
        settings_text = self._get_settings_text(lang)
        self.bot.edit_message_text(
            settings_text,
            user_id,
            call.message.message_id,
            reply_markup=self._get_settings_keyboard(lang),
            parse_mode='Markdown'
        )
        
        self.bot.answer_callback_query(call.id)