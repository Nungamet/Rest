import customtkinter as ctk
from config import COLORS

class AnimationManager:
    def __init__(self, root):
        self.root = root
    
    def fade_in(self, widget, duration=800, callback=None):
        """Плавное появление через изменение цвета"""
        try:
            # Сохраняем оригинальный цвет
            original_color = widget.cget("fg_color") if hasattr(widget, 'cget') and widget.cget("fg_color") else COLORS["card_bg"]
            
            # Начинаем с почти черного цвета
            widget.configure(fg_color="#0a0a0a")
            
            def animate(step=0):
                # Плавно изменяем цвет к оригинальному
                if step <= 20:
                    # Вычисляем промежуточный цвет
                    r1, g1, b1 = 10, 10, 10  # Начальный темный цвет
                    r2, g2, b2 = self.hex_to_rgb(original_color)
                    
                    r = int(r1 + (r2 - r1) * (step / 20))
                    g = int(g1 + (g2 - g1) * (step / 20))
                    b = int(b1 + (b2 - b1) * (step / 20))
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    try:
                        widget.configure(fg_color=color)
                    except:
                        pass
                    
                    self.root.after(duration // 20, lambda: animate(step + 1))
                elif callback:
                    callback()
            
            animate()
        except Exception as e:
            print(f"Ошибка анимации fade_in: {e}")
            if callback:
                callback()
    
    def hex_to_rgb(self, hex_color):
        """Конвертирует hex цвет в RGB"""
        try:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return (43, 43, 43)  # fallback цвет
    
    def slide_from_top(self, widget, duration=1000, callback=None):
        """Скольжение сверху - упрощенная версия"""
        try:
            # Просто показываем виджет с задержкой
            widget.pack_forget()
            self.root.after(200, lambda: widget.pack(fill="x", padx=10, pady=10))
            
            if callback:
                self.root.after(duration, callback)
        except:
            if callback:
                callback()
    
    def typewriter_effect(self, widget, text, speed=100, callback=None):
        """Эффект печатной машинки"""
        try:
            widget.configure(text="")
            current_text = ""
            
            def type_char(index=0):
                nonlocal current_text
                if index < len(text):
                    current_text += text[index]
                    try:
                        widget.configure(text=current_text)
                    except:
                        pass
                    self.root.after(speed, lambda: type_char(index + 1))
                elif callback:
                    callback()
            
            type_char()
        except:
            widget.configure(text=text)
            if callback:
                callback()
    
    def bounce_in(self, widget, duration=600, callback=None):
        """Прыгающее появление через изменение шрифта"""
        try:
            original_font = widget.cget("font")
            if isinstance(original_font, tuple):
                original_size = original_font[1]
            else:
                original_size = 24
            
            def animate(step=0):
                if step == 0:
                    new_size = 8
                elif step < 8:
                    new_size = 28
                else:
                    new_size = original_size
                    
                try:
                    if hasattr(widget, 'configure'):
                        if isinstance(original_font, tuple):
                            new_font = (original_font[0], new_size) + original_font[2:]
                        else:
                            new_font = ("Arial", new_size, "bold")
                        widget.configure(font=new_font)
                except:
                    pass
                
                if step < 10:
                    self.root.after(duration // 10, lambda: animate(step + 1))
                elif callback:
                    callback()
            
            animate()
        except:
            if callback:
                callback()
    
    def stagger_children(self, parent, animation_type="fade", delay=100):
        """Последовательная анимация дочерних элементов"""
        try:
            children = parent.winfo_children()
            
            for i, child in enumerate(children):
                if animation_type == "fade":
                    self.root.after(i * delay, lambda w=child: self.fade_in(w))
                elif animation_type == "slide":
                    self.root.after(i * delay, lambda w=child: self.slide_from_top(w))
        except:
            pass

    def simple_appear(self, widget, delay=0):
        """Простое появление с задержкой"""
        try:
            self.root.after(delay, lambda: widget.pack(fill="x", padx=10, pady=10))
        except:
            pass

    def fade_in_text(self, widget, duration=1000, callback=None):
        """Анимация появления текста из невидимого в видимый"""
        try:
            # Сохраняем оригинальный цвет текста
            original_color = widget.cget("text_color")
            
            # Начинаем с невидимого (совпадает с фоном)
            widget.configure(text_color=COLORS["dark_bg"])
            
            def animate(step=0):
                if step <= 20:
                    # Плавно изменяем цвет текста
                    r1, g1, b1 = self.hex_to_rgb(COLORS["dark_bg"])
                    r2, g2, b2 = self.hex_to_rgb(original_color)
                    
                    r = int(r1 + (r2 - r1) * (step / 20))
                    g = int(g1 + (g2 - g1) * (step / 20))
                    b = int(b1 + (b2 - b1) * (step / 20))
                    
                    color = f"#{r:02x}{g:02x}{b:02x}"
                    
                    try:
                        widget.configure(text_color=color)
                    except:
                        pass
                    
                    self.root.after(duration // 20, lambda: animate(step + 1))
                elif callback:
                    callback()
            
            animate()
        except Exception as e:
            print(f"Ошибка анимации текста: {e}")
            if callback:
                callback()
    
    def slide_text_from_top(self, widget, start_y=0.3, end_y=0.5, duration=800, callback=None):
        """Анимация перемещения текста сверху вниз"""
        try:
            # Получаем текущее положение
            widget.place(relx=0.5, rely=start_y, anchor="center")
            
            def animate(step=0):
                if step <= 20:
                    # Плавно изменяем позицию Y
                    current_y = start_y + (end_y - start_y) * (step / 20)
                    try:
                        widget.place(relx=0.5, rely=current_y, anchor="center")
                    except:
                        pass
                    
                    self.root.after(duration // 20, lambda: animate(step + 1))
                elif callback:
                    callback()
            
            animate()
        except Exception as e:
            print(f"Ошибка анимации перемещения: {e}")
            if callback:
                callback()