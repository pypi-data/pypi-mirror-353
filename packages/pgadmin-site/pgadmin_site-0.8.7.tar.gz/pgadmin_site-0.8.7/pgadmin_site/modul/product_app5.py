import psycopg2
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import re
import os

import csv

# Стили (стили могут быть адаптированы позже)
STYLES = {
    'bg': '#FFFFFF',
    'secondary_bg': '#F4E8D3',
    'accent': '#67BA80',
    'font': 'Segoe UI'
}

def export_to_csv():
    conn = get_db()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("select * from partners;")
        with open("out.csv", "w", newline='') as csv_file:   
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([i[0] for i in cursor.description]) # write headers
            csv_writer.writerows(cursor)
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка экспорта в CSV: {str(e)}")
    finally:
        conn.close()

def get_db():
    """Устанавливает соединение с базой данных."""
    try:
        # Обновляем параметры подключения, если необходимо
        return psycopg2.connect(
            dbname='amm',
            user='postgres',
            password='postgres',
            host='localhost',
            port='5432'
        )
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка подключения к БД: {str(e)}")
        return None

def load_products():
    """Загружает список продуктов из БД и рассчитывает общее время изготовления."""
    conn = get_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        # Изменяем запрос для расчета общего времени изготовления из product_workshop_times
        cursor.execute("""
            SELECT
                p.product_id,
                p.product_type,
                p.product_name,
                p.article,
                p.min_partner_price,
                p.main_material,
                COALESCE(SUM(pwt.time_in_workshop), 0) AS total_manufacturing_time
            FROM products p
            LEFT JOIN product_workshop_times pwt ON p.article = pwt.product_article
            GROUP BY p.product_id, p.product_type, p.product_name, p.article, p.min_partner_price, p.main_material
            ORDER BY p.product_name
        """)
        return cursor.fetchall()
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки продуктов: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

def delete_product(product_id):
    """Удаляет продукт из БД по ID. Каскадное удаление в product_workshop_times."""
    conn = get_db()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # Благодаря ON DELETE CASCADE в таблице product_workshop_times, связанные записи удалятся автоматически
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        conn.commit()
        messagebox.showinfo("Успех", "Продукт успешно удален")
        return True
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка удаления продукта: {str(e)}")
        conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def load_workshops():
    """Загружает список цехов из БД."""
    conn = get_db()
    if not conn:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT workshop_id, workshop_name, num_people, manufacturing_time_per_product
            FROM workshops
            ORDER BY workshop_name
        """)
        return cursor.fetchall()
    except psycopg2.Error as e:
        messagebox.showerror("Ошибка", f"Ошибка загрузки цехов: {str(e)}")
        return []
    finally:
        if conn:
            conn.close()

class ProductForm(tk.Toplevel):
    """Форма для добавления или редактирования продукта."""
    def __init__(self, parent, product=None):
        super().__init__(parent)
        self.title("Добавление продукта" if not product else "Редактирование продукта")
        self.geometry("500x400") # Reverted geometry
        self.configure(bg=STYLES['bg'])

        self.product = product # Store product data if editing

        # --- Секция Основных данных продукта ---
        main_data_frame = tk.LabelFrame(self, text="Данные продукта", bg=STYLES['bg'], padx=10, pady=10)
        main_data_frame.pack(fill=tk.X, padx=20, pady=10)

        fields = [
            ("Тип продукта", 'product_type'),
            ("Наименование продукта", 'product_name'),
            ("Артикул", 'article'),
            ("Минимальная стоимость для партнёра", 'min_partner_price'),
            ("Основной материал", 'main_material')
        ]
        self.field_names = [f[1] for f in fields]

        self.entries = {}
        for label, field_name in fields:
            frame = tk.Frame(main_data_frame, bg=STYLES['bg'])
            frame.pack(fill=tk.X, pady=2)

            tk.Label(frame, text=label + ":", bg=STYLES['bg'], font=(STYLES['font'], 10)).pack(side=tk.LEFT, anchor='w')

            if field_name == 'product_type':
                self.entries[field_name] = ttk.Combobox(frame, values=["Стол", "Стул", "Кровать"], state='readonly')
            else:
                # Артикул не должен меняться при редактировании
                state = tk.NORMAL if not product or field_name != 'article' else tk.DISABLED
                self.entries[field_name] = tk.Entry(frame, state=state)

            self.entries[field_name].pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Заполняем основные данные, если редактируем
        if product:
             product_data = {
                'product_id': product[0],
                'product_type': product[1],
                'product_name': product[2],
                'article': product[3],
                'min_partner_price': product[4],
                'main_material': product[5]
            }
             for field_name in self.field_names:
                if field_name in product_data:
                    value = product_data[field_name]
                    # Handle Combobox separately
                    if field_name == 'product_type':
                         self.entries[field_name].set(str(value) if value is not None else "")
                    else:
                         self.entries[field_name].insert(0, str(value) if value is not None else "")

        # --- Кнопки Сохранить/Отмена для всей формы ---
        btn_frame = tk.Frame(self, bg=STYLES['bg'])
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        tk.Button(btn_frame, text="Сохранить", command=self.save, bg=STYLES['accent'], fg='white').pack(side=tk.RIGHT, padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.destroy, bg=STYLES['secondary_bg']).pack(side=tk.RIGHT, padx=5)

        if product:
            for field, value in zip(self.field_names, product):
                self.entries[field].delete(0, tk.END)
                self.entries[field].insert(0, value)
                
    def save(self):
        # Собираем основные данные продукта из полей
        product_data = {}
        for field_name in self.field_names:
            product_data[field_name] = self.entries[field_name].get().strip()

        # Проверяем обязательные поля (наименование и артикул)
        if not product_data['product_name'] or not product_data['article']:
            messagebox.showerror("Ошибка", "Заполните обязательные поля: Наименование продукта, Артикул")
            return
            
        # Проверяем, что тип продукта выбран
        if not product_data['product_type']:
             messagebox.showerror("Ошибка", "Выберите тип продукта")
             return

        # Преобразуем числовые поля и проверяем неотрицательность стоимости
        try:
            min_price_str = product_data['min_partner_price']
            if min_price_str:
                min_price = float(min_price_str)
                if min_price < 0:
                     messagebox.showerror("Ошибка", "Минимальная стоимость для партнёра не может быть отрицательной")
                     return
                product_data['min_partner_price'] = min_price
            else:
                 product_data['min_partner_price'] = None

        except ValueError:
            messagebox.showerror("Ошибка", "Минимальная стоимость для партнёра должна быть числом")
            return

        # --- Начало логики сохранения в БД ---
        conn = get_db()
        if not conn:
            return # get_db already showed error

        try:
            cursor = conn.cursor()

            # Используем INSERT ... ON CONFLICT (article) DO UPDATE
            # Это соответствует структуре сохранения в module4.py и упрощает логику
            cursor.execute("""
                INSERT INTO products
                (product_type, product_name, article, min_partner_price, main_material)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (article) DO UPDATE
                SET product_type = EXCLUDED.product_type,
                    product_name = EXCLUDED.product_name,
                    min_partner_price = EXCLUDED.min_partner_price,
                    main_material = EXCLUDED.main_material
            """, (
                product_data['product_type'],
                product_data['product_name'],
                product_data['article'],
                product_data['min_partner_price'],
                product_data['main_material']
            ))

            # Определяем, было ли это добавление или обновление для сообщения пользователю
            # Можно использовать cursor.rowcount, но ON CONFLICT может вернуть 0 даже при UPDATE
            # Проще проверить, были ли данные продукта переданы при создании формы
            if self.product:
                 messagebox.showinfo("Успех", "Данные продукта обновлены")
            else:
                 messagebox.showinfo("Успех", "Новый продукт добавлен")

            conn.commit()
            self.master.refresh_products() # Обновляем список в главном окне
            self.destroy() # Закрываем форму после успешного сохранения

        except psycopg2.Error as e:
            # Обработка ошибок БД, включая возможные нарушения уникальности (кроме артикула, который теперь обрабатывается ON CONFLICT)
            messagebox.showerror("Ошибка", f"Ошибка сохранения продукта в БД: {str(e)}")
            conn.rollback()
        except Exception as e:
            # Общие исключения
            messagebox.showerror("Ошибка", f"Неизвестная ошибка при сохранении продукта: {str(e)}")
        finally:
            if conn:
                conn.close()
        # --- Конец логики сохранения в БД ---

class WorkshopWindow(tk.Toplevel):
    """Окно для отображения информации о цехах."""
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Информация о цехах")
        self.geometry("600x400")
        self.configure(bg=STYLES['bg'])
        
        # Таблица для цехов
        columns = ("workshop_name", "num_people", "manufacturing_time_per_product")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        
        # Настройка заголовков
        self.tree.heading("workshop_name", text="Название цеха")
        self.tree.heading("num_people", text="Количество человек")
        self.tree.heading("manufacturing_time_per_product", text="Время изготовления (ед.)")
        
        # Размещаем таблицу
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Загружаем данные
        self.load_workshops()

    def load_workshops(self):
        workshops = load_workshops()
        
        # Очищаем существующие данные
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Добавляем новые данные
        for row in workshops:
            self.tree.insert("", tk.END, values=row[1:]) # Skip workshop_id

class ProductApp(tk.Tk):
    """Главное приложение для управления продуктами."""
    def __init__(self):
        super().__init__()
        self.title("Управление продуктами")
        self.geometry("800x600")
        self.configure(bg=STYLES['bg'])
        
        # Загрузка логотипа (опционально, можно адаптировать)
        try:
            # Убедитесь, что файл 'Мастер пол.png' существует или замените его
            logo = Image.open("Мастер пол.png") 
            logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
            self.logo = ImageTk.PhotoImage(logo)
            self.iconphoto(True, self.logo)
        except Exception as e:
            print(f"Ошибка загрузки логотипа: {e}") # Print error instead of messagebox for startup
        
        # Кнопки управления
        btn_frame = tk.Frame(self, bg=STYLES['bg'])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="Добавить продукт",
                 command=self.add_product,
                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="Обновить",
                 command=self.refresh_products,
                 bg=STYLES['secondary_bg']).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(btn_frame, text="Цехи",
                 command=self.show_workshops,
                 bg=STYLES['accent'], fg='white').pack(side=tk.LEFT, padx=5)
        
        # Фрейм для карточек продуктов
        self.cards_frame = tk.Frame(self, bg=STYLES['bg'])
        self.cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Обновляем список продуктов при запуске
        self.refresh_products()
    
    def refresh_products(self):
        """Загружает и отображает карточки продуктов."""
        # Очищаем существующие карточки
        for widget in self.cards_frame.winfo_children():
            widget.destroy()
            
        products = load_products()

        if not products:
            tk.Label(self.cards_frame, text="Нет данных о продуктах.", bg=STYLES['bg'], font=(STYLES['font'], 12)).pack(pady=20)
            return

        for product in products:
            # Создаем фрейм для карточки продукта
            card = tk.Frame(self.cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10, bg=STYLES['bg'])
            card.pack(fill=tk.X, padx=10, pady=5)
            
            # Привязываем событие клика для редактирования
            # Передаем полную информацию о продукте
            card.bind('<Button-1>', lambda e, p=product: self.edit_product(p))
            
            # Фрейм для верхней строки (Тип | Наименование продукта и Время изготовления)
            top_frame = tk.Frame(card, bg=STYLES['bg'])
            top_frame.pack(fill=tk.X)
            
            # Тип | Наименование продукта
            header_text = f"{product[1] or ''} | {product[2] or 'Неизвестный продукт'}" # Use index 1 for type, 2 for name
            tk.Label(top_frame, text=header_text, font=(STYLES['font'], 12, 'bold'), bg=STYLES['bg']).pack(side=tk.LEFT, anchor='w')
            
            # Время изготовления (справа)
            manufacturing_time_text = f"Время изготовления: {product[6] or '-'}" # Use index 6 for manufacturing_time
            tk.Label(top_frame, text=manufacturing_time_text, font=(STYLES['font'], 10), bg=STYLES['bg']).pack(side=tk.RIGHT, anchor='e')
            
            # Информация о продукте (Артикул, Мин. стоимость, Материал) ниже
            # Using a consistent structure for these lines
            info_lines = [
                f"Артикул: {product[3] or '-'}", # Use index 3 for article
                f"Минимальная стоимость для партнёра: {product[4] if product[4] is not None else '-'}", # Use index 4 for min_partner_price
                f"Основной материал: {product[5] or '-'}" # Use index 5 for main_material
            ]
            
            for line_text in info_lines:
                tk.Label(card, text=line_text, justify='left', font=(STYLES['font'], 10), bg=STYLES['bg']).pack(anchor='w', pady=1) # Reduced pady

    def add_product(self):
        """Открывает форму для добавления нового продукта."""
        ProductForm(self)
    
    def edit_product(self, product):
        """Открывает форму для редактирования продукта."""
        ProductForm(self, product)

    def show_workshops(self):
        """Открывает окно с информацией о цехах."""
        WorkshopWindow(self)

# Точка входа в приложение
if __name__ == "__main__":
    app = ProductApp()
    app.mainloop() 