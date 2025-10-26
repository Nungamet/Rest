import customtkinter as ctk
from config import COLORS

class UIComponents:
    def __init__(self, root, animations, data_manager):
        self.root = root
        self.animations = animations
        self.data_manager = data_manager
        
    def create_header(self, parent):
        """Создание шапки приложения"""
        header_frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"], height=80)
        header_frame.pack(fill="x", padx=10, pady=10)
        header_frame.pack_propagate(False)
        
        # Анимированный заголовок
        title_label = ctk.CTkLabel(
            header_frame,
            text="",
            font=("Arial", 20, "bold"),
            text_color=COLORS["primary"]
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Имя пользователя
        user_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 {self.data_manager.current_user}",
            font=("Arial", 12),
            text_color=COLORS["text_secondary"]
        )
        user_label.place(relx=0.02, rely=0.5, anchor="w")
        
        # Кнопка админа (только для админов)
        if self.data_manager.is_admin:
            admin_btn = ctk.CTkButton(
                header_frame,
                text="⚙️ Управление",
                command=self.show_admin_panel,
                fg_color=COLORS["secondary"],
                hover_color="#29b6f6",
                width=100,
                height=30
            )
            admin_btn.place(relx=0.85, rely=0.5, anchor="e")
        
        # Запускаем анимацию заголовка
        self.animations.typewriter_effect(
            title_label, 
            "🍖 REST"
        )
        
        return header_frame
    
    def show_admin_panel(self):
        """Показ панели админа"""
        from admin_panel import AdminPanel
        AdminPanel(self.root, self.data_manager, self.firebase_manager)
    
    def set_firebase_manager(self, firebase_manager):
        """Установка менеджера Firebase"""
        self.firebase_manager = firebase_manager
    
    def create_online_section(self, parent):
        """Создание раздела онлайн игроков"""
        online_frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"])
        
        # Заголовок
        title = ctk.CTkLabel(
            online_frame,
            text="👥 ОНЛАЙН В РЕСТОРАНЕ",
            font=("Arial", 20, "bold"),
            text_color=COLORS["secondary"]
        )
        title.pack(pady=10)
        
        # Список игроков
        online_list = ctk.CTkTextbox(
            online_frame, 
            height=60, 
            fg_color=COLORS["dark_bg"],
            text_color=COLORS["text_primary"],
            font=("Arial", 12)
        )
        online_list.pack(fill="x", padx=10, pady=5)
        online_list.insert("1.0", "🟢 Загрузка...")
        online_list.configure(state="disabled")
        
        # Анимация появления
        self.animations.simple_appear(online_frame, 200)
        
        return online_list, online_frame
    
    def create_menu_section(self, parent, order_callback):
        """Создание раздела меню - только вкладка 'Все блюда'"""
        menu_frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"])
        
        # Заголовок
        title = ctk.CTkLabel(
            menu_frame,
            text="📋 МЕНЮ - ВСЕ БЛЮДА",
            font=("Arial", 20, "bold"),
            text_color=COLORS["success"]
        )
        title.pack(pady=10)
        
        # Получаем рецепты (только "Все блюда")
        categories = self.data_manager.get_recipes_by_category()
        
        # Создаем одну вкладку "Все блюда"
        tabview = ctk.CTkTabview(menu_frame, fg_color=COLORS["dark_bg"])
        tabview.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Только одна вкладка
        tabview.add("Все блюда")
        tab = tabview.tab("Все блюда")
        
        # Создаем прокручиваемый фрейм
        scroll_frame = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Создаем сетку для блюд - ИСПРАВЛЕНИЕ ЗДЕСЬ
        recipes_dict = categories["Все блюда"]
        self.create_category_grid(scroll_frame, recipes_dict, order_callback)
        
        self.animations.simple_appear(menu_frame, 400)
        
        return tabview, menu_frame
    
    def create_category_grid(self, parent, recipes, order_callback):
        """Создание сетки блюд"""
        row, col = 0, 0
        for recipe_id, recipe in recipes.items():
            item_frame = self.create_menu_item(parent, recipe, recipe_id, order_callback)
            item_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            col += 1
            if col >= 3:  # 3 блюда в ряду
                col = 0
                row += 1
        
        # Настройка веса колонок
        for i in range(3):
            parent.columnconfigure(i, weight=1)
    
    def create_menu_item(self, parent, recipe, recipe_id, order_callback):
        """Создание элемента меню"""
        item_frame = ctk.CTkFrame(
            parent, 
            fg_color=COLORS["card_bg"], 
            width=200, 
            height=100,
            corner_radius=15
        )
        item_frame.grid_propagate(False)
        
        # Название блюда
        name_label = ctk.CTkLabel(
            item_frame,
            text=recipe["name"],
            font=("Arial", 14, "bold"),
            text_color=COLORS["warning"],
            wraplength=180
        )
        name_label.pack(pady=10)
        
        # Цена
        price_label = ctk.CTkLabel(
            item_frame,
            text=f"💰 ${recipe['price']}",
            font=("Arial", 12),
            text_color=COLORS["text_secondary"]
        )
        price_label.pack(pady=2)
        
        # Кнопка заказа
        order_btn = ctk.CTkButton(
            item_frame,
            text="ЗАКАЗАТЬ",
            command=lambda rid=recipe_id: order_callback(rid),
            fg_color=COLORS["primary"],
            hover_color="#e55a2b",
            width=120,
            height=30
        )
        order_btn.pack(pady=8)
        
        return item_frame
    
    def create_orders_section(self, parent):
        """Создание раздела заказов"""
        orders_frame = ctk.CTkFrame(parent, fg_color=COLORS["card_bg"])
        
        title = ctk.CTkLabel(
            orders_frame,
            text="📦 МОИ ЗАКАЗЫ",
            font=("Arial", 20, "bold"),
            text_color=COLORS["warning"]
        )
        title.pack(pady=10)
        
        orders_text = ctk.CTkTextbox(
            orders_frame, 
            height=150,
            fg_color=COLORS["dark_bg"],
            text_color=COLORS["text_primary"],
            font=("Arial", 12)
        )
        orders_text.pack(fill="x", padx=10, pady=5)
        orders_text.insert("1.0", "Ваши заказы появятся здесь...")
        orders_text.configure(state="disabled")
        
        self.animations.simple_appear(orders_frame, 600)
        
        return orders_text, orders_frame