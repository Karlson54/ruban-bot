import telebot
from telebot import types
from config.bot_config import BotConfig
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.user_service import UserService


class SettingsHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.user_service = UserService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Settings command handler
        self.bot.message_handler(commands=['settings'])(self.settings_command)
        
        # Language selection callback
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('set_lang_'))(self.handle_language_selection)
        
        # Back to main menu callback
        self.bot.callback_query_handler(func=lambda call: call.data == 'back_to_main')(self.back_to_main)

    def settings_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)
        
        # Create keyboard with current language settings
        self.keyboards.set_language(lang)
        keyboard = self.keyboards.settings_keyboard()
        
        self.bot.send_message(
            user_id,
            "⚙️ " + self.keyboards.get_text('settings'),
            reply_markup=keyboard
        )

    def handle_language_selection(self, call):
        user_id = call.from_user.id
        lang_code = call.data.split('_')[2]  # Extract language code from "set_lang_XX"
        
        # Update user language in database
        if self.user_service.set_language(user_id, lang_code):  # Use set_language instead of set_user_language
            # Update keyboards language
            self.keyboards.set_language(lang_code)
            
            # Send confirmation in the selected language
            if lang_code == 'ua':
                message_text = "🇺🇦 Мову змінено на українську!"
            else:
                message_text = "🇬🇧 Language changed to English!"
                
            self.bot.send_message(
                user_id,
                message_text,
                reply_markup=self.keyboards.main_keyboard(user_id)
            )
        
        self.bot.answer_callback_query(call.id)

    def back_to_main(self, call):
        user_id = call.from_user.id
        lang = self.user_service.get_user_language(user_id)
        
        # Update keyboards language
        self.keyboards.set_language(lang)
        
        # Send message with main keyboard
        self.bot.send_message(
            user_id,
            "👍",
            reply_markup=self.keyboards.main_keyboard(user_id)
        )
        
        self.bot.answer_callback_query(call.id)