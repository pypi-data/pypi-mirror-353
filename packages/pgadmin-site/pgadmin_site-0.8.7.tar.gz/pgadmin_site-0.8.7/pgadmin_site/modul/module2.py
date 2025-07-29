import psycopg2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox


def calculate_discount(total_sales):
    if total_sales < 10000:
        return "0%"
    elif total_sales < 50000:
        return "5%"
    elif total_sales < 300000:
        return "10%"
    else:
        return "15%"

def load_partners():
    conn = psycopg2.connect(
        dbname='amm',
        user='postgres',
        password='postgres',
        host='localhost',  # или другой адрес сервера
        port='5432'        # стандартный порт PostgreSQL
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            p.partner_name, p.partner_type, p.director, p.phone, p.rating,
            COALESCE(SUM(pp.product_kolvo), 0) AS total_sales
        FROM
            partners p
        LEFT JOIN
            partner_products pp ON p.partner_name = pp.partner_name
        GROUP BY
            p.partner_name
        ORDER BY
            p.partner_name
    """)
    partners = cursor.fetchall()
    conn.close()
    return partners

def show_partners():
    # Очищаем старые карточки, если они есть
    for widget in cards_frame.winfo_children():
        widget.destroy()
    partners = load_partners()
    for partner in partners:
        partner_name, partner_type, director, phone, rating, total_sales = partner
        discount = calculate_discount(total_sales)

        card = tk.Frame(cards_frame, bd=1, relief=tk.SOLID, padx=10, pady=10)
        card.pack(fill=tk.X, padx=10, pady=10)

        # Верхняя строка: Тип | Имя партнера и скидка справа
        top_frame = tk.Frame(card)
        top_frame.pack(fill=tk.X)
        left_label = tk.Label(top_frame, text=f"{partner_type} | {partner_name}", font=("Arial", 14))
        left_label.pack(side=tk.LEFT, anchor="w")
        right_label = tk.Label(top_frame, text=discount, font=("Arial", 14))
        right_label.pack(side=tk.RIGHT, anchor="e")

        # Остальная информация
        info_label = tk.Label(card, text=f"Директор {director}\n{phone}\nРейтинг: {rating}", anchor="w", justify="left")
        info_label.pack(anchor="w", pady=(5, 0))

root = tk.Tk()
root.title("Учет партнеров")
try:
    logo = Image.open("Мастер пол.png")
    logo = logo.resize((100, 100), Image.Resampling.LANCZOS)
    logo = ImageTk.PhotoImage(logo)
    root.iconphoto(True, logo)
except:
    messagebox.showerror("Ошибка", "Не удалось загрузить логотип")
# cards_frame для карточек
cards_frame = tk.Frame(root)
cards_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

show_partners()

root.mainloop()
