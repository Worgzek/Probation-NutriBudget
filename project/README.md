# Technical & Infrastructure Documentation: NutriBudget

> An intelligent web application combining optimization algorithms and an AI Agent to suggest meal plans, balance nutrition, and optimize meal costs for students.

---

## 1. Architecture & Tech Stack Overview

- **System Architecture:** Decoupled architecture between the independent Frontend and Backend API. Adopts a **Stateless** model (no user profiles stored in the database to optimize security, protect privacy, and reduce system load).
- **Backend:** Python, FastAPI, Pydantic (strict input data validation).
- **Database:** PostgreSQL 15, supporting advanced indexing (`GIN index`) for food allergy tag arrays.
- **Infrastructure & Containerization:** Docker, Docker Compose managing multi-services (Database & Backend).

---

## 2. Project Directory Structure

project/
├── backend/
│   ├── app/
│   │   ├── main.py        # FastAPI initialization, CORS, Health check endpoints
│   │   └── schemas.py     # Pydantic models definition (Stateless payload)
│   └── requirements.txt   # Dependencies list
├── database/
│   └── schema.sql         # Initialization script for foods and request_logs tables
├── frontend/              # Frontend source code directory (HTML/JS)
├── .env                   # Secure environment variables (Database credentials)
├── .gitignore             # Ignored files and folders for Git
└── docker-compose.yaml    # Container orchestration (db, backend)
└── Dockerfile             # Python/FastAPI environment containerization

---

## 3. Database Schema (Stateless)

The entire database structure is initialized automatically via the `database/schema.sql` file:

    -- 1. Foods table - Input for the optimize_meal_plan() algorithm
    CREATE TABLE IF NOT EXISTS foods (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        category VARCHAR(50) NOT NULL
            CHECK (category IN ('protein', 'carb', 'vegetable', 'fruit', 'dairy', 'fat', 'other')),
        price_per_unit DECIMAL(10,2) NOT NULL CHECK (price_per_unit >= 0),
        unit VARCHAR(50) NOT NULL DEFAULT '100g',
        calories DECIMAL(6,2) NOT NULL CHECK (calories >= 0),
        protein DECIMAL(6,2) NOT NULL CHECK (protein >= 0),
        carbs DECIMAL(6,2) NOT NULL CHECK (carbs >= 0),
        fat DECIMAL(6,2) NOT NULL CHECK (fat >= 0),
        allergen_tags TEXT[] NOT NULL DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Optimized lookup indexing
    CREATE INDEX IF NOT EXISTS idx_foods_allergen_tags ON foods USING GIN (allergen_tags);
    CREATE INDEX IF NOT EXISTS idx_foods_category ON foods (category);

    -- 2. Request logs table
    CREATE TABLE IF NOT EXISTS request_logs (
        id SERIAL PRIMARY KEY,
        endpoint VARCHAR(100) NOT NULL,       -- 'nutrition/macros' or 'meal-plan'
        request_payload JSONB NOT NULL,
        response_payload JSONB NOT NULL,
        feasible BOOLEAN,                      -- null for macros endpoint, true/false for meal-plan
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_logs_endpoint ON request_logs (endpoint);
    CREATE INDEX IF NOT EXISTS idx_logs_created_at ON request_logs (created_at);

---

## 4. Pydantic Schemas (backend/app/schemas.py)

Data structure used to validate incoming payloads according to the stateless model:

    from pydantic import BaseModel, Field
    from typing import List
    from datetime import datetime

    class UserProfilePayload(BaseModel):
        age: int = Field(..., gt=0, description="User age")
        weight: float = Field(..., gt=0, description="Weight in kg")
        height: float = Field(..., gt=0, description="Height in cm")
        gender: str = Field(..., description="Gender: 'male' or 'female'")
        activity_level: str = Field(..., description="Activity level")
        goal: str = Field(..., description="Goal: lose_weight, maintain, gain_muscle")
        budget_limit: float = Field(..., ge=0, description="Maximum budget (VND)")
        allergies: List[str] = Field(default=[], description="List of allergies to exclude")

    class MealPlanRequest(BaseModel):
        profile: UserProfilePayload
        target_meals_count: int = Field(default=3, description="Number of meals per day")

    class FoodCreate(BaseModel):
        name: str
        category: str
        price_per_unit: float
        unit: str = "100g"
        calories: float
        protein: float
        carbs: float
        fat: float
        allergen_tags: List[str] = []

    class FoodResponse(FoodCreate):
        id: int
        created_at: datetime

        class Config:
            from_attributes = True

---

## 5. Logic Separation & AI Agent

- **Core Logic (Deterministic Code):** Basic biometric indices like BMR, TDEE, and macro targets are calculated with absolute precision using pure Python mathematical functions, ensuring ultra-fast response times and zero computational error.
- **AI Agent (Gemini API):** Takes charge of advanced optimization in the `optimize_meal_plan()` step, performing natural semantic analysis, flexible allergy filtering, and combining food items to precisely match a student's budget.

---

## 6. Quick Start Guide

1. Configure environment variables (`.env`):
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=nutribudget

2. Start the system using Docker Compose:
   docker compose up --build

3. Verify operation status:
   - FastAPI Root: http://localhost:8000/
   - Check Database Connection: http://localhost:8000/health/db
