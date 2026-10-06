import os
import psycopg2
from psycopg2.extras import RealDictCursor


def get_food_db() -> list[dict]:
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is not configured")

    connection = psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    name,
                    category,
                    price_per_unit,
                    unit,
                    calories,
                    protein,
                    carbs,
                    fat,
                    allergen_tags
                FROM foods
                ORDER BY id;
            """)

            rows = cursor.fetchall()

            return [
                {
                    "name": row["name"],
                    "category": row["category"],
                    "price_per_unit": float(row["price_per_unit"]),
                    "unit": row["unit"],
                    "calories": float(row["calories"]),
                    "protein": float(row["protein"]),
                    "carbs": float(row["carbs"]),
                    "fat": float(row["fat"]),
                    "allergen_tags": row["allergen_tags"] or [],
                }
                for row in rows
            ]

    finally:
        connection.close()