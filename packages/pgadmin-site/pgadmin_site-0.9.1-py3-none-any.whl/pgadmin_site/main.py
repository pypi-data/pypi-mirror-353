"""
Основной модуль, содержащий функцию site для создания веб-интерфейса.
"""

import os
import logging
from typing import Optional
import psycopg2
import shutil
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, flash, send_from_directory
from sqlalchemy import create_engine, MetaData, Table, Column, inspect, text, select
from sqlalchemy.exc import SQLAlchemyError
from flask_sqlalchemy import SQLAlchemy
import json
from werkzeug.utils import secure_filename
import io
import csv
import pathlib
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False
import pkg_resources

# Настройка логирования
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def site(host: str, 
         port: int = 5432, 
         username: str = "postgres", 
         password: str = "", 
         database: str = "postgres", 
         web_port: int = 5000,
         debug: bool = False,
         card: str = None,
         icon: str = None,
         foto: str = None,
         bkg: str = "#FFFFFF",
         sec: str = "#F4E8D3",
         acc: str = "#67BA80"):
    """
    Создать и запустить локальный веб-сайт для работы с таблицами PostgreSQL или карточками.
    Args:
        host: Хост PostgreSQL сервера
        port: Порт PostgreSQL сервера
        username: Имя пользователя PostgreSQL
        password: Пароль PostgreSQL
        database: Имя базы данных PostgreSQL
        web_port: Порт для веб-интерфейса
        debug: Включить режим отладки
        card: Название шаблона карточки (без .json) для отображения карточек вместо таблиц
        icon: Путь к файлу иконки (.jpg, .png или .jpeg)
        foto: Путь к файлу изображения (.jpg, .png или .jpeg) с опциональным параметром movable (true/false)
        bkg: основной фон (по умолчанию #FFFFFF)
        sec: дополнительный фон (по умолчанию #F4E8D3)
        acc: акцент (по умолчанию #67BA80)
    """
    # Создаем Flask приложение
    app = Flask(__name__)
    app.secret_key = os.urandom(24)
    app.config['DEBUG'] = debug
    
    # Проверка и установка иконки
    if icon:
        if not os.path.exists(icon):
            raise ValueError(f"Файл иконки не найден: {icon}")
        if not icon.lower().endswith((".jpg", ".jpeg", ".png", ".ico")):
            raise ValueError("Иконка должна быть в формате .jpg, .jpeg, .png или .ico")
        
        # Копируем иконку в статическую директорию
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        icon_filename = 'favicon' + os.path.splitext(icon)[1]
        icon_path = os.path.join(static_dir, icon_filename)
        shutil.copy2(icon, icon_path)
        
        # Добавляем маршрут для фавикона
        @app.route('/favicon.ico')
        def favicon():
            return send_from_directory(static_dir, icon_filename)

    # Обработка параметра foto
    foto_enabled = False
    foto_movable = False
    foto_url = None
    if foto:
        foto_parts = foto.split()
        foto_path = foto_parts[0]
        foto_movable = len(foto_parts) > 1 and foto_parts[1].lower() == 'true'
        foto_enabled = True
        if not os.path.exists(foto_path):
            raise ValueError(f"Файл изображения не найден: {foto_path}")
        if not foto_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise ValueError("Изображение должно быть в формате .jpg, .jpeg или .png")
        
        # Копируем изображение в статическую директорию
        static_dir = os.path.join(os.path.dirname(__file__), 'static')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        
        foto_filename = 'foto' + os.path.splitext(foto_path)[1]
        foto_path_dest = os.path.join(static_dir, foto_filename)
        shutil.copy2(foto_path, foto_path_dest)
        
        # Создаем файл для хранения позиции изображения
        position_file = os.path.join(static_dir, 'foto_position.json')
        if not os.path.exists(position_file):
            with open(position_file, 'w') as f:
                json.dump({'x': 0, 'y': 0}, f)
        
        # Добавляем маршруты для работы с изображением
        foto_url = '/foto'
        @app.route('/foto')
        def get_foto():
            return send_from_directory(static_dir, foto_filename)
        
        @app.route('/foto/position/<card_name>', methods=['GET', 'POST'])
        def foto_position(card_name):
            # Используем имя карточки для уникального файла позиции
            position_file = os.path.join(os.path.dirname(__file__), 'static', f'foto_position_{secure_filename(card_name)}.json')
            
            if request.method == 'POST':
                data = request.json
                try:
                    with open(position_file, 'r') as f:
                        pos = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pos = {'x': 0, 'y': 0, 'deleted': False}

                # Если удаление
                if data.get('deleted') is True:
                    pos['deleted'] = True
                # Если просто перемещение
                else:
                    pos['x'] = data.get('x', pos.get('x', 0))
                    pos['y'] = data.get('y', pos.get('y', 0))
                    # Убедимся, что флаг удаления не сбрасывается при перемещении
                    pos.setdefault('deleted', False)

                with open(position_file, 'w') as f:
                    json.dump(pos, f)
                return jsonify({'status': 'ok'})
            else:
                try:
                    with open(position_file, 'r') as f:
                        pos = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    pos = {'x': 0, 'y': 0, 'deleted': False}
                # Гарантируем наличие всех ключей
                pos.setdefault('x', 0)
                pos.setdefault('y', 0)
                pos.setdefault('deleted', False)
                return jsonify(pos)
    
    # Настраиваем подключение к базе данных
    connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db = SQLAlchemy(app)
    
    # Создаем прямое подключение к базе данных через SQLAlchemy
    # вместо использования db.engine, которое требует контекст приложения
    engine = create_engine(connection_string)
    
    # Получаем метаданные базы данных
    metadata = MetaData()
    inspector = inspect(engine)

    def load_card_template(card_name):
        # Если card_name — это путь к существующему файлу, используем его напрямую
        if os.path.isfile(card_name):
            path = card_name
        else:
            # Если card_name оканчивается на .json, не добавляем ещё раз
            if card_name.endswith('.json'):
                fname = card_name
            else:
                fname = f"{card_name}.json"
            # Сначала ищем в текущей директории запуска
            cwd_path = os.path.abspath(fname)
            if os.path.isfile(cwd_path):
                path = cwd_path
            else:
                # По умолчанию ищем в стандартной папке
                path = os.path.join(os.path.dirname(__file__), "templates", "cards", fname)
                if not os.path.isfile(path):
                    return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def get_stages(product_id):
        with engine.connect() as connection:
            result = connection.execute(text('SELECT * FROM production_stage WHERE product_id = :pid'), {'pid': product_id})
            return list(result.mappings())

    def eval_formula(formula, row):
        import decimal, datetime, re
        # ВРЕМЕННО: логируем все ключи строки
        logging.info(f"ROW KEYS: {list(row.keys())}, ROW: {row}")
        if not formula:
            return ''
        f = formula
        # Собираем маппинг коротких имён
        short_map = {}
        for k, v in row.items():
            if '.' in k:
                short = k.split('.', 1)[1]
                if short not in short_map:
                    short_map[short] = k
                else:
                    short_map[short] = None  # Неуникальное короткое имя
            else:
                short_map[k] = k
        # Подстановка значений
        def repl(m):
            key = m.group(1)
            full_key = key
            if key not in row:
                # Пробуем найти по короткому имени
                full_key = short_map.get(key)
            val = row.get(full_key)
            if isinstance(val, decimal.Decimal):
                val = float(val)
            elif isinstance(val, datetime.date):
                val = val.isoformat()
            return repr(val) if val is not None else 'None'
        f = re.sub(r'\{([\w\.]+)\}', repl, f)
        # Добавляем get_stages в контекст формулы
        try:
            return str(eval(f, {"get_stages": get_stages, "sum": sum, "row": row}))
        except Exception as e:
            return f"[Ошибка формулы: {e}]"

    common_ctx = dict(foto_enabled=foto_enabled, foto_movable=foto_movable, foto_url=foto_url, bkg=bkg, sec=sec, acc=acc)

    @app.route('/')
    def index():
        if card:
            card_template = load_card_template(card)
            if not card_template:
                return render_template('error.html', error=f"Шаблон карточки '{card}' не найден.", **common_ctx)
            
            try:
                table_names = inspector.get_table_names()
                if not table_names:
                     return render_template('error.html', error="В базе данных нет таблиц.", **common_ctx)

                # --- Собираем все нужные (таблица, столбец) из шаблона --- 
                needed_cols = set()
                used_tables = []
                import re

                # Собираем столбцы из db_column и formula
                for fig in card_template:
                    # Из db_column
                    db_col = fig.get('db_column')
                    db_table = fig.get('db_table')
                    if db_col and db_table:
                         needed_cols.add((db_table, db_col))
                         if db_table not in used_tables:
                             used_tables.append(db_table)
                    
                    # Из formula (ищем {table.column})
                    if fig.get('formula'):
                        for m in re.findall(r'\{(\w+)\.(\w+)\}', fig['formula']):
                             t, c = m
                             needed_cols.add((t, c))
                             if t not in used_tables:
                                 used_tables.append(t)
                        # Также ищем {column} для случая без префикса таблицы
                        for m in re.findall(r'\{([^\.\}]+)\}', fig['formula']):
                             col_name = m
                             # Пробуем найти этот столбец в каждой таблице
                             found_in_tables = []
                             for t_name in table_names:
                                 columns = inspector.get_columns(t_name)
                                 if col_name in [col['name'] for col in columns]:
                                     needed_cols.add((t_name, col_name))
                                     if t_name not in used_tables:
                                         used_tables.append(t_name)
                                     found_in_tables.append(t_name)
                             # Если найден в нескольких таблицах, это неоднозначно, но мы добавили во все

                # Если нет нужных таблиц, берем первую попавшуюся для запроса
                if not used_tables:
                     main_table = table_names[0]
                     used_tables.append(main_table)
                     # Добавляем все столбцы из этой таблицы, если шаблон пустой
                     if not needed_cols:
                          columns = inspector.get_columns(main_table)
                          for col in columns:
                               needed_cols.add((main_table, col['name']))

                main_table = used_tables[0] # Берем первую таблицу как основную для FROM
                join_tables = used_tables[1:] # Остальные таблицы для JOIN

                # --- Автоматически строим JOIN по foreign key --- 
                joins = []
                # Словарь для хранения уже добавленных пар таблиц в JOIN, чтобы избежать дублирования
                joined_pairs = set()

                # Начинаем с основной таблицы и пытаемся присоединить остальные
                current_tables_in_join = {main_table}
                sql_joins = ''

                # Итерируемся по всем таблицам, которые нужно присоединить
                while join_tables:
                    joined_something = False
                    remaining_join_tables = []

                    for t_to_join in join_tables:
                        # Ищем внешние ключи, которые соединяют t_to_join с уже присоединенными таблицами
                        found_join = False
                        # Проверяем внешние ключи в текущей таблице (t_to_join)
                        fks_in_current = inspector.get_foreign_keys(t_to_join)
                        for fk in fks_in_current:
                             if fk['referred_table'] in current_tables_in_join:
                                 from_table = t_to_join
                                 to_table = fk['referred_table']
                                 # Создаем условие JOIN (предполагаем простой случай с одним столбцом)
                                 join_condition = f'"{from_table}"."{fk['constrained_columns'][0]}" = "{to_table}"."{fk['referred_columns'][0]}"'
                                 # Добавляем JOIN, если эта пара еще не добавлена
                                 if (from_table, to_table) not in joined_pairs and (to_table, from_table) not in joined_pairs:
                                     sql_joins += f' LEFT JOIN "{from_table}" ON {join_condition}'
                                     current_tables_in_join.add(from_table)
                                     joined_pairs.add((from_table, to_table))
                                     found_join = True
                                     break # Нашли связь, переходим к следующей таблице

                        if not found_join:
                             # Проверяем внешние ключи в уже присоединенных таблицах, ссылающиеся на t_to_join
                             for t_in_join in list(current_tables_in_join):
                                 if t_in_join != t_to_join: # Избегаем проверки на саму себя
                                     fks_in_joined = inspector.get_foreign_keys(t_in_join)
                                     for fk in fks_in_joined:
                                         if fk['referred_table'] == t_to_join:
                                             from_table = t_in_join
                                             to_table = t_to_join
                                             join_condition = f'"{from_table}"."{fk['constrained_columns'][0]}" = "{to_table}"."{fk['referred_columns'][0]}"'
                                             if (from_table, to_table) not in joined_pairs and (to_table, from_table) not in joined_pairs:
                                                 sql_joins += f' LEFT JOIN "{to_table}" ON {join_condition}'
                                                 current_tables_in_join.add(to_table)
                                                 joined_pairs.add((from_table, to_table))
                                                 found_join = True
                                                 break
                                 if found_join: break

                        if found_join:
                            joined_something = True
                        else:
                            remaining_join_tables.append(t_to_join)

                    join_tables = remaining_join_tables
                    # Если на этом шаге ничего не присоединили, выходим, чтобы избежать бесконечного цикла
                    if not joined_something and join_tables: 
                         # Обработка случая, когда нет прямых FK связей между всеми нужными таблицами
                         # В таком случае просто выбираем из основной таблицы и добавляем предупреждение
                         logger.warning(f"Не удалось автоматически построить JOIN для всех нужных таблиц: {join_tables}. Будут показаны только данные из {main_table}.")
                         sql_joins = '' # Сбрасываем JOINы, если не удалось соединить все
                         needed_cols = [(main_table, col['name']) for col in inspector.get_columns(main_table)]
                         break # Выходим из цикла while
                    if not join_tables: break # Все таблицы присоединены или нет таблиц для присоединения


                # --- Собираем SELECT столбцы с алиасами table.column --- 
                select_cols_str = ', '.join([f'"{t}"."{c}" AS "{t}.{c}"' for t, c in needed_cols]) if needed_cols else '*' # Если нет нужных столбцов, выбираем все
                
                sql = f'SELECT {select_cols_str} FROM "{main_table}" {sql_joins} LIMIT 100'
                
                logger.info(f"Generated SQL query for cards: {sql}")
                
                with engine.connect() as connection:
                    result = connection.execute(text(sql))
                    data = [dict(row) for row in result.mappings()]

                logger.info(f"DATA for cards: {data}")

                # --- Обработка фото, привязанного к карточке --- 
                foto_enabled_for_card = False
                foto_url_for_card = None
                foto_movable_for_card = False

                if foto and card: # Активируем фото только если указан card
                     foto_parts = foto.split()
                     foto_path = foto_parts[0]
                     foto_movable_for_card = len(foto_parts) > 1 and foto_parts[1].lower() == 'true'
                     
                     if os.path.exists(foto_path):
                          # Копируем фото, если его еще нет в static для этого card
                          static_dir = os.path.join(os.path.dirname(__file__), 'static')
                          foto_filename = f'foto_{secure_filename(card)}{os.path.splitext(foto_path)[1]}'
                          foto_path_dest = os.path.join(static_dir, foto_filename)
                          if not os.path.exists(foto_path_dest):
                               os.makedirs(static_dir, exist_ok=True)
                               shutil.copy2(foto_path, foto_path_dest)

                          foto_url_for_card = url_for('static', filename=foto_filename)
                          foto_enabled_for_card = True
                     else:
                          logger.warning(f"Файл фото для карточки не найден: {foto_path}")
                
                # Обновляем common_ctx для передачи в шаблон
                card_common_ctx = common_ctx.copy()
                card_common_ctx['foto_enabled'] = foto_enabled_for_card
                card_common_ctx['foto_movable'] = foto_movable_for_card
                card_common_ctx['foto_url'] = foto_url_for_card
                # В шаблон card_svg.html мы передаем имя карточки для использования в JS
                card_common_ctx['card_name'] = card
                # Также передаем флаг foto_enabled в обычный common_ctx для index и table view
                common_ctx['foto_enabled'] = foto_enabled # Это для index.html и table.html, если они будут использовать фото

                return render_template('card_svg.html', card_template=card_template, data=data, abs=abs, eval_formula=eval_formula, **card_common_ctx)

            except SQLAlchemyError as e:
                logger.error(f"Ошибка при работе с базой данных при загрузке карточек: {str(e)}")
                return render_template('error.html', error=f"Ошибка при загрузке карточек: {str(e)}", **common_ctx)
            except Exception as e:
                 logger.error(f"Непредвиденная ошибка при загрузке карточек: {str(e)}")
                 return render_template('error.html', error=f"Непредвиденная ошибка: {str(e)}", **common_ctx)

        else:
            # Логика для отображения списка таблиц, если card не указан
            try:
                table_names = inspector.get_table_names()
                return render_template('index.html', tables=table_names, current_db=database, **common_ctx)
            except SQLAlchemyError as e:
                logger.error(f"Ошибка при подключении к базе данных: {str(e)}")
                return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>')
    def view_table(table_name):
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            # Получаем информацию о колонках
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            # Получаем данные из таблицы
            with engine.connect() as connection:
                query = text(f"SELECT * FROM \"{table_name}\" LIMIT 100")
                result = connection.execute(query)
                try:
                    rows = list(result.mappings())
                except AttributeError:
                    try:
                        rows = [dict(row) for row in result]
                    except TypeError:
                        rows = list(result)
            all_tables = inspector.get_table_names()
            current_index = all_tables.index(table_name)
            prev_table = all_tables[current_index - 1] if current_index > 0 else None
            next_table = all_tables[current_index + 1] if current_index < len(all_tables) - 1 else None
            return render_template(
                'table.html', 
                table_name=table_name,
                columns=column_names,
                rows=rows,
                all_tables=all_tables,
                prev_table=prev_table,
                next_table=next_table,
                card_name=card,
                **common_ctx
            )
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при работе с таблицей {table_name}: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>/edit/<int:row_id>', methods=['GET', 'POST'])
    def edit_row(table_name, row_id):
        card_name = request.args.get('card') or card
        try:
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
            if not pk_columns:
                abort(400, f"Таблица {table_name} не имеет первичного ключа")
            primary_key = pk_columns[0]
            if request.method == 'POST':
                data = {col['name']: request.form.get(col['name']) for col in columns}
                update_parts = [f"\"{col}\" = :{col}" for col in data.keys()]
                update_sql = f"UPDATE \"{table_name}\" SET {', '.join(update_parts)} WHERE \"{primary_key}\" = :row_id"
                with engine.begin() as connection:
                    connection.execute(text(update_sql), {**data, 'row_id': row_id})
                flash('Запись успешно обновлена', 'success')
                return redirect(url_for('view_table', table_name=table_name, card=card_name))
            with engine.connect() as connection:
                query = text(f"SELECT * FROM \"{table_name}\" WHERE \"{primary_key}\" = :row_id")
                result = connection.execute(query, {'row_id': row_id})
                row_result = result.fetchone()
                try:
                    row = row_result._asdict()
                except AttributeError:
                    try:
                        row = dict(row_result)
                    except TypeError:
                        row = row_result
            return render_template('edit_row.html', table_name=table_name, row=row, columns=columns, card_name=card_name, **common_ctx)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при редактировании строки: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>/add', methods=['GET', 'POST'])
    def add_row(table_name):
        card_name = request.args.get('card') or card
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            if request.method == 'POST':
                data = {}
                for col in columns:
                    value = request.form.get(col['name'])
                    if value or not col.get('nullable', True):
                        data[col['name']] = value
                columns_str = ', '.join([f"\"{col}\"" for col in data.keys()])
                values_str = ', '.join([f":{col}" for col in data.keys()])
                insert_sql = f"INSERT INTO \"{table_name}\" ({columns_str}) VALUES ({values_str})"
                with engine.begin() as connection:
                    connection.execute(text(insert_sql), data)
                flash('Запись успешно добавлена', 'success')
                return redirect(url_for('view_table', table_name=table_name, card=card_name))
            return render_template('add_row.html', table_name=table_name, columns=columns, card_name=card_name, **common_ctx)
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении строки: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>/delete/<int:row_id>', methods=['POST'])
    def delete_row(table_name, row_id):
        """Удалить строку из таблицы"""
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            
            # Получаем информацию о первичном ключе
            pk_columns = inspector.get_pk_constraint(table_name)['constrained_columns']
            
            if not pk_columns:
                abort(400, f"Таблица {table_name} не имеет первичного ключа")
            
            primary_key = pk_columns[0]
            
            # Выполняем запрос на удаление
            with engine.begin() as connection:
                delete_sql = f"DELETE FROM \"{table_name}\" WHERE \"{primary_key}\" = :row_id"
                connection.execute(text(delete_sql), {'row_id': row_id})
            
            flash('Запись успешно удалена', 'success')
            return redirect(url_for('view_table', table_name=table_name))
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при удалении строки: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>/structure')
    def table_structure(table_name):
        card_name = request.args.get('card') or card
        try:
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            columns = inspector.get_columns(table_name)
            pk_constraint = inspector.get_pk_constraint(table_name)
            pk_columns = pk_constraint['constrained_columns'] if pk_constraint else []
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            return render_template(
                'structure.html',
                table_name=table_name,
                columns=columns,
                pk_columns=pk_columns,
                foreign_keys=foreign_keys,
                indexes=indexes,
                card_name=card_name,
                **common_ctx
            )
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при получении структуры таблицы: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/table/<table_name>/add_column', methods=['GET', 'POST'])
    def add_column(table_name):
        """Добавить новый столбец в таблицу"""
        try:
            # Проверяем, что таблица существует
            if table_name not in inspector.get_table_names():
                abort(404, f"Таблица {table_name} не найдена")
            
            if request.method == 'POST':
                column_name = request.form.get('column_name')
                column_type = request.form.get('column_type')
                nullable = request.form.get('nullable') == 'on'
                default = request.form.get('default')
                
                # Формируем SQL запрос для добавления столбца
                nullable_str = "NULL" if nullable else "NOT NULL"
                default_str = f"DEFAULT {default}" if default else ""
                
                alter_sql = f"ALTER TABLE \"{table_name}\" ADD COLUMN \"{column_name}\" {column_type} {nullable_str} {default_str}"
                
                # Выполняем запрос
                with engine.begin() as connection:
                    connection.execute(text(alter_sql))
                
                flash('Столбец успешно добавлен', 'success')
                return redirect(url_for('table_structure', table_name=table_name))
            
            return render_template('add_column.html', table_name=table_name, **common_ctx)
        
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при добавлении столбца: {str(e)}")
            return render_template('error.html', error=str(e), **common_ctx)
    
    @app.route('/delete_card', methods=['POST'])
    def delete_card():
        card_name = request.args.get('card') or request.form.get('card') or card
        card_key = request.form.get('card_key')
        # Определяем основную таблицу и основной столбец
        card_template = load_card_template(card_name)
        used_tables = []
        for fig in card_template:
            db_col = fig.get('db_column')
            db_table = fig.get('db_table')
            if db_col and db_table and db_col not in (None, '', 'None') and db_table not in (None, '', 'None'):
                if db_table not in used_tables:
                    used_tables.append(db_table)
        if not used_tables:
            return render_template('error.html', error='Не удалось определить основную таблицу для удаления.', **common_ctx)
        main_table = used_tables[0]
        # Определяем основной столбец (первый столбец основной таблицы)
        columns = inspector.get_columns(main_table)
        key_col = columns[0]['name']
        # Удаляем сначала из зависимых таблиц (по foreign key), потом из основной
        with engine.begin() as connection:
            # Удаляем из зависимых таблиц
            for t in inspector.get_table_names():
                if t == main_table:
                    continue
                fks = inspector.get_foreign_keys(t)
                for fk in fks:
                    if fk['referred_table'] == main_table:
                        fk_col = fk['constrained_columns'][0]
                        del_sql = f"DELETE FROM \"{t}\" WHERE \"{fk_col}\" = :key_val"
                        connection.execute(text(del_sql), {'key_val': card_key})
            # Удаляем из основной таблицы
            del_sql = f"DELETE FROM \"{main_table}\" WHERE \"{key_col}\" = :key_val"
            connection.execute(text(del_sql), {'key_val': card_key})
        flash('Карточка и все связанные данные удалены', 'success')
        return redirect(url_for('index', card=card_name))
    
    @app.route('/button_query', methods=['GET', 'POST'])
    def button_query():
        # Получаем индексы карточки и кнопки
        row_idx = int(request.args.get('row', 0))
        fig_idx = int(request.args.get('fig', 0))
        card_template = load_card_template(card)
        table_names = inspector.get_table_names()
        data = []
        if table_names:
            needed = set()
            used_tables = []
            import re
            for fig in card_template:
                db_col = fig.get('db_column')
                db_table = fig.get('db_table')
                if db_col and db_table and db_col not in (None, '', 'None') and db_table not in (None, '', 'None'):
                    needed.add((db_table, db_col))
                    if db_table not in used_tables:
                        used_tables.append(db_table)
                if fig.get('formula'):
                    for m in re.findall(r'\{([\w\.]+)\}', fig['formula']):
                        if '.' in m:
                            t, c = m.split('.', 1)
                            needed.add((t, c))
                            if t not in used_tables:
                                used_tables.append(t)
                        else:
                            for t in table_names:
                                columns = inspector.get_columns(t)
                                if m in [col['name'] for col in columns]:
                                    needed.add((t, m))
                                    if t not in used_tables:
                                        used_tables.append(t)
            # --- Получаем данные ---
            with engine.connect() as connection:
                # Собираем SELECT с нужными JOIN
                main_table = used_tables[0]
                # Формируем alias_map
                alias_map = {main_table: 't0'}
                join_sql = ''
                fks = inspector.get_foreign_keys(main_table)
                for i, fk in enumerate(fks):
                    ref_table = fk['referred_table']
                    alias = f"t{i+1}"
                    alias_map[ref_table] = alias
                    join_sql += f" LEFT JOIN \"{ref_table}\" {alias} ON t0.\"{fk['constrained_columns'][0]}\" = {alias}.\"{fk['referred_columns'][0]}\""
                # SELECT с alias
                select_cols = []
                for t, c in needed:
                    alias = alias_map.get(t, 't0')
                    select_cols.append(f"{alias}.\"{c}\" AS \"{t}.{c}\"")
                sql = f"SELECT {', '.join(select_cols)} FROM \"{main_table}\" t0{join_sql}"
                result = connection.execute(text(sql))
                data = list(result.mappings())
        # --- Находим нужную строку и кнопку ---
        if row_idx >= len(data):
            return '<div class="alert alert-danger">Строка не найдена</div>'
        row = data[row_idx]
        # fig_idx — это индекс фигуры в шаблоне
        if fig_idx >= len(card_template) or card_template[fig_idx].get('type') != 'ButtonFigure':
            return '<div class="alert alert-danger">Кнопка не найдена</div>'
        fig = card_template[fig_idx]
        # --- Получаем параметры кнопки ---
        table = fig.get('table')
        columns = fig.get('columns', [])
        filters = fig.get('filters', [])
        # --- Формируем SQL-запрос ---
        if not table or not columns:
            return '<div class="alert alert-warning">Выберите таблицу и столбцы для запроса.</div>'
        # --- Формируем alias для таблиц ---
        alias_map = {table: 't0'}
        join_sql = ''
        fks = inspector.get_foreign_keys(table)
        for i, fk in enumerate(fks):
            ref_table = fk['referred_table']
            alias = f"t{i+1}"
            alias_map[ref_table] = alias
            join_sql += f" LEFT JOIN \"{ref_table}\" {alias} ON t0.\"{fk['constrained_columns'][0]}\" = {alias}.\"{fk['referred_columns'][0]}\""
        # --- SELECT с универсальными псевдонимами ---
        select_cols = []
        col_labels = []
        for c in columns:
            if isinstance(c, dict):
                col_name = c['column']
                label = c.get('label', c['column'].split('.')[-1])
            else:
                col_name = c
                label = c.split('.')[-1]
            col_labels.append(label)
            if '.' in col_name:
                t, col = col_name.split('.', 1)
                alias = alias_map.get(t, 't0')
                select_cols.append(f"{alias}.\"{col}\" AS \"{t}.{col}\"")
            else:
                select_cols.append(f"t0.\"{col_name}\" AS \"{table}.{col_name}\"")
        sql = f"SELECT {', '.join(select_cols)} FROM \"{table}\" t0{join_sql}"
        where = []
        params = {}
        for i, f in enumerate(filters):
            col_f = f['column'] if isinstance(f['column'], str) else f['column'].get('column', '')
            val = f['value']
            # Подстановка значения из карточки
            if isinstance(val, str) and val.startswith('{') and val.endswith('}'):
                key = val[1:-1]
                val = row.get(key)
            if '.' in col_f:
                t, col = col_f.split('.', 1)
                alias = alias_map.get(t, 't0')
                where.append(f"{alias}.\"{col}\" {f['op']} :val{i}")
            else:
                where.append(f"t0.\"{col_f}\" {f['op']} :val{i}")
            params[f"val{i}"] = val
        if where:
            sql += ' WHERE ' + ' AND '.join(where)
        rows = []
        try:
            with engine.connect() as connection:
                result = connection.execute(text(sql), params)
                rows = list(result.mappings())
        except Exception as e:
            return f"<div class=\"alert alert-danger\">Ошибка SQL: {e}</div>"
        # --- Только таблица результата ---
        if rows:
            html = '<div class="table-responsive mt-3"><table class="table table-bordered table-sm"><thead><tr>'
            for label in col_labels:
                html += f"<th>{label}</th>"
            html += '</tr></thead><tbody>'
            for r in rows:
                html += '<tr>' + ''.join([f"<td>{r[c['column']] if isinstance(c, dict) else r[c]}</td>" for c in columns]) + '</tr>'
            html += '</tbody></table></div>'
        else:
            html = '<div class="alert alert-info mt-3">Нет данных</div>'
        return html
    
    @app.route('/table/<table_name>/import', methods=['GET', 'POST'])
    def import_table(table_name):
        """Импорт данных из CSV/Excel в таблицу"""
        if table_name not in inspector.get_table_names():
            abort(404, f"Таблица {table_name} не найдена")
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        error = None
        if request.method == 'POST':
            file = request.files.get('file')
            if not file:
                error = 'Файл не выбран'
            else:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[-1].lower()
                try:
                    if ext == 'csv':
                        stream = io.StringIO(file.stream.read().decode('utf-8'))
                        reader = csv.DictReader(stream)
                        rows = list(reader)
                    elif ext in ('xls', 'xlsx') and HAS_PANDAS:
                        df = pd.read_excel(file)
                        rows = df.to_dict(orient='records')
                    else:
                        error = 'Поддерживаются только CSV и Excel (xlsx)'
                        rows = []
                    if not error and rows:
                        with engine.begin() as connection:
                            for row in rows:
                                data = {k: row[k] for k in column_names if k in row}
                                if data:
                                    columns_str = ', '.join([f'"{k}"' for k in data.keys()])
                                    values_str = ', '.join([f':{k}' for k in data.keys()])
                                    sql = f'INSERT INTO "{table_name}" ({columns_str}) VALUES ({values_str})'
                                    connection.execute(text(sql), data)
                        flash('Данные успешно импортированы', 'success')
                        return redirect(url_for('view_table', table_name=table_name))
                except Exception as e:
                    error = f'Ошибка импорта: {e}'
        return render_template('import_table.html', table_name=table_name, columns=column_names, error=error, **common_ctx)
    
    @app.route('/table/<table_name>/export')
    def export_table(table_name):
        """Экспорт данных таблицы в CSV или Excel"""
        if table_name not in inspector.get_table_names():
            abort(404, f"Таблица {table_name} не найдена")
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        fmt = request.args.get('format', 'csv')
        
        with engine.connect() as connection:
            query = text(f'SELECT * FROM "{table_name}"')
            result = connection.execute(query)
            rows = list(result.mappings())
            
        if fmt == 'xlsx' and HAS_PANDAS:
            df = pd.DataFrame(rows, columns=column_names)
            # Используем временный файл для сохранения Excel
            import tempfile
            import os
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
                temp_filepath = tmp_file.name
                with pd.ExcelWriter(temp_filepath, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
            
            # Отправляем файл и затем удаляем его
            response = send_from_directory(directory=os.path.dirname(temp_filepath), path=os.path.basename(temp_filepath), as_attachment=True, download_name=f'{table_name}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            @response.call_on_close
            def cleanup():
                os.remove(temp_filepath)
            return response
            
        elif fmt == 'csv':
            # Используем StringIO для текстовых данных
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=column_names)
            writer.writeheader()
            for row in rows:
                # Убедимся, что все значения - строки для записи в CSV
                writer.writerow({k: str(row[k]) if row[k] is not None else '' for k in column_names})
            
            # Получаем текстовое содержимое, затем кодируем его в байты
            csv_output = output.getvalue().encode('utf-8')

            return app.response_class(
                csv_output, # Отправляем байты
                mimetype='text/csv', 
                headers={
                    'Content-Disposition': f'attachment; filename={table_name}.csv'
                },
                # Указываем кодировку явно для клиента
                content_type='text/csv; charset=utf-8'
            )
        else:
            abort(400, "Неподдерживаемый формат экспорта. Используйте 'csv' или 'xlsx'.")
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Обработчик ошибки 404"""
        return render_template('error.html', error=error, **common_ctx), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Обработчик ошибки 500"""
        return render_template('error.html', error=error, **common_ctx), 500
    
    # Запускаем приложение
    logger.info(f"Запуск веб-сервера на порту {web_port}")
    logger.info(f"Подключение к базе данных: {connection_string.replace(password, '****')}")
    
    app.run(host="0.0.0.0", port=web_port, debug=debug)
    
    return app 

def crede():
    """
    Создает папку demo и копирует в нее все файлы из текущей demo:
    product_card.json, example_site.py, import_data.sql, README.md, schema.sql
    """
    import shutil
    import pathlib
    import pkg_resources
    
    # Получаем путь к установленному пакету
    package_path = pathlib.Path(pkg_resources.resource_filename('pgadmin_site', ''))
    src = package_path / 'demo'  # Путь к demo в пакете
    dst = pathlib.Path.cwd() / 'demo'
    
    if not src.exists():
        raise FileNotFoundError(f"Папка demo не найдена в пакете: {src}")
        
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return str(dst)

def create_module_file(modul_command: str):
    """
    Создаёт файл module2.py, module3.py, module4.py или product_app5.py в текущей директории с соответствующим кодом.
    modul_command: строка вида 'modul(2)', 'modul(3)', 'modul(4)', 'modul(5)'
    """
    import pathlib
    import pkg_resources

    mapping = {
        'modul(2)': 'module2.py',
        'modul(3)': 'module3.py',
        'modul(4)': 'module4.py',
        'modul(5)': 'product_app5.py',
    }
    filename = mapping.get(modul_command)
    if not filename:
        raise ValueError("modul_command должен быть 'modul(2)', 'modul(3)', 'modul(4)' или 'product_app5'")
    
    # Получаем путь к установленному пакету
    package_path = pathlib.Path(pkg_resources.resource_filename('pgadmin_site', ''))
    src = package_path / 'modul' / filename  # Путь к файлу в пакете
    dst = pathlib.Path.cwd() / filename
    
    if not src.exists():
        raise FileNotFoundError(f"Файл {src} не найден в пакете.")
        
    with open(src, 'r', encoding='utf-8') as fsrc, open(dst, 'w', encoding='utf-8') as fdst:
        fdst.write(fsrc.read())
    return str(dst)

# --- TKINTER CARD DESIGNER ---
def tkinter_card_designer():
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    import os
    import json

    class CardDesigner(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title("Конструктор карточек PGAdmin Site")
            self.geometry("800x600")
            self.configure(bg="#f8f9fa")
            self.fields = []
            self.card_name = tk.StringVar()
            self.card_fields_frame = tk.Frame(self, bg="#f8f9fa")
            self.card_fields_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            self._draw_ui()

        def _draw_ui(self):
            top = tk.Frame(self, bg="#f8f9fa")
            top.pack(fill=tk.X, padx=20, pady=10)
            tk.Label(top, text="Название шаблона:", bg="#f8f9fa").pack(side=tk.LEFT)
            tk.Entry(top, textvariable=self.card_name, width=30).pack(side=tk.LEFT, padx=5)
            tk.Button(top, text="Добавить поле", command=self.add_field, bg="#67BA80", fg="white").pack(side=tk.LEFT, padx=10)
            tk.Button(top, text="Сохранить шаблон", command=self.save_card, bg="#007bff", fg="white").pack(side=tk.LEFT, padx=10)
            self.fields_container = tk.Frame(self.card_fields_frame, bg="#f8f9fa")
            self.fields_container.pack(fill=tk.BOTH, expand=True)
            self.refresh_fields()

        def add_field(self):
            field = {"label": tk.StringVar(), "type": tk.StringVar(value="text"), "calc": tk.StringVar()}
            self.fields.append(field)
            self.refresh_fields()

        def remove_field(self, idx):
            del self.fields[idx]
            self.refresh_fields()

        def refresh_fields(self):
            for widget in self.fields_container.winfo_children():
                widget.destroy()
            for idx, field in enumerate(self.fields):
                row = tk.Frame(self.fields_container, bg="#f8f9fa")
                row.pack(fill=tk.X, pady=3)
                tk.Label(row, text=f"Поле {idx+1}:", bg="#f8f9fa").pack(side=tk.LEFT)
                tk.Entry(row, textvariable=field["label"], width=20).pack(side=tk.LEFT, padx=5)
                ttk.Combobox(row, textvariable=field["type"], values=["text", "number", "discount_calc"], width=12).pack(side=tk.LEFT, padx=5)
                tk.Entry(row, textvariable=field["calc"], width=30).pack(side=tk.LEFT, padx=5)
                tk.Label(row, text="(формула/выражение, если нужно)", bg="#f8f9fa").pack(side=tk.LEFT, padx=2)
                tk.Button(row, text="Удалить", command=lambda i=idx: self.remove_field(i), bg="#dc3545", fg="white").pack(side=tk.LEFT, padx=5)

        def save_card(self):
            name = self.card_name.get().strip()
            if not name:
                messagebox.showerror("Ошибка", "Введите название шаблона!")
                return
            if not self.fields:
                messagebox.showerror("Ошибка", "Добавьте хотя бы одно поле!")
                return
            card_data = []
            for f in self.fields:
                card_data.append({
                    "label": f["label"].get(),
                    "type": f["type"].get(),
                    "calc": f["calc"].get()
                })
            os.makedirs(os.path.join(os.path.dirname(__file__), "templates", "cards"), exist_ok=True)
            path = os.path.join(os.path.dirname(__file__), "templates", "cards", f"{name}.json")
            with open(path, "w", encoding="utf-8") as fp:
                json.dump(card_data, fp, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", f"Шаблон '{name}' сохранён!")

    CardDesigner().mainloop() 