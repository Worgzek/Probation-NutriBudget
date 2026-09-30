def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    # Công thức Mifflin-St Jeor
    base = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)
    if gender.lower() == "male":
        return base + 5
    else:
        return base - 161

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "heavy": 1.725
    }
    return bmr * multipliers.get(activity_level, 1.2)

def calculate_macros(weight_kg: float, tdee: float, goal: str):

    if goal == "weight_loss":
        target_calories = tdee - 500
    elif goal == "muscle_gain":
        target_calories = tdee + 300
    else:
        target_calories = tdee

    # Phân bổ Macro cơ bản: Protein (2.0g/kg), Fat (25% tổng calo), phần còn lại là Carb
    protein_g = weight_kg * 2.0
    fat_g = (target_calories * 0.25) / 9.0
    carb_g = (target_calories - (protein_g * 4 + fat_g * 9)) / 4.0

    return {
        "calories": round(target_calories, 2),
        "protein_g": round(protein_g, 2),
        "fat_g": round(fat_g, 2),
        "carb_g": round(carb_g, 2)
    }

