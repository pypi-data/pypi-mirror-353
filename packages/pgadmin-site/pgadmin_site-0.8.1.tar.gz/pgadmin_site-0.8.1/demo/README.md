# Демонстрационный экзамен: мебельная компания

## 1. Развертывание БД

1. Откройте pgAdmin или DBeaver
2. Создайте базу данных `furniture_db`
3. Выполните скрипт `schema.sql` для создания таблиц и связей
4. Выполните скрипт `import_data.sql` для загрузки тестовых данных

## 2. Запуск сайта

1. Замените `your_password` в `example_site.py` на ваш пароль PostgreSQL
2. Запустите сайт:
```bash
python demo/example_site.py
```

## 3. Функциональность

### 3.1 Просмотр данных
- Открывается главная страница с карточками продукции
- Каждая карточка показывает:
  - Название изделия
  - Тип модели
  - Материал
  - Цех изготовления
  - Время изготовления
  - Кнопка "Этапы" для просмотра этапов производства

### 3.2 Работа с карточками
- Нажмите "Этапы" на карточке для просмотра этапов производства
- Карточки можно просматривать в виде таблицы (кнопка "К таблицам")
- В табличном виде доступно:
  - Редактирование записей
  - Добавление новых записей
  - Удаление записей
  - Импорт данных из CSV/Excel

### 3.3 Перемещаемое изображение
- На странице есть перемещаемое изображение
- Перетащите его мышью в нужное место
- Позиция сохраняется между сессиями

### 3.4 Импорт данных
1. Нажмите "Импорт" в табличном виде
2. Выберите CSV или Excel файл
3. Файл должен содержать колонки:
   - product: name, model_type, material, workshop_id, production_time
   - workshop: name, location
   - production_stage: product_id, workshop_id, stage_name, stage_time

## 4. Структура БД

### Таблицы:
- `workshop` - цехи
- `product` - продукция
- `production_stage` - этапы изготовления
- `material` - материалы
- `product_material` - использование материалов

### Связи:
- product.workshop_id -> workshop.workshop_id
- production_stage.product_id -> product.product_id
- production_stage.workshop_id -> workshop.workshop_id
- product_material.product_id -> product.product_id
- product_material.material_id -> material.material_id

## 5. Настройка внешнего вида

В `example_site.py` можно настроить:
- `icon` - путь к логотипу
- `foto` - путь к изображению и флаг перемещаемости
- `bkg` - цвет фона
- `sec` - второй цвет
- `acc` - акцентный цвет

## 6. Примеры запросов

### Получение всех изделий с цехами:
```sql
SELECT p.*, w.name as workshop_name 
FROM product p 
JOIN workshop w ON p.workshop_id = w.workshop_id;
```

### Получение этапов производства:
```sql
SELECT p.name, ps.stage_name, ps.stage_time 
FROM product p 
JOIN production_stage ps ON p.product_id = ps.product_id;
```

### Расчет времени на материал:
```sql
SELECT p.name, m.name as material, pm.quantity 
FROM product p 
JOIN product_material pm ON p.product_id = pm.product_id 
JOIN material m ON pm.material_id = m.material_id;
```

## 7. Редактирование карточек

- Запустите редактор карточек:
  ```python
  from pgadmin_site import tkinter_card_designer
  tkinter_card_designer(username="postgres", password="your_password", database="furniture_db")
  ```
- Сохраните шаблон карточки в папку `pgadmin_site/templates/cards/`.
- Запустите сайт с параметром `card="имя_шаблона"`.

## 4. Получение ER-диаграммы

- Откройте pgAdmin/DBeaver, выберите базу, экспортируйте ER-диаграмму в PDF.
- Файл приложите к отчёту.

## 5. Импорт/экспорт данных

- Через веб-интерфейс (будет кнопка "Импорт/Экспорт") или вручную через SQL.

## 6. Примеры и пояснения

- Все примеры строго по экзаменационному заданию.
- Весь код с комментариями.
- Для любых изменений используйте визуальные редакторы библиотеки. 