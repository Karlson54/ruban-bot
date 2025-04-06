import telebot
from config.bot_config import BotConfig
from config.init_db import init_database
from handler.admin_handler import AdminHandler
from handler.user_handler import UserHandler
from handler.catalog_handler import CatalogHandler
from handler.order_handler import OrderHandler
from handler.cart_handler import CartHandler


def main():
    # Initialize database
    init_database()

    # Create bot instance
    bot = telebot.TeleBot(BotConfig.TOKEN)

    # Initialize handlers
    admin_handler = AdminHandler(bot)
    user_handler = UserHandler(bot)
    catalog_handler = CatalogHandler(bot)
    order_handler = OrderHandler(bot)
    cart_handler = CartHandler(bot)

    # Register all handlers
    admin_handler.register_handlers()
    user_handler.register_handlers()
    catalog_handler.register_handlers()
    order_handler.register_handlers()
    cart_handler.register_handlers()

    # Start the bot
    print("Bot started...")
    bot.infinity_polling()


if __name__ == "__main__":
    main()