from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
 
from app.schemas import MealPlanRequest, MealPlanResponse, NutritionRequest, NutritionResponse
from app.nutrition.calculator import calculate_nutrition
from app.planner.optimizer import optimize_meal_plan

 
import os
import psycopg2

from app.query import get_food_db
 
app = FastAPI(
    title="NutriBudget API",
    description="API cho NutriBudget - tính macro và gợi ý thực đơn theo ngân sách",
    version="1.0.0",
)
 
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
DATABASE_URL = os.getenv("DATABASE_URL")
 
 
@app.get("/health")
def health():
    """Healthcheck Docker"""
    return {"status": "ok"}
 
 
@app.get("/health/db")
def check_db_connection():
    """Healthcheck DB """
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        cursor.close()
        connection.close()
        return {"status": "success", "database_version": db_version[0]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")
 
 
@app.post("/api/v1/nutrition/macros", response_model=NutritionResponse)
def get_nutrition_macros(payload: NutritionRequest):
    try:
        result = calculate_nutrition(
        weight_kg=payload.weight_kg,
        height_cm=payload.height_cm,
        age=payload.age,
        gender=payload.gender,
        activity_level=payload.activity_level,
        goal=payload.goal,
    )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
 
    return NutritionResponse(
        calories=result["calories"],
        protein_g=result["protein_g"],
        fat_g=result["fat_g"],
        carb_g=result["carb_g"],
        explanation=(
            "Đây là kết quả ước tính dựa trên công thức "
            "Mifflin-St Jeor và phân bổ macro theo mục tiêu. "
            "Bản MVP hiện chưa sử dụng LLM."
        ),
        warning=result["warnings"],
    )

@app.post(
    "/api/v1/meal-plan",
    response_model=MealPlanResponse
)
def create_meal_plan(payload: MealPlanRequest):
    try:
        food_db = get_food_db()

        result = optimize_meal_plan(
            macro_targets=payload.macro_targets.model_dump(),
            budget=payload.budget.model_dump(),
            food_db=food_db,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Meal plan generation failed: {str(e)}"
        )