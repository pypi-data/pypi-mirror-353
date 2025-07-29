import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import re
import os

# Стили
STYLES = {
    'bg': '#FFFFFF',
    'secondary_bg': '#F4E8D3',
    'accent': '#67BA80',
    'font': 'Segoe UI'
}

def calculate_discount(total_sales):
    if total_sales < 10000:
        return "0%"
    elif total_sales < 50000:
        return "5%"
    elif total_sales < 300000:
        return "10%"
    else:
        return "15%"

def get_db():
    try:
        return psycopg2.connect(
            dbname='amm',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к БД:\n{str(e)}")
        return None

def load_partners():
    conn = get_db()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.*, COALESCE(SUM(pp.product_kolvo), 0) as total_sales
            FROM partners p
            LEFT JOIN partner_products pp ON p.partner_name = pp.partner_name
            GROUP BY p.partner_name
            ORDER BY p.partner_name
        """)
        return cursor.fetchall()
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки данных:\n{str(e)}")
        return []
    finally:
        conn.close()

class PartnerForm(tk.Toplevel):
    def __init__(self, parent, partner=None):
        super().__init__(parent)
        self.title("Добавление партнера" if not partner else "Редактирование партнера")
        self.geometry("500x400")
        self.configure(bg=STYLES['bg'])
        
        # Поля формы
        fields = [
            ("Наименование", "name"),
            ("Тип партнера", "partner_type"),
            ("ФИО директора", "director"),
            ("Email", "email"),
            ("Телефон", "phone"),
            ("Адрес", "address"),
            ("ИНН", "inn"),
            ("Рейтинг", "rating")
        ]
        self.field_order = [f[1] for f in fields]
        
        # Создаем поля ввода
        self.entries = {}
        for label, field in fields:
            frame = tk.Frame(self, bg=STYLES['bg'])
            frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(frame, text=label + ":", bg=STYLES['bg'], font=(STYLES['font'], 10)).pack(side=tk.LEFT)
            
            if field == "partner_type":
                self.entries[field] = ttk.Combobox(frame, values=["OOO", "АОА", "ЗАО", "ПАО"])
            else:
                self.entries[field] = tk.Entry(frame)
            self.entries[field].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Кнопки
        btn_frame = tk.Frame(self, bg=STYLES['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Button(btn_frame, text="Сохранить", command=self.save,
                 bg=STYLES['accent'], fg='white').pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.destroy,
                 bg=STYLES['secondary_bg']).pack(side=tk.RIGHT, padx=5)
        
        # Заполняем форму данными, если они есть
        if partner:
            for field, value in zip(self.field_order, partner):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, value)
    
    def save(self):
        # Проверяем обязательные поля
        if not all(self.entries[field].get().strip() for field in ['name', 'partner_type', 'rating']):
            messagebox.showerror("Ошибка", "Заполните все обязательные поля")
            return
        try:
            rating = int(self.entries['rating'].get())
            if rating <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Ошибка", "Рейтинг должен быть положительным числом")
            return
        conn = get_db()
        if not conn:
            return
        try:
            cursor = conn.cursor()
            # Формируем data в нужном порядке
            data = [self.entries[field].get().strip() for field in self.field_order]
            data[-1] = int(data[-1])  # Рейтинг
            cursor.execute("""
                INSERT INTO partners 
                (partner_name, partner_type, director, email, phone, address, inn, rating)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (partner_name) DO UPDATE
                SET partner_type = EXCLUDED.partner_type,
                    director = EXCLUDED.director,
                    email = EXCLUDED.email,
                    phone = EXCLUDED.phone,
                    address = EXCLUDED.address,
                    inn = EXCLUDED.inn,
                    rating = EXCLUDED.rating
            """, data)
            conn.commit()
            messagebox.showinfo("Успех", "Данные сохранены")
            self.master.refresh_partners()
            self.destroy()
        except psycopg2.Error as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения:\n{str(e)}")
        finally:
            conn.close()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Учет партнеров")
        self.geometry("800x600")
        self.configure(bg=STYLES['bg'])
        
        # Загружаем логотип
        try:
            logo = Image.open("logo.png")
            logo = logo.resize((200, 100), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo)
            tk.Label(self, image=self.logo, bg=STYLES['bg']).pack(pady=10)
        except:
            messagebox.showerror("Ошибка", "Не удалось загрузить логотип")
        
        # Кнопки управления
        btn_frame = tk.Frame(self, bg=STYLES['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Добавить партнера",
                 command=self.add_partner,
                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Обновить",
                 command=self.refresh_partners,
                 bg=STYLES['secondary_bg']).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для карточек
        self.cards_frame = tk.Frame(self, bg=STYLES['bg'])
        self.cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_partners()
    
    def refresh_partners(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
        for partner in load_partners():
            card = tk.Frame(self.cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10, bg=STYLES['bg'])
            card.pack(fill=tk.X, padx=10, pady=5)
            card.bind('<Button-1>', lambda e, p=partner: self.edit_partner(p))
            top_frame = tk.Frame(card, bg=STYLES['bg'])
            top_frame.pack(fill=tk.X)
            header = f"{partner[1]} | {partner[0]}"
            tk.Label(top_frame, text=header, font=(STYLES['font'], 12, 'bold'), bg=STYLES['bg']).pack(side=tk.LEFT, anchor='w')
            discount = calculate_discount(partner[-1])
            tk.Label(top_frame, text=discount, font=(STYLES['font'], 12), bg=STYLES['bg']).pack(side=tk.RIGHT, anchor='e')
            info = f"{partner[2]}\n+7 {partner[4]}\nРейтинг: {partner[7]}"
            tk.Label(card, text=info, anchor='w', justify='left', font=(STYLES['font'], 10), bg=STYLES['bg']).pack(anchor='w', pady=5)
    
    def add_partner(self):
        PartnerForm(self)
    
    def edit_partner(self, partner):
        PartnerForm(self, partner)

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
