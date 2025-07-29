-- Схема БД для мебельной компании (3НФ)
-- Таблица: Цехи
CREATE TABLE workshop (
    workshop_id SERIAL PRIMARY KEY, -- Уникальный идентификатор цеха
    name VARCHAR(100) NOT NULL,    -- Название цеха
    location VARCHAR(100)          -- Местоположение
);

-- Таблица: Продукция
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY, -- Уникальный идентификатор продукции
    name VARCHAR(100) NOT NULL,    -- Название продукции
    model_type VARCHAR(50),        -- Тип модели (современная/классическая)
    sku VARCHAR(50),               -- Артикул
    min_price NUMERIC(10,2),       -- Минимальная стоимость для партнера
    material VARCHAR(100),         -- Материал
    workshop_id INTEGER NOT NULL,  -- Внешний ключ на цех
    production_time INTEGER,       -- Время изготовления (часы)
    FOREIGN KEY (workshop_id) REFERENCES workshop(workshop_id) ON DELETE CASCADE
);

-- Таблица: Этапы изготовления (каждая продукция проходит через этапы в цехах)
CREATE TABLE production_stage (
    stage_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    workshop_id INTEGER NOT NULL,
    stage_name VARCHAR(100),
    stage_time INTEGER NOT NULL, -- Время на этапе (часы)
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE,
    FOREIGN KEY (workshop_id) REFERENCES workshop(workshop_id) ON DELETE CASCADE
);

-- Таблица: Материалы (опционально)
CREATE TABLE material (
    material_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    eco_friendly BOOLEAN DEFAULT TRUE
);

-- Таблица: Использование материалов в продукции (опционально)
CREATE TABLE product_material (
    product_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity NUMERIC(10,2),
    PRIMARY KEY (product_id, material_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES material(material_id) ON DELETE CASCADE
); 