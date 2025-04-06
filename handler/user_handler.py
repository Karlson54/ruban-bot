import telebot
from telebot import types
from config.bot_config import BotConfig
from config.messages import Messages
from config.keyboard_config import Keyboards
from service.user_service import UserService


class UserHandler:
    def __init__(self, bot):
        self.bot = bot
        self.messages = Messages()
        self.user_service = UserService()
        self.keyboards = Keyboards()

    def register_handlers(self):
        # Basic command handlers
        self.bot.message_handler(commands=['start'])(self.start_command)
        self.bot.message_handler(commands=['help'])(self.help_command)
        self.bot.message_handler(commands=['info'])(self.info_command)
        self.bot.message_handler(commands=['language', 'lang'])(self.language_command)
        self.bot.message_handler(commands=['feedback'])(self.feedback_command)

        # Feedback handler for next message
        self.bot.message_handler(func=self.is_feedback_message)(self.process_feedback)

        # Language selection callback
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))(self.language_callback)

    def start_command(self, message):
        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name

        # Register or update user
        self.user_service.register_user(user_id, username, first_name, last_name)
        lang = self.user_service.get_user_language(user_id)

        # Send welcome message with main keyboard
        self.bot.send_message(
            user_id,
            self.messages.get_message('start', lang),
            reply_markup=self.keyboards.main_keyboard(user_id)
        )

    def help_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.bot.send_message(
            user_id,
            self.messages.get_message('help', lang),
            reply_markup=self.keyboards.main_keyboard()
        )

    def info_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)
        self.bot.send_message(
            user_id,
            self.messages.get_message('info', lang),
            reply_markup=self.keyboards.main_keyboard()
        )

    def language_command(self, message):
        user_id = message.from_user.id

        # Create language selection keyboard
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            types.InlineKeyboardButton("🇺🇦 Українська", callback_data="lang_ua"),
            types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        )

        self.bot.send_message(
            user_id,
            "Оберіть мову / Choose language:",
            reply_markup=keyboard
        )

    def language_callback(self, call):
        user_id = call.from_user.id
        lang_code = call.data.split('_')[1]

        if self.user_service.set_language(user_id, lang_code):
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
                reply_markup=self.keyboards.main_keyboard()
            )

        self.bot.answer_callback_query(call.id)

    def feedback_command(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Set waiting feedback flag
        self.user_service.set_waiting_feedback(user_id, True)

        self.bot.send_message(
            user_id,
            self.messages.get_message('feedback_prompt', lang)
        )

    def is_feedback_message(self, message):
        return self.user_service.is_waiting_feedback(message.from_user.id)

    def process_feedback(self, message):
        user_id = message.from_user.id
        lang = self.user_service.get_user_language(user_id)

        # Process the feedback
        self.user_service.process_feedback(user_id, message.text, self.bot)

        # Send confirmation to user
        self.bot.send_message(
            user_id,
            self.messages.get_message('feedback_received', lang),
            reply_markup=self.keyboards.main_keyboard()
        )