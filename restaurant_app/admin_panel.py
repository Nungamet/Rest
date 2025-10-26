import customtkinter as ctk
from config import COLORS
from notifications import notifier

class AdminPanel:
    def __init__(self, parent, data_manager, firebase_manager):
        self.data_manager = data_manager
        self.firebase_manager = firebase_manager
        self.parent = parent
        
        # Создаем новое окно
        self.window = ctk.CTkToplevel(parent)
        self.window.title("Панель управления - Админ")
        self.window.geometry("1000x700")
        self.window.resizable(True, True)
        
        # Делаем окно модальным
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_admin_interface()
    
    def create_admin_interface(self):
        """Создание интерфейса админа"""
        main_frame = ctk.CTkFrame(self.window, fg_color=COLORS["dark_bg"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        title = ctk.CTkLabel(
            main_frame,
            text="⚙️ ПАНЕЛЬ УПРАВЛЕНИЯ АДМИНА",
            font=("Arial", 20, "bold"),
            text_color=COLORS["primary"]
        )
        title.pack(pady=15)
        
        # Создаем вкладки
        tabview = ctk.CTkTabview(main_frame, fg_color=COLORS["card_bg"])
        tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка управления заказами
        tabview.add("Управление заказами")
        self.create_orders_tab(tabview.tab("Управление заказами"))
        
        # Вкладка управления меню
        tabview.add("Управление меню")
        self.create_menu_tab(tabview.tab("Управление меню"))
    
    def create_orders_tab(self, parent):
        """Создание вкладки управления заказами"""
        # Фрейм для списка заказов
        self.orders_frame = ctk.CTkScrollableFrame(parent, fg_color=COLORS["dark_bg"])
        self.orders_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Обновляем отображение заказов
        self.update_orders_display()
    
    def update_orders_display(self):
        """Обновление отображения заказов в панели админа"""
        # Очищаем предыдущие заказы
        for widget in self.orders_frame.winfo_children():
            widget.destroy()
        
        if not self.data_manager.orders:
            no_orders_label = ctk.CTkLabel(
                self.orders_frame,
                text="Нет активных заказов",
                font=("Arial", 16),
                text_color=COLORS["text_secondary"]
            )
            no_orders_label.pack(pady=20)
            return
        
        # Показываем ВСЕ заказы всех игроков
        active_orders = [order for order in self.data_manager.orders 
                        if order['status'] == "Готовится"]
        
        if not active_orders:
            no_orders_label = ctk.CTkLabel(
                self.orders_frame,
                text="Нет активных заказов",
                font=("Arial", 16),
                text_color=COLORS["text_secondary"]
            )
            no_orders_label.pack(pady=20)
            return
        
        for order in active_orders:
            order_frame = ctk.CTkFrame(self.orders_frame, fg_color=COLORS["card_bg"], height=100)
            order_frame.pack(fill="x", padx=5, pady=5)
            order_frame.pack_propagate(False)
            
            # Информация о заказе
            info_text = f"#{order['id']} {order['recipe_name']}\n"
            info_text += f"👤 {order['customer']} | ⏰ {order['time']} | 💰 ${order['price']}"
            
            info_label = ctk.CTkLabel(
                order_frame,
                text=info_text,
                font=("Arial", 12),
                text_color=COLORS["text_primary"]
            )
            info_label.place(relx=0.05, rely=0.3, anchor="w")
            
            # Статус заказа
            status_label = ctk.CTkLabel(
                order_frame,
                text=f"📍 {order['status']}",
                font=("Arial", 12, "bold"),
                text_color=COLORS["warning"]
            )
            status_label.place(relx=0.05, rely=0.7, anchor="w")
            
            # Кнопки управления
            btn_frame = ctk.CTkFrame(order_frame, fg_color="transparent")
            btn_frame.place(relx=0.95, rely=0.5, anchor="e")
            
            complete_btn = ctk.CTkButton(
                btn_frame,
                text="✅ Готово",
                command=lambda o=order: self.complete_order(o),
                fg_color=COLORS["success"],
                hover_color="#388e3c",
                width=80,
                height=30
            )
            complete_btn.pack(side="left", padx=5)
            
            cancel_btn = ctk.CTkButton(
                btn_frame,
                text="❌ Отмена",
                command=lambda o=order: self.cancel_order(o),
                fg_color=COLORS["error"],
                hover_color="#c62828",
                width=80,
                height=30
            )
            cancel_btn.pack(side="left", padx=5)
    
    def complete_order(self, order):
        """Завершение заказа с уведомлением игрока"""
        # Push-уведомление Windows для игрока
        notifier.show_notification(
            "🍽️ Заказ готов!", 
            f"Ваш заказ '{order['recipe_name']}' готов к выдаче!",
            duration=10
        )
        
        # Удаляем заказ
        self.data_manager.remove_order(order['id'])
        
        # Отправляем обновление в Firebase
        if self.firebase_manager:
            self.firebase_manager.remove_order(order['id'])
        
        # Обновляем отображение
        self.update_orders_display()
    
    def cancel_order(self, order):
        """Отмена заказа с уведомлением игрока"""
        # Push-уведомление Windows для игрока
        notifier.show_notification(
            "❌ Заказ отменен", 
            f"Заказ '{order['recipe_name']}' был отменен администратором",
            duration=10
        )
        
        # Удаляем заказ
        self.data_manager.remove_order(order['id'])
        
        # Отправляем обновление в Firebase
        if self.firebase_manager:
            self.firebase_manager.remove_order(order['id'])
        
        # Обновляем отображение
        self.update_orders_display()
    
    def create_menu_tab(self, parent):
        """Создание вкладки управления меню"""
        main_frame = ctk.CTkFrame(parent, fg_color=COLORS["dark_bg"])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладки для управления меню
        menu_tabview = ctk.CTkTabview(main_frame, fg_color=COLORS["card_bg"])
        menu_tabview.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка добавления блюда
        menu_tabview.add("Добавить блюдо")
        self.create_add_dish_tab(menu_tabview.tab("Добавить блюдо"))
        
        # Вкладка редактирования блюд
        menu_tabview.add("Редактировать блюда")
        self.create_edit_dishes_tab(menu_tabview.tab("Редактировать блюда"))
    
    def create_add_dish_tab(self, parent):
        """Создание вкладки добавления блюда"""
        add_frame = ctk.CTkFrame(parent, fg_color=COLORS["dark_bg"])
        add_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        title = ctk.CTkLabel(
            add_frame,
            text="ДОБАВИТЬ НОВОЕ БЛЮДО В МЕНЮ",
            font=("Arial", 18, "bold"),
            text_color=COLORS["secondary"]
        )
        title.pack(pady=20)
        
        # Форма добавления блюда
        form_frame = ctk.CTkFrame(add_frame, fg_color=COLORS["card_bg"])
        form_frame.pack(fill="x", padx=50, pady=20)
        
        # Название блюда
        ctk.CTkLabel(
            form_frame,
            text="🍽️ Название блюда:",
            font=("Arial", 14, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        self.dish_name_var = ctk.StringVar()
        dish_name_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.dish_name_var,
            font=("Arial", 14),
            width=300,
            height=40,
            placeholder_text="Введите название блюда"
        )
        dish_name_entry.pack(pady=10)
        
        # Цена блюда
        ctk.CTkLabel(
            form_frame,
            text="💰 Цена:",
            font=("Arial", 14, "bold"),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        self.dish_price_var = ctk.StringVar()
        dish_price_entry = ctk.CTkEntry(
            form_frame,
            textvariable=self.dish_price_var,
            font=("Arial", 14),
            width=200,
            height=40,
            placeholder_text="Введите цену"
        )
        dish_price_entry.pack(pady=10)
        
        # Кнопка добавления
        add_btn = ctk.CTkButton(
            form_frame,
            text="➕ ДОБАВИТЬ В МЕНЮ",
            command=self.add_to_menu,
            fg_color=COLORS["success"],
            hover_color="#388e3c",
            width=200,
            height=40,
            font=("Arial", 14, "bold")
        )
        add_btn.pack(pady=20)
        
        # Список добавленных блюд
        self.dishes_list = ctk.CTkTextbox(
            form_frame,
            height=150,
            fg_color=COLORS["dark_bg"],
            text_color=COLORS["text_primary"],
            font=("Arial", 12)
        )
        self.dishes_list.pack(fill="x", padx=10, pady=10)
        self.update_dishes_list()
    
    def create_edit_dishes_tab(self, parent):
        """Создание вкладки редактирования блюд"""
        edit_frame = ctk.CTkFrame(parent, fg_color=COLORS["dark_bg"])
        edit_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Заголовок
        title = ctk.CTkLabel(
            edit_frame,
            text="РЕДАКТИРОВАТЬ СУЩЕСТВУЮЩИЕ БЛЮДА",
            font=("Arial", 18, "bold"),
            text_color=COLORS["warning"]
        )
        title.pack(pady=20)
        
        # Фрейм для списка блюд
        self.edit_dishes_frame = ctk.CTkScrollableFrame(edit_frame, fg_color=COLORS["dark_bg"])
        self.edit_dishes_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.update_edit_dishes_list()
    
    def update_edit_dishes_list(self):
        """Обновление списка блюд для редактирования"""
        for widget in self.edit_dishes_frame.winfo_children():
            widget.destroy()
        
        if not self.data_manager.recipes:
            no_dishes_label = ctk.CTkLabel(
                self.edit_dishes_frame,
                text="Меню пустое",
                font=("Arial", 16),
                text_color=COLORS["text_secondary"]
            )
            no_dishes_label.pack(pady=20)
            return
        
        for recipe_id, recipe in self.data_manager.recipes.items():
            dish_frame = ctk.CTkFrame(self.edit_dishes_frame, fg_color=COLORS["card_bg"], height=80)
            dish_frame.pack(fill="x", padx=5, pady=5)
            dish_frame.pack_propagate(False)
            
            # Информация о блюде
            info_text = f"#{recipe_id} {recipe['name']} - 💰 ${recipe['price']}"
            
            info_label = ctk.CTkLabel(
                dish_frame,
                text=info_text,
                font=("Arial", 12),
                text_color=COLORS["text_primary"]
            )
            info_label.place(relx=0.05, rely=0.5, anchor="w")
            
            # Кнопки управления
            btn_frame = ctk.CTkFrame(dish_frame, fg_color="transparent")
            btn_frame.place(relx=0.95, rely=0.5, anchor="e")
            
            edit_btn = ctk.CTkButton(
                btn_frame,
                text="✏️ Изменить",
                command=lambda rid=recipe_id, r=recipe: self.edit_dish(rid, r),
                fg_color=COLORS["warning"],
                hover_color="#f57c00",
                width=80,
                height=30
            )
            edit_btn.pack(side="left", padx=5)
            
            remove_btn = ctk.CTkButton(
                btn_frame,
                text="🗑️ Удалить",
                command=lambda rid=recipe_id: self.remove_dish(rid),
                fg_color=COLORS["error"],
                hover_color="#c62828",
                width=80,
                height=30
            )
            remove_btn.pack(side="left", padx=5)
    
    def edit_dish(self, recipe_id, recipe):
        """Редактирование блюда"""
        # Создаем окно редактирования
        edit_window = ctk.CTkToplevel(self.window)
        edit_window.title(f"Редактирование блюда #{recipe_id}")
        edit_window.geometry("400x300")
        edit_window.transient(self.window)
        edit_window.grab_set()
        
        # Форма редактирования
        form_frame = ctk.CTkFrame(edit_window, fg_color=COLORS["card_bg"])
        form_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            form_frame,
            text=f"Редактирование #{recipe_id}",
            font=("Arial", 16, "bold"),
            text_color=COLORS["primary"]
        ).pack(pady=10)
        
        # Название блюда
        ctk.CTkLabel(
            form_frame,
            text="Название блюда:",
            font=("Arial", 12),
            text_color=COLORS["text_primary"]
        ).pack(pady=5)
        
        edit_name_var = ctk.StringVar(value=recipe['name'])
        edit_name_entry = ctk.CTkEntry(
            form_frame,
            textvariable=edit_name_var,
            font=("Arial", 12),
            width=300,
            height=35
        )
        edit_name_entry.pack(pady=5)
        
        # Цена блюда
        ctk.CTkLabel(
            form_frame,
            text="Цена:",
            font=("Arial", 12),
            text_color=COLORS["text_primary"]
        ).pack(pady=5)
        
        edit_price_var = ctk.StringVar(value=str(recipe['price']))
        edit_price_entry = ctk.CTkEntry(
            form_frame,
            textvariable=edit_price_var,
            font=("Arial", 12),
            width=200,
            height=35
        )
        edit_price_entry.pack(pady=5)
        
        def save_changes():
            new_name = edit_name_var.get().strip()
            new_price = edit_price_var.get().strip()
            
            if not new_name or not new_price:
                notifier.show_notification("Ошибка", "Заполните все поля")
                return
            
            try:
                price = int(new_price)
                if price <= 0:
                    notifier.show_notification("Ошибка", "Цена должна быть положительной")
                    return
            except ValueError:
                notifier.show_notification("Ошибка", "Введите корректную цену")
                return
            
            # Обновляем блюдо
            self.data_manager.update_recipe(recipe_id, new_name, price)
            
            # Сохраняем в Firebase
            self.firebase_manager.firebase.save_menu_from_data_manager(self.data_manager)
            
            notifier.show_notification("Успех", f"Блюдо обновлено: {new_name}")
            edit_window.destroy()
            self.update_edit_dishes_list()
            self.update_dishes_list()
        
        # Кнопка сохранения
        save_btn = ctk.CTkButton(
            form_frame,
            text="💾 СОХРАНИТЬ",
            command=save_changes,
            fg_color=COLORS["success"],
            hover_color="#388e3c",
            width=150,
            height=40
        )
        save_btn.pack(pady=20)
    
    def remove_dish(self, recipe_id):
        """Удаление блюда"""
        recipe = self.data_manager.recipes[recipe_id]
        
        # Подтверждение удаления
        confirm_window = ctk.CTkToplevel(self.window)
        confirm_window.title("Подтверждение удаления")
        confirm_window.geometry("400x200")
        confirm_window.transient(self.window)
        confirm_window.grab_set()
        
        confirm_frame = ctk.CTkFrame(confirm_window, fg_color=COLORS["card_bg"])
        confirm_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            confirm_frame,
            text=f"Удалить блюдо?",
            font=("Arial", 16, "bold"),
            text_color=COLORS["error"]
        ).pack(pady=10)
        
        ctk.CTkLabel(
            confirm_frame,
            text=f"#{recipe_id} {recipe['name']} - ${recipe['price']}",
            font=("Arial", 14),
            text_color=COLORS["text_primary"]
        ).pack(pady=10)
        
        def confirm_remove():
            self.data_manager.remove_recipe(recipe_id)
            self.firebase_manager.firebase.save_menu_from_data_manager(self.data_manager)
            notifier.show_notification("Успех", f"Блюдо удалено: {recipe['name']}")
            confirm_window.destroy()
            self.update_edit_dishes_list()
            self.update_dishes_list()
        
        btn_frame = ctk.CTkFrame(confirm_frame, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text="✅ ДА, УДАЛИТЬ",
            command=confirm_remove,
            fg_color=COLORS["error"],
            hover_color="#c62828",
            width=120,
            height=35
        )
        confirm_btn.pack(side="left", padx=10)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ ОТМЕНА",
            command=confirm_window.destroy,
            fg_color=COLORS["secondary"],
            hover_color="#29b6f6",
            width=120,
            height=35
        )
        cancel_btn.pack(side="left", padx=10)
    
    def update_dishes_list(self):
        """Обновление списка добавленных блюд"""
        self.dishes_list.configure(state="normal")
        self.dishes_list.delete("1.0", "end")
        
        if self.data_manager.recipes:
            self.dishes_list.insert("1.0", "📋 ТЕКУЩЕЕ МЕНЮ:\n\n")
            for recipe_id, recipe in self.data_manager.recipes.items():
                self.dishes_list.insert("end", f"• #{recipe_id} {recipe['name']} - ${recipe['price']}\n")
        else:
            self.dishes_list.insert("1.0", "Меню пустое")
        
        self.dishes_list.configure(state="disabled")
    
    def add_to_menu(self):
        """Добавление нового блюда в меню"""
        dish_name = self.dish_name_var.get().strip()
        dish_price = self.dish_price_var.get().strip()
        
        if not dish_name or not dish_price:
            notifier.show_notification("Ошибка", "Заполните все поля")
            return
        
        try:
            price = int(dish_price)
            if price <= 0:
                notifier.show_notification("Ошибка", "Цена должна быть положительной")
                return
        except ValueError:
            notifier.show_notification("Ошибка", "Введите корректную цену")
            return
        
        # Добавляем блюдо в меню
        new_id = self.data_manager.add_recipe(dish_name, price)
        
        # Сохраняем в Firebase
        self.firebase_manager.firebase.save_menu_from_data_manager(self.data_manager)
        
        notifier.show_notification("Успех", f"Блюдо '{dish_name}' добавлено в меню за ${price} (ID: {new_id})")
        
        # Очищаем поля и обновляем списки
        self.dish_name_var.set("")
        self.dish_price_var.set("")
        self.update_dishes_list()
        self.update_edit_dishes_list()