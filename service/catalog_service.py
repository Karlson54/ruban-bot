from repository.catalog_repository import CatalogRepository


class CatalogService:
    def __init__(self):
        self.catalog_repo = CatalogRepository()

    def get_all_items(self):
        return self.catalog_repo.get_all_items()

    def get_item_by_id(self, item_id):
        return self.catalog_repo.get_item_by_id(item_id)

    def add_item(self, name, description, price_str):
        try:
            price = float(price_str)
            if price <= 0:
                return False, "Ціна повинна бути позитивним числом"

            item_id = self.catalog_repo.add_item(name, description, price)
            return True, item_id
        except ValueError:
            return False, "Неправильний формат ціни"

    def remove_item(self, item_id):
        return self.catalog_repo.remove_item(item_id)

    def format_catalog_for_display(self, items, lang='ua'):
        if not items:
            return "На жаль, каталог порожній."

        formatted_items = []
        for item in items:
            item_id, name, description, price = item
            formatted_items.append(f"🔹 {name} - {price} грн")

        return "\n".join(formatted_items)

    def format_item_details(self, item, lang='ua'):
        if not item:
            return "Товар не знайдено."

        item_id, name, description, price = item
        return f"📌 {name}\n\n📝 {description}\n\n💰 Ціна: {price} грн"
