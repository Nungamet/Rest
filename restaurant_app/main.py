import customtkinter as ctk
import threading
import time
from datetime import datetime

from config import COLORS, UPDATE_INTERVAL, ADMIN_USERS
from animations import AnimationManager
from data_manager import DataManager
from firebase_manager import FirebaseManager
from ui_components import UIComponents
from notifications import notifier

class RestaurantApp:
    def __init__(self):
        # Настройка приложения
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        self.root = ctk.CTk()
        self.root.title("Rest")
        
        # Оконный режим с нормальным размером
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Центрируем окно на экране
        self.center_window()
        
        self.root.resizable(True, True)
        self.root.attributes('-topmost', False)
        
        # Инициализация менеджеров
        self.data_manager = DataManager()
        self.animations = AnimationManager(self.root)
        self.firebase_manager = FirebaseManager(self.data_manager)
        
        # Переменные UI
        self.online_list = None
        self.orders_text = None
        self.is_running = True
        
        # Таймер для автообновления
        self.update_timer = None
        
        # Сначала запрашиваем имя пользователя
        self.ask_username()
        
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def ask_username(self):
        """Запрос имени пользователя"""
        self.login_frame = ctk.CTkFrame(self.root, fg_color=COLORS["dark_bg"])
        self.login_frame.pack(fill="both", expand=True)
        
        # Заголовок
        title_label = ctk.CTkLabel(
            self.login_frame,
            text="REST",
            font=("Arial", 28, "bold"),
            text_color=COLORS["primary"]
        )
        title_label.pack(pady=30)
        
        # Поле ввода имени
        ctk.CTkLabel(
            self.login_frame,
            text="Введите ваш ник:",
            font=("Arial", 18),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        self.username_var = ctk.StringVar()
        self.username_entry = ctk.CTkEntry(
            self.login_frame,
            textvariable=self.username_var,
            font=("Arial", 16),
            width=300,
            height=50,
            placeholder_text="Введите ник"
        )
        self.username_entry.pack(pady=10)
        
        # Фрейм для пароля (изначально скрыт)
        self.password_frame = ctk.CTkFrame(self.login_frame, fg_color="transparent")
        
        self.password_label = ctk.CTkLabel(
            self.password_frame,
            text="Пароль для Admin:",
            font=("Arial", 14),
            text_color=COLORS["text_secondary"]
        )
        self.password_label.pack(pady=5)
        
        self.password_var = ctk.StringVar()
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            textvariable=self.password_var,
            font=("Arial", 16),
            width=300,
            height=50,
            placeholder_text="Введите пароль",
            show="*"
        )
        self.password_entry.pack(pady=10)
        
        # Кнопка входа
        login_btn = ctk.CTkButton(
            self.login_frame,
            text="ПОДКЛЮЧИТЬСЯ К СЕРВЕРУ",
            command=self.login,
            fg_color=COLORS["primary"],
            hover_color="#e55a2b",
            width=250,
            height=50,
            font=("Arial", 16, "bold")
        )
        login_btn.pack(pady=20)
        
        # Статус подключения
        self.status_label = ctk.CTkLabel(
            self.login_frame,
            text="🔴 Не подключено",
            font=("Arial", 12),
            text_color=COLORS["error"]
        )
        self.status_label.pack(pady=10)
        
        # Привязка Enter к входу и отслеживание изменения имени
        self.username_entry.bind('<Return>', lambda e: self.login())
        self.username_entry.bind('<KeyRelease>', self.on_username_change)
        self.password_entry.bind('<Return>', lambda e: self.login())
        self.username_entry.focus()
    
    def on_username_change(self, event=None):
        """Обработчик изменения имени пользователя"""
        username = self.username_var.get().strip()
        if username == "Admin":
            # Показываем поле пароля
            self.password_frame.pack(pady=10)
        else:
            # Скрываем поле пароля
            self.password_frame.pack_forget()
    
    def login(self):
        """Вход в приложение"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username:
            notifier.show_notification("Ошибка", "Введите имя пользователя")
            return
        
        # Проверка пароля для Admin
        if username == "Admin":
            if password != ADMIN_USERS["Admin"]:
                notifier.show_notification("Ошибка", "Неверный пароль для Admin")
                return
        
        # Обновляем статус
        self.status_label.configure(text="🟡 Подключение к серверу...", text_color=COLORS["warning"])
        self.root.update()
        
        try:
            self.data_manager.set_user(username, password)
            
            # Инициализируем UI компоненты
            self.ui_components = UIComponents(self.root, self.animations, self.data_manager)
            self.ui_components.set_firebase_manager(self.firebase_manager)
            
            # Подключаемся к Firebase
            self.firebase_manager.start_listeners(
                self.order_listener,
                self.users_listener
            )
            
            # Обновляем статус
            self.status_label.configure(text="🟢 Подключено к серверу!", text_color=COLORS["success"])
            self.root.update()
            
            # Задержка перед переходом
            self.root.after(1000, self.show_main_interface)
            
        except Exception as e:
            self.status_label.configure(text="🔴 Ошибка подключения", text_color=COLORS["error"])
            notifier.show_notification("Ошибка", f"Не удалось подключиться: {e}")
    
    def show_main_interface(self):
        """Переход к главному интерфейсу"""
        try:
            self.login_frame.destroy()
        except:
            pass
            
        self.create_main_interface()
        
    def create_main_interface(self):
        """Создание главного интерфейса"""
        if not self.is_running:
            return
            
        try:
            # Основной фрейм с прокруткой
            self.main_frame = ctk.CTkScrollableFrame(self.root, fg_color=COLORS["dark_bg"])
            self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Создание UI компонентов
            self.ui_components.create_header(self.main_frame)
            
            # Получаем компоненты
            self.online_list, online_frame = self.ui_components.create_online_section(self.main_frame)
            self.menu_tabs, menu_frame = self.ui_components.create_menu_section(self.main_frame, self.add_order)
            self.orders_text, orders_frame = self.ui_components.create_orders_section(self.main_frame)
            
            # Запуск автообновления
            self.start_auto_update()
            
            # Первоначальная загрузка данных
            self.load_initial_data()
            
            notifier.show_notification("Успех", "Подключено!")
            
        except Exception as e:
            notifier.show_notification("Ошибка", f"Ошибка создания интерфейса: {e}")
    
    def load_initial_data(self):
        """Первоначальная загрузка данных"""
        # Загружаем заказы из Firebase
        orders = self.firebase_manager.get_all_orders()
        self.data_manager.sync_orders(orders)
        self.update_orders_display()
        
        # Загружаем онлайн пользователей
        online_users = self.firebase_manager.firebase.get_online_users()
        self.data_manager.update_online_users(online_users)
        self.update_online_users()
        
        # Загружаем меню из Firebase
        self.firebase_manager.firebase.load_menu_to_data_manager(self.data_manager)
    
    def start_auto_update(self):
        """Запуск автоматического обновления"""
        if not self.is_running:
            return
            
        # Планируем следующее обновление
        self.update_timer = self.root.after(UPDATE_INTERVAL, self.start_auto_update)
    
    def add_order(self, recipe_id):
        """Добавление заказа"""
        if not self.is_running:
            return
            
        try:
            order = self.data_manager.add_order(recipe_id, self.data_manager.current_user)
            success = self.firebase_manager.add_order(order)
            
            if success:
                notifier.show_notification("Успех", f"Заказ '{order['recipe_name']}' отправлен на кухню!")
                self.update_orders_display()
            else:
                notifier.show_notification("Ошибка", "Не удалось отправить заказ")
                
        except Exception as e:
            notifier.show_notification("Ошибка", f"Ошибка добавления заказа: {e}")
    
    def order_listener(self, message):
        """Обработчик заказов из Firebase"""
        if message.get("type") == "orders_update" and self.is_running:
            orders_data = message.get("data", [])
            self.data_manager.sync_orders(orders_data)
            self.update_orders_display()
            
            # Уведомление о новых заказах для админа
            if self.data_manager.is_admin and hasattr(self, 'last_order_count'):
                if len(orders_data) > self.last_order_count:
                    notifier.show_notification("Новый заказ", "Поступил новый заказ!")
            
            self.last_order_count = len(orders_data)
    
    def users_listener(self, message):
        """Обработчик пользователей из Firebase"""
        if message.get("type") == "users_update" and self.is_running:
            users_data = message.get("data", [])
            self.data_manager.update_online_users(users_data)
            self.update_online_users()
    
    def update_online_users(self):
        """Обновление списка онлайн"""
        if self.online_list and self.is_running:
            try:
                self.online_list.configure(state="normal")
                self.online_list.delete("1.0", "end")
                
                # Исключаем Admin из списка онлайн
                online_users = [user for user in self.data_manager.online_users if user != "Admin"]
                
                if online_users:
                    online_text = " | ".join(online_users)
                    status_text = f"🟢 ОНЛАЙН ({len(online_users)}): {online_text}"
                else:
                    status_text = "🟡 Нет игроков онлайн"
                
                self.online_list.insert("1.0", status_text)
                self.online_list.configure(state="disabled")
            except Exception as e:
                print(f"Ошибка обновления онлайн: {e}")
    
    def update_orders_display(self):
        """Обновление отображения заказов"""
        if self.orders_text and self.is_running:
            try:
                self.orders_text.configure(state="normal")
                self.orders_text.delete("1.0", "end")
                
                # Показываем только заказы текущего пользователя
                user_orders = [order for order in self.data_manager.orders 
                             if order['customer'] == self.data_manager.current_user]
                
                if not user_orders:
                    self.orders_text.insert("1.0", "📦 Ваши заказы появятся здесь\n\n")
                    self.orders_text.insert("end", "Закажите что-нибудь из меню!")
                else:
                    self.orders_text.insert("1.0", f"📦 ВАШИ ЗАКАЗЫ ({len(user_orders)}):\n\n")
                    for order in user_orders[-10:]:  # Последние 10 заказов
                        status_emoji = "✅" if order['status'] == 'Готово' else "⏳"
                        order_text = f"{status_emoji} {order['recipe_name']}\n"
                        order_text += f"   ⏰ {order['time']} | 💰 ${order['price']}\n"
                        order_text += f"   📍 {order['status']}\n\n"
                        self.orders_text.insert("end", order_text)
                
                self.orders_text.configure(state="disabled")
            except Exception as e:
                print(f"Ошибка обновления заказов: {e}")
    
    def safe_quit(self):
        """Безопасное закрытие приложения"""
        self.is_running = False
        
        # Сохраняем данные перед выходом
        if hasattr(self, 'firebase_manager'):
            # Сохраняем меню в Firebase
            self.firebase_manager.firebase.save_menu_from_data_manager(self.data_manager)
            self.firebase_manager.stop()
        
        # Останавливаем таймер обновления
        if self.update_timer:
            self.root.after_cancel(self.update_timer)
        
        # Закрываем окно
        self.root.quit()
        self.root.destroy()
    
    def run(self):
        """Запуск приложения"""
        # Обработка закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.safe_quit)
        
        try:
            self.root.mainloop()
        except Exception as e:
            notifier.show_notification("Ошибка", f"Ошибка приложения: {e}")
        finally:
            self.is_running = False

if __name__ == "__main__":
    app = RestaurantApp()
    app.run()