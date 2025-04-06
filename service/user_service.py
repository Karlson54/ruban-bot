from repository.user_repository import UserRepository
from config.bot_config import BotConfig


class UserService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, user_id, username, first_name, last_name, language=None):
        if not language:
            language = BotConfig.DEFAULT_LANGUAGE

        self.user_repo.create_or_update_user(user_id, username, first_name, last_name, language)

    def is_admin(self, user_id):
        return user_id in BotConfig.ADMIN_IDS

    def set_language(self, user_id, language):
        if language in BotConfig.LANGUAGES:
            self.user_repo.set_language(user_id, language)
            return True
        return False

    def get_user_language(self, user_id):
        language = self.user_repo.get_user_language(user_id)
        if language not in BotConfig.LANGUAGES:
            language = BotConfig.DEFAULT_LANGUAGE
        return language

    def set_waiting_feedback(self, user_id, is_waiting=True):
        self.user_repo.set_waiting_feedback(user_id, is_waiting)

    def is_waiting_feedback(self, user_id):
        return self.user_repo.is_waiting_feedback(user_id)

    def process_feedback(self, user_id, feedback_text, bot):
        # Скидаємо флаг очікування зворотного зв'язку
        self.set_waiting_feedback(user_id, False)

        # Повідомляємо адміністраторів про новий відгук
        user = self.user_repo.get_user(user_id)
        user_info = f"{user[2]} {user[3]}" if user else f"Користувач ID: {user_id}"

        feedback_message = f"📮 НОВИЙ ВІДГУК\n\n👤 Від: {user_info}\n\n💬 Текст: {feedback_text}"

        for admin_id in BotConfig.ADMIN_IDS:
            try:
                bot.send_message(admin_id, feedback_message)
            except Exception as e:
                print(f"Не вдалося надіслати відгук адміністратору {admin_id}: {e}")

        return True
