"""
Пример запуска pgadmin_site для мебельной компании (экзамен)
"""
from pgadmin_site import site

if __name__ == "__main__":
    site(
        host="localhost",           # Адрес сервера PostgreSQL
        port=5432,                   # Порт PostgreSQL
        username="postgres",        # Имя пользователя
        password="your_password",   # Пароль
        database="furniture_db",    # Имя базы данных (создай через schema.sql)
        web_port=5000,               # Порт для веб-интерфейса
        icon="demo/logo.png",       # Логотип (замени на свой при необходимости)
        foto="demo/foto.jpg true",  # Фото (замени на своё, true=перемещаемое)
        card="demo/product_card",   # Шаблон карточки
        bkg="#FFFFFF",              # Цвет фона
        sec="#F4E8D3",              # Второй цвет
        acc="#67BA80"               # Акцент
    ) 