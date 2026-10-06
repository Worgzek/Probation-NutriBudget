"""
app/meal_planning/optimizer.py
 
Tool thuần cho Meal Planning Agent - KHÔNG dùng LLM.
Bài toán "Diet Problem" kinh điển, giải bằng linear programming (PuLP).
 
Spec đã chốt:
- Solver tính cho 1 NGÀY, budget (tuần/tháng) quy đổi về budget/ngày trước khi đưa vào
- Giới hạn tối đa 400g/ngày cho mỗi loại thực phẩm (4 đơn vị x 100g)
- Calories trong khoảng ±10% target; protein/fat/carb là ràng buộc >= target
- Kết quả 1 ngày chia 3 bữa theo tỷ lệ cố định: sáng 25% / trưa 40% / tối 35%
- food_db truyền vào đã được lọc dị ứng từ trước (không lọc ở đây)
"""
 
import pulp
 
 
PERIOD_DAYS = {"weekly": 7, "monthly": 30}
MAX_UNITS_PER_FOOD = 4  # 4 x 100g = 400g/ngày/loại
CALORIE_TOLERANCE = 0.10  # +-10% quanh target
 
MEAL_SPLIT = [
    ("Bữa sáng", 0.25),
    ("Bữa trưa", 0.40),
    ("Bữa tối", 0.35),
]
 
 
def _daily_budget(budget: dict) -> float:
    days = PERIOD_DAYS[budget["period"]]
    return budget["amount"] / days
 
 
def _build_and_solve(macro_targets: dict, daily_budget: float, food_db: list,
                      enforce_budget: bool = True):
    """Dựng và giải 1 lần bài toán LP. Trả về (status, x_values dict theo tên food)."""
    prob = pulp.LpProblem("diet_problem", pulp.LpMinimize)
 
    # Biến quyết định: số đơn vị (100g) của mỗi thực phẩm, 0 -> MAX_UNITS_PER_FOOD
    x = {
        food["name"]: pulp.LpVariable(f"x_{i}", lowBound=0, upBound=MAX_UNITS_PER_FOOD)
        for i, food in enumerate(food_db)
    }
 
    # Mục tiêu: tối thiểu hóa tổng chi phí
    prob += pulp.lpSum(food["price_per_unit"] * x[food["name"]] for food in food_db)
 
    # Ràng buộc macro - protein/fat/carb phải đạt ít nhất target
    prob += pulp.lpSum(food["protein"] * x[food["name"]] for food in food_db) >= macro_targets["protein_g"]
    prob += pulp.lpSum(food["fat"] * x[food["name"]] for food in food_db) >= macro_targets["fat_g"]
    prob += pulp.lpSum(food["carbs"] * x[food["name"]] for food in food_db) >= macro_targets["carb_g"]
 
    # Ràng buộc calories - trong khoảng +-10% target
    total_calories = pulp.lpSum(food["calories"] * x[food["name"]] for food in food_db)
    prob += total_calories <= macro_targets["calories"] * (1 + CALORIE_TOLERANCE)
    prob += total_calories >= macro_targets["calories"] * (1 - CALORIE_TOLERANCE)
 
    # Ràng buộc ngân sách - có thể tắt khi cần thử "nếu không giới hạn budget thì tốn tối thiểu bao nhiêu"
    if enforce_budget:
        prob += pulp.lpSum(food["price_per_unit"] * x[food["name"]] for food in food_db) <= daily_budget
 
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
 
    status = pulp.LpStatus[prob.status]
    x_values = {name: var.value() for name, var in x.items()}
    total_cost = sum(
        food["price_per_unit"] * (x_values[food["name"]] or 0) for food in food_db
    )
    return status, x_values, total_cost
 
 
def _build_meals(x_values: dict, food_db: list) -> list:
    """Chia kết quả 1 ngày thành 3 bữa theo tỷ lệ cố định."""
    by_name = {food["name"]: food for food in food_db}
    meals = []
    for meal_name, ratio in MEAL_SPLIT:
        ingredients = []
        meal_calories = meal_protein = meal_fat = meal_carb = meal_cost = 0.0
        for name, units in x_values.items():
            if not units or units < 0.01:
                continue
            food = by_name[name]
            amount_g = units * 100 * ratio
            if amount_g < 1:  # bỏ qua lượng quá nhỏ, không đáng ghi vào thực đơn
                continue
            cost = food["price_per_unit"] * units * ratio
            ingredients.append({
                "name": name,
                "amount_g": round(amount_g, 1),
                "cost": round(cost, 0),
            })
            factor = (amount_g / 100)
            meal_calories += food["calories"] * factor
            meal_protein += food["protein"] * factor
            meal_fat += food["fat"] * factor
            meal_carb += food["carbs"] * factor
            meal_cost += cost
 
        meals.append({
            "meal_name": meal_name,
            "ingredients": ingredients,
            "macros": {
                "calories": round(meal_calories, 1),
                "protein_g": round(meal_protein, 1),
                "fat_g": round(meal_fat, 1),
                "carb_g": round(meal_carb, 1),
            },
            "meal_cost": round(meal_cost, 0),
        })
    return meals
 
 
def optimize_meal_plan(macro_targets: dict, budget: dict, food_db: list) -> dict:
    """
    macro_targets: {"calories", "protein_g", "fat_g", "carb_g"} - target NGÀY (từ Agent 1)
    budget: {"amount", "period"} - "weekly" | "monthly"
    food_db: list các dict {"name","category","price_per_unit","calories","protein","carbs","fat",...}
             ĐÃ lọc dị ứng từ trước khi gọi hàm này.
 
    Trả về dict khớp MealPlanResponse (feasible, meals, total_cost_estimate, message, suggested_budget).
    """
    daily_budget = _daily_budget(budget)
    days = PERIOD_DAYS[budget["period"]]
 
    status, x_values, daily_cost = _build_and_solve(macro_targets, daily_budget, food_db, enforce_budget=True)
 
    if status == "Optimal":
        meals = _build_meals(x_values, food_db)
        return {
            "feasible": True,
            "meals": meals,
            "total_cost_estimate": round(daily_cost * days, 0),
            "message": None,
            "suggested_budget": None,
        }
 
    # Infeasible - thử lại KHÔNG giới hạn budget, để phân biệt 2 loại nguyên nhân:
    # (a) budget quá thấp so với macro target -> có nghiệm khi bỏ ràng buộc budget
    # (b) macro target không thể đạt được dù food_db/giới hạn 400g có rộng rãi thế nào
    status_relaxed, x_relaxed, min_cost = _build_and_solve(
        macro_targets, daily_budget, food_db, enforce_budget=False
    )
 
    if status_relaxed == "Optimal":
        suggested_daily_budget = min_cost
        return {
            "feasible": False,
            "meals": [],
            "total_cost_estimate": None,
            "message": (
                f"Với ngân sách hiện tại, chưa đủ để đạt chỉ tiêu dinh dưỡng đã đề ra. "
                f"Cần tối thiểu khoảng {round(suggested_daily_budget * days):,.0f}đ/{('tuần' if budget['period']=='weekly' else 'tháng')} "
                f"để đạt đủ macro trong ngân sách. Bạn muốn tăng ngân sách hay điều chỉnh lại mục tiêu?"
            ),
            "suggested_budget": round(suggested_daily_budget * days, 0),
        }
 
    # Vô nghiệm ngay cả khi không giới hạn budget - vấn đề nằm ở macro target hoặc food_db,
    # không phải ở tiền. Không đưa suggested_budget vì tăng tiền cũng không giải quyết được.
    return {
        "feasible": False,
        "meals": [],
        "total_cost_estimate": None,
        "message": (
            "Không tìm được thực đơn đạt đủ chỉ tiêu dinh dưỡng với danh sách thực phẩm hiện có, "
            "dù ngân sách là bao nhiêu. Có thể do mục tiêu dinh dưỡng quá cao so với giới hạn khẩu phần "
            "mỗi loại thực phẩm, hoặc danh sách thực phẩm chưa đủ đa dạng."
        ),
        "suggested_budget": None,
    }
 