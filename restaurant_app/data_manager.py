import json
import time
from datetime import datetime

class DataManager:
    def __init__(self):
        self.recipes = self.load_default_recipes()
        self.orders = []
        self.online_users = []
        self.current_user = ""
        self.is_admin = False
        self.notifications = []
    
    def set_user(self, username, password=""):
        """Установка текущего пользователя"""
        self.current_user = username
        self.is_admin = self.check_admin(username, password)
    
    def check_admin(self, username, password):
        """Проверяет, является ли текущий пользователь админом"""
        from config import ADMIN_USERS
        return username == "Admin" and password == ADMIN_USERS["Admin"]
    
    def load_default_recipes(self):
        """Загрузка стандартных рецептов"""
        return {
            1: {"name": "🥩 Стейк с картофелем", "price": 85},
            2: {"name": "🍲 Мясное рагу", "price": 75},
            3: {"name": "🌶️ Банка чили", "price": 65},
            4: {"name": "🍝 Спагетти", "price": 55},
            5: {"name": "🥧 Пастуший пирог", "price": 90},
            6: {"name": "🍜 Куриный суп", "price": 60},
            7: {"name": "🥣 Овощное рагу", "price": 45},
            8: {"name": "🍲 Рагу Гамбо", "price": 70},
            9: {"name": "🍞 Кукурузный хлеб", "price": 35},
            10: {"name": "🎃 Тыквенный пирог", "price": 50},
            11: {"name": "🌭 Чили-дог", "price": 40},
            12: {"name": "🌮 Рыбные тако", "price": 45},
            13: {"name": "🍳 Вареное яйцо", "price": 20},
            14: {"name": "🫐 Черника", "price": 15},
            15: {"name": "🍯 Банка мёда", "price": 30},
            16: {"name": "🥫 Банка бульона", "price": 35}
        }
    
    def load_recipes_from_dict(self, recipes_dict):
        """Загрузка рецептов из словаря (из Firebase)"""
        if recipes_dict:
            # Конвертируем ключи в int если они строки
            converted_recipes = {}
            for key, value in recipes_dict.items():
                try:
                    converted_recipes[int(key)] = value
                except (ValueError, TypeError):
                    converted_recipes[key] = value
            self.recipes = converted_recipes
    
    def get_all_recipes(self):
        """Получение всех рецептов"""
        return self.recipes
    
    def get_recipes_by_category(self):
        """Получение рецептов - только вкладка 'Все блюда'"""
        # ВОТ ИСПРАВЛЕНИЕ - возвращаем словарь, а не список
        return {
            "Все блюда": self.recipes  # Это словарь {id: recipe}
        }
    
    def add_recipe(self, name, price):
        """Добавление нового рецепта в меню"""
        new_id = max(self.recipes.keys()) + 1 if self.recipes else 1
        self.recipes[new_id] = {"name": name, "price": price}
        return new_id
    
    def update_recipe(self, recipe_id, name, price):
        """Обновление существующего рецепта"""
        if recipe_id in self.recipes:
            self.recipes[recipe_id] = {"name": name, "price": price}
            return True
        return False
    
    def remove_recipe(self, recipe_id):
        """Удаление рецепта"""
        if recipe_id in self.recipes:
            del self.recipes[recipe_id]
            return True
        return False
    
    def add_order(self, recipe_id, customer):
        """Добавление нового заказа"""
        if recipe_id not in self.recipes:
            return None
            
        recipe = self.recipes[recipe_id]
        order_id = int(time.time() * 1000)
        
        order = {
            "id": order_id,
            "recipe_id": recipe_id,
            "recipe_name": recipe["name"],
            "customer": customer,
            "status": "Готовится",
            "time": datetime.now().strftime("%H:%M:%S"),
            "price": recipe["price"],
            "timestamp": time.time()
        }
        
        self.orders.append(order)
        return order
    
    def remove_order(self, order_id):
        """Удаление заказа"""
        self.orders = [order for order in self.orders if order["id"] != order_id]
        return True
    
    def get_order_by_id(self, order_id):
        """Получение заказа по ID"""
        for order in self.orders:
            if order["id"] == order_id:
                return order
        return None
    
    def get_all_orders(self):
        """Получение всех заказов (для админа)"""
        return self.orders
    
    def update_online_users(self, users_list):
        """Обновление списка онлайн пользователей"""
        self.online_users = users_list
    
    def sync_orders(self, firebase_orders):
        """Синхронизация заказов с Firebase"""
        self.orders = firebase_orders
    
    def add_notification(self, message):
        """Добавление уведомления"""
        self.notifications.append({
            "message": message,
            "time": datetime.now().strftime("%H:%M:%S")
        })
    
    def get_notifications(self):
        """Получение всех уведомлений"""
        return self.notifications
    
    def clear_notifications(self):
        """Очистка уведомлений"""
        self.notifications.clear()