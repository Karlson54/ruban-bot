import os

class BotConfig:
    TOKEN = os.environ.get('BOT_TOKEN', "7574595805:AAFjrdshTQuwK4TZrZc_KCfkEs0QmzjmF_Y")
    ADMIN_IDS = [428862346]
    DB_FILE = 'shop_bot.db'
    LANGUAGES = ['ua', 'en']
    DEFAULT_LANGUAGE = 'en'