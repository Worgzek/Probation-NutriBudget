-- 1. User Profiles
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    weight DECIMAL(5,2) NOT NULL, -- cân nặng tính bằng kg
    height DECIMAL(5,2) NOT NULL, -- chiều cao tính bằng cm
    activity_level VARCHAR(50) NOT NULL, -- mức độ vận động (sedentary, light, moderate, active,...)
    target VARCHAR(50) NOT NULL, -- mục tiêu (lose_weight, maintain, gain_muscle)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Foods
CREATE TABLE IF NOT EXISTS foods (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100), -- phân loại (cơm, thịt, rau, trái cây,...)
    price_per_unit DECIMAL(10,2) NOT NULL, -- giá tiền (VNĐ) trên mỗi đơn vị chuẩn (ví dụ: 100g hoặc 1 phần)
    unit VARCHAR(50) DEFAULT '100g', -- đơn vị tính
    calories DECIMAL(6,2) NOT NULL, -- lượng calo (kcal)
    protein DECIMAL(6,2) NOT NULL, -- gram protein
    carbs DECIMAL(6,2) NOT NULL, -- gram carbohydrate
    fat DECIMAL(6,2) NOT NULL, -- gram chất béo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Meal Plans
CREATE TABLE IF NOT EXISTS meal_plans (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    total_cost DECIMAL(10,2) NOT NULL, -- tổng chi phí dự kiến cho thực đơn
    total_calories DECIMAL(6,2) NOT NULL, -- tổng calo đạt được
    plan_details JSONB NOT NULL, -- lưu chi tiết thực đơn các bữa sáng, trưa, tối dưới dạng JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
