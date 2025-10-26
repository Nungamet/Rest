import time
import threading
import requests
import json

class RealFirebaseManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.base_url = "https://rest-81907-default-rtdb.firebaseio.com"
        self.is_running = True
        
    def _make_request(self, endpoint, method="GET", data=None):
        """Выполняет HTTP запрос к Firebase"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                response = requests.get(f"{url}.json")
            elif method == "POST":
                response = requests.post(f"{url}.json", json=data)
            elif method == "PUT":
                response = requests.put(f"{url}.json", json=data)
            elif method == "DELETE":
                response = requests.delete(f"{url}.json")
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Ошибка Firebase: {e}")
            return None
    
    def add_user(self, username):
        """Добавление пользователя в онлайн"""
        user_data = {
            "name": username,
            "joined": time.strftime("%H:%M:%S"),
            "last_seen": int(time.time())
        }
        return self._make_request(f"/online_users/{username}", "PUT", user_data)
    
    def remove_user(self, username):
        """Удаление пользователя из онлайн"""
        return self._make_request(f"/online_users/{username}", "DELETE")
    
    def update_user_presence(self, username):
        """Обновление времени последней активности"""
        return self._make_request(f"/online_users/{username}/last_seen", "PUT", int(time.time()))
    
    def get_online_users(self):
        """Получение списка онлайн пользователей"""
        users_data = self._make_request("/online_users")
        online_users = []
        
        if users_data:
            current_time = time.time()
            for username, user_info in users_data.items():
                if user_info and isinstance(user_info, dict):
                    last_seen = user_info.get('last_seen', 0)
                    # Считаем онлайн если был активен в последние 30 секунд
                    if current_time - last_seen < 30:
                        online_users.append(username)
        
        return online_users
    
    def add_order(self, order):
        """Добавление заказа в Firebase"""
        return self._make_request(f"/orders/{order['id']}", "PUT", order)
    
    def remove_order(self, order_id):
        """Удаление заказа из Firebase"""
        return self._make_request(f"/orders/{order_id}", "DELETE")
    
    def get_all_orders(self):
        """Получение всех заказов"""
        orders_data = self._make_request("/orders")
        orders = []
        
        if orders_data:
            for order_id, order_info in orders_data.items():
                if order_info and isinstance(order_info, dict):
                    orders.append(order_info)
        
        return orders
    
    def get_active_orders(self):
        """Получение активных заказов"""
        all_orders = self.get_all_orders()
        return [order for order in all_orders if order.get('status') == 'Готовится']
    
    def save_menu_from_data_manager(self, data_manager):
        """Сохранение меню в Firebase"""
        return self._make_request("/menu", "PUT", data_manager.recipes)
    
    def load_menu_to_data_manager(self, data_manager):
        """Загрузка меню из Firebase в DataManager"""
        try:
            menu_data = self._make_request("/menu")
            if menu_data:
                data_manager.load_recipes_from_dict(menu_data)
                print("✅ Меню загружено из Firebase")
            else:
                print("ℹ️ Меню в Firebase пустое, используются стандартные рецепты")
        except Exception as e:
            print(f"❌ Ошибка загрузки меню: {e}")
    
    def start_listeners(self, order_callback, user_callback):
        """Запуск слушателей изменений"""
        def listener_thread():
            while self.is_running:
                try:
                    # Проверяем обновления заказов
                    orders = self.get_active_orders()
                    if orders:
                        order_callback({"data": orders, "type": "orders_update"})
                    
                    # Проверяем онлайн пользователей
                    online_users = self.get_online_users()
                    if online_users:
                        user_callback({"data": online_users, "type": "users_update"})
                    
                    # Обновляем свое присутствие
                    if self.data_manager.current_user:
                        self.update_user_presence(self.data_manager.current_user)
                    
                    time.sleep(3)  # Проверяем каждые 3 секунды
                    
                except Exception as e:
                    print(f"Ошибка слушателя: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=listener_thread, daemon=True)
        thread.start()
        return thread
    
    def stop(self):
        """Остановка менеджера"""
        self.is_running = False
        # Удаляем пользователя из онлайн при выходе
        if self.data_manager.current_user:
            self.remove_user(self.data_manager.current_user)

class FirebaseManager:
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.firebase = RealFirebaseManager(data_manager)
        self.is_running = True
    
    def start_listeners(self, order_callback, user_callback):
        """Запуск слушателей"""
        # Сначала добавляем текущего пользователя в онлайн
        if self.data_manager.current_user:
            self.firebase.add_user(self.data_manager.current_user)
        
        # Загружаем меню из Firebase
        self.firebase.load_menu_to_data_manager(self.data_manager)
        
        return self.firebase.start_listeners(order_callback, user_callback)
    
    def add_order(self, order):
        """Добавление заказа"""
        if self.firebase and self.is_running:
            return self.firebase.add_order(order)
        return False
    
    def remove_order(self, order_id):
        """Удаление заказа"""
        if self.firebase and self.is_running:
            return self.firebase.remove_order(order_id)
        return False
    
    def get_all_orders(self):
        """Получение всех заказов"""
        if self.firebase:
            return self.firebase.get_all_orders()
        return []
    
    def stop(self):
        """Остановка"""
        self.is_running = False
        if self.firebase:
            self.firebase.stop()