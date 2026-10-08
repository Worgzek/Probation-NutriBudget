-- seed_foods.sql
-- Dữ liệu mẫu để test optimize_meal_plan() trước khi J4 soạn đủ food_db.csv (40 dòng).
-- Dinh dưỡng tính trên 100g (unit mặc định). Giá là ước tính chợ/siêu thị VN, làm tròn.
-- Phủ đủ 7 category và 4 nhóm dị ứng (seafood, dairy, egg, peanut, gluten) để test lọc dị ứng.
 
INSERT INTO foods (name, category, price_per_unit, unit, calories, protein, carbs, fat, allergen_tags) VALUES
-- Protein
('Ức gà',        'protein', 4500,  '100g', 165, 31.0, 0.0,  3.6,  '{}'),
('Thịt bò nạc',  'protein', 28000, '100g', 250, 26.0, 0.0,  15.0, '{}'),
('Trứng gà',     'protein', 3500,  '100g', 155, 13.0, 1.1,  11.0, '{egg}'),
('Đậu phụ',      'protein', 1500,  '100g', 76,  8.0,  1.9,  4.8,  '{}'),
('Tôm',          'protein', 22000, '100g', 99,  24.0, 0.2,  0.3,  '{seafood}'),
('Cá hồi',       'protein', 35000, '100g', 208, 20.0, 0.0,  13.0, '{seafood}'),
 
-- Carb
('Gạo trắng',    'carb',    2000,  '100g', 130, 2.7,  28.0, 0.3,  '{}'),
('Khoai lang',   'carb',    1500,  '100g', 86,  1.6,  20.0, 0.1,  '{}'),
('Yến mạch',     'carb',    6000,  '100g', 389, 16.9, 66.0, 6.9,  '{}'),
('Bánh mì',      'carb',    2500,  '100g', 265, 9.0,  49.0, 3.2,  '{gluten}'),
 
-- Vegetable
('Bông cải xanh','vegetable', 3500, '100g', 34,  2.8,  7.0,  0.4,  '{}'),
('Rau cải bó xôi','vegetable', 2000, '100g', 23,  2.9,  3.6,  0.4,  '{}'),
 
-- Fruit
('Chuối',        'fruit',   2000,  '100g', 89,  1.1,  23.0, 0.3,  '{}'),
 
-- Dairy
('Sữa tươi',     'dairy',   3000,  '100g', 42,  3.4,  5.0,  1.0,  '{dairy}'),
('Sữa chua',     'dairy',   2500,  '100g', 61,  3.5,  4.7,  3.3,  '{dairy}'),
 
-- Fat
('Dầu ô liu',    'fat',     25000, '100g', 884, 0.0,  0.0,  100.0, '{}'),
('Đậu phộng',    'fat',     5000,  '100g', 567, 25.8, 16.0, 49.0, '{peanut}');
 
