-- Импорт тестовых данных
-- Цехи
INSERT INTO workshop (name, location) VALUES
('Столярный', 'Корпус 1'),
('Сборочный', 'Корпус 2'),
('Отделочный', 'Корпус 3');

-- Продукция
INSERT INTO product (name, model_type, sku, min_price, material, workshop_id, production_time) VALUES
('Стол "Модерн"', 'современная', 'ST-001', 12000, 'Дуб', 1, 12),
('Шкаф "Классика"', 'классическая', 'SH-002', 18500, 'Сосна', 2, 20),
('Кресло "Эко"', 'современная', 'KR-003', 9500, 'Бук', 1, 8);

-- Этапы изготовления
INSERT INTO production_stage (product_id, workshop_id, stage_name, stage_time) VALUES
(1, 1, 'Распиловка', 3),
(1, 2, 'Сборка', 5),
(1, 3, 'Отделка', 4),
(2, 2, 'Сборка', 10),
(2, 3, 'Отделка', 10),
(3, 1, 'Распиловка', 2),
(3, 2, 'Сборка', 3),
(3, 3, 'Отделка', 3);

-- Материалы
INSERT INTO material (name, eco_friendly) VALUES
('Дуб', TRUE),
('Сосна', TRUE),
('Бук', TRUE);

-- Использование материалов
INSERT INTO product_material (product_id, material_id, quantity) VALUES
(1, 1, 5.0),
(2, 2, 8.0),
(3, 3, 3.5); 