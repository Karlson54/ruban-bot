from repository.order_repository import OrderRepository
from repository.catalog_repository import CatalogRepository
from config.bot_config import BotConfig


class OrderService:
    def __init__(self):
        self.order_repo = OrderRepository()
        self.catalog_repo = CatalogRepository()

    def create_order(self, user_id, user_name, item_id):
        item = self.catalog_repo.get_item_by_id(item_id)
        if not item:
            return False, "Товар не знайдено"

        item_id, item_name, _, price = item
        order_id = self.order_repo.create_order(user_id, user_name, item_id, item_name, price)

        # Відправляємо повідомлення адміністраторам (в реальному боті)
        # Тут можна додати логіку повідомлень

        return True, order_id

    def get_all_orders(self):
        return self.order_repo.get_all_orders()

    def get_user_orders(self, user_id):
        return self.order_repo.get_user_orders(user_id)

    def format_orders_for_admin(self, orders, lang='ua'):
        if not orders:
            return "Список замовлень порожній."

        formatted_orders = []
        for order in orders:
            order_id, user_id, user_name, item_name, price, status, created_at = order
            formatted_orders.append(
                f"🔖 Замовлення #{order_id}\n"
                f"👤 Користувач: {user_name} (ID: {user_id})\n"
                f"📦 Товар: {item_name}\n"
                f"💰 Ціна: {price} грн\n"
                f"📅 Дата: {created_at}\n"
                f"📊 Статус: {status}\n"
            )

        return "\n".join(formatted_orders)

    def format_user_orders(self, orders, lang='ua'):
        if not orders:
            return "У вас ще немає замовлень."

        formatted_orders = []
        for order in orders:
            order_id, item_name, price, status, created_at = order
            formatted_orders.append(
                f"🔖 Замовлення #{order_id}\n"
                f"📦 Товар: {item_name}\n"
                f"💰 Ціна: {price} грн\n"
                f"📅 Дата: {created_at}\n"
                f"📊 Статус: {status}\n"
            )

        return "\n".join(formatted_orders)

    def notify_admins_about_order(self, bot, order_id, user_id, user_name, item_name, price):
        message = (
            f"🔔 НОВЕ ЗАМОВЛЕННЯ #{order_id}\n\n"
            f"👤 Користувач: {user_name} (ID: {user_id})\n"
            f"📦 Товар: {item_name}\n"
            f"💰 Ціна: {price} грн\n"
        )

        for admin_id in BotConfig.ADMIN_IDS:
            try:
                bot.send_message(admin_id, message)
            except Exception as e:
                print(f"Не вдалося надіслати повідомлення адміністратору {admin_id}: {e}")