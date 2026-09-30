from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import NutritionRequest, NutritionResponse
from app.nutrition.services import calculate_bmr, calculate_tdee, calculate_macros

import os
import psycopg2

app = FastAPI(
    title="NutriBudget API",
    description="Pờ rô bây sừn",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/nutribudget")

@app.get("/")
def read_root():
    return {
        "project": "NutriBudget API",
        "status": "Success",
        "message": "mmb"
    }

@app.get("/health/db")
def check_db_connection():
    try:
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        cursor.close()
        connection.close()
        return {
            "status": "success",
            "message": "THÔNG",
            "database_version": db_version[0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@app.post("/api/v1/nutrition/macros", response_model=NutritionResponse)
def get_nutrition_macros(payload: NutritionRequest):
    try:
        # 1. BMR
        bmr = calculate_bmr(
            weight_kg=payload.weight_kg,
            height_cm=payload.height_cm,
            age=payload.age,
            gender=payload.gender
        )
        
        # 2. TDEE
        tdee = calculate_tdee(bmr, payload.activity_level)
        
        # 3. Macro
        macros = calculate_macros(
            weight_kg=payload.weight_kg,
            tdee=tdee,
            goal=payload.goal
        )
        
        return NutritionResponse(
            calories=macros["calories"],
            protein_g=macros["protein_g"],
            fat_g=macros["fat_g"],
            carb_g=macros["carb_g"],
            explanation="Đây là kết quả tính toán dựa trên công thức khoa học Mifflin-St Jeor và phân bổ macro tiêu chuẩn cho mục tiêu của bạn. (Bản MVP tạm thời)",
            warning=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed: {str(e)}")