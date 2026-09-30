from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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

# Lấy chuỗi kết nối từ biến môi trường (Docker compose đã truyền vào)
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
