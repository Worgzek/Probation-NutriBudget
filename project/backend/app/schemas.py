from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


#NUTRITION AGENT — POST /api/v1/nutrition/macros

ActivityLevel = Literal["sedentary", "light", "moderate", "heavy"]
Goal = Literal["weight_loss", "maintain", "muscle_gain"]
Gender = Literal["male", "female"]


class NutritionRequest(BaseModel):
    height_cm: float = Field(..., gt=0, le=250, description="chieu cao (cm)")
    weight_kg: float = Field(..., gt=0, le=300, description="can nang (kg)")
    age: int = Field(..., gt=0, le=120, description="tuoi")
    gender: Gender
    activity_level: ActivityLevel
    goal: Goal
    notes: Optional[str] = Field(
        None, max_length=200,
        description="ghi chu tu do, vd: tinh trang van dong can luu y"
    )


class NutritionResponse(BaseModel):
    calories: float
    protein_g: float
    fat_g: float
    carb_g: float
    explanation: str = Field(..., description="LLM giai thich vi sao macro nay phu hop")
    warning: Optional[str] = Field(
        None, description="canh bao neu phat hien bat thuong (vd: BMI thap + muc tieu giam can)"
    )


#2. MEAL PLANNING AGENT — POST /api/v1/meal-plan

class MacroTargets(BaseModel):
    """Dùng lại nguyên response của bước 1 - frontend gửi lại, không tính lại ở backend."""
    calories: float
    protein_g: float
    fat_g: float
    carb_g: float


BudgetPeriod = Literal["weekly", "monthly"]


class Budget(BaseModel):
    amount: float = Field(..., ge=0)
    period: BudgetPeriod


class MealPlanRequest(BaseModel):
    macro_targets: MacroTargets
    budget: Budget
    notes: Optional[str] = Field(
        None, max_length=200,
        description="di ung + so thich, vd: 'di ung hai san, uu tien mon chay'. "
                    "LLM tu trich xuat nhom di ung chuan tu day, KHONG co field allergies rieng."
    )


class Ingredient(BaseModel):
    name: str
    amount_g: float = Field(..., ge=0)
    cost: float = Field(..., ge=0)


class Meal(BaseModel):
    meal_name: str
    ingredients: List[Ingredient]
    macros: MacroTargets
    meal_cost: float = Field(..., ge=0)


class MealPlanResponse(BaseModel):
    feasible: bool
    meals: List[Meal] = Field(default_factory=list)
    total_cost_estimate: Optional[float] = None
    message: Optional[str] = Field(
        None, description="Bat buoc co khi feasible=False, giai thich ly do + huong xu ly"
    )
    suggested_budget: Optional[float] = Field(
        None, description="Chi co khi feasible=False va solver uoc tinh duoc muc budget kha thi"
    )


#3. FOODS

FoodCategory = Literal["protein", "carb", "vegetable", "fruit", "dairy", "fat", "other"]


class FoodCreate(BaseModel):
    name: str
    category: FoodCategory
    price_per_unit: float = Field(..., ge=0)
    unit: str = "100g"
    calories: float = Field(..., ge=0)
    protein: float = Field(..., ge=0)
    carbs: float = Field(..., ge=0)
    fat: float = Field(..., ge=0)
    allergen_tags: List[str] = Field(default_factory=list)


class FoodResponse(FoodCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


#ALLERGENS — GET /api/v1/allergens (danh mục nội bộ để LLM map)

class Allergen(BaseModel):
    key: str
    label: str


#5. REQUEST LOGS

class RequestLogCreate(BaseModel):
    endpoint: Literal["nutrition/macros", "meal-plan"]
    request_payload: dict
    response_payload: dict
    feasible: Optional[bool] = None