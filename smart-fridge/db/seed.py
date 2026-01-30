from __future__ import annotations

from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parents[1]))

from lib import db


ITEMS = [
    {"name": "鸡蛋", "category": "protein", "default_unit": "pcs", "shelf_life_days_default": 10},
    {"name": "牛奶", "category": "dairy", "default_unit": "ml", "shelf_life_days_default": 7},
    {"name": "鸡胸", "category": "protein", "default_unit": "g", "shelf_life_days_default": 4},
    {"name": "番茄", "category": "vegetable", "default_unit": "pcs", "shelf_life_days_default": 5},
    {"name": "蘑菇", "category": "vegetable", "default_unit": "g", "shelf_life_days_default": 4},
    {"name": "洋葱", "category": "vegetable", "default_unit": "pcs", "shelf_life_days_default": 10},
    {"name": "大米", "category": "staple", "default_unit": "g", "shelf_life_days_default": 180},
    {"name": "面条", "category": "staple", "default_unit": "g", "shelf_life_days_default": 120},
    {"name": "土豆", "category": "vegetable", "default_unit": "pcs", "shelf_life_days_default": 20},
    {"name": "胡萝卜", "category": "vegetable", "default_unit": "pcs", "shelf_life_days_default": 14},
    {"name": "生菜", "category": "vegetable", "default_unit": "g", "shelf_life_days_default": 5},
    {"name": "酸奶", "category": "dairy", "default_unit": "ml", "shelf_life_days_default": 7},
]

RECIPES = [
    {"name": "蛋炒饭", "tags": "rice,quick", "allergens": "egg", "steps": "炒蛋后下饭翻炒", "nutrition": {"calories": 520}},
    {"name": "番茄炒蛋", "tags": "egg", "allergens": "egg", "steps": "番茄炒软后下蛋", "nutrition": {"calories": 320}},
    {"name": "鸡胸沙拉", "tags": "salad,protein", "allergens": "", "steps": "鸡胸煎熟切片拌生菜", "nutrition": {"calories": 280}},
    {"name": "蘑菇汤", "tags": "soup", "allergens": "", "steps": "蘑菇洋葱炒香加水煮", "nutrition": {"calories": 180}},
    {"name": "洋葱土豆炖鸡", "tags": "stew", "allergens": "", "steps": "鸡胸与洋葱土豆炖煮", "nutrition": {"calories": 450}},
    {"name": "牛奶燕麦", "tags": "breakfast", "allergens": "dairy", "steps": "牛奶加热与燕麦同煮", "nutrition": {"calories": 300}},
    {"name": "炒面", "tags": "noodle", "allergens": "", "steps": "面条煮熟后与蔬菜翻炒", "nutrition": {"calories": 480}},
    {"name": "蔬菜沙拉", "tags": "salad", "allergens": "", "steps": "生菜番茄胡萝卜拌匀", "nutrition": {"calories": 200}},
]

RECIPE_INGREDIENTS = {
    "蛋炒饭": [
        ("鸡蛋", 2, "pcs"),
        ("大米", 150, "g"),
        ("洋葱", 0.5, "pcs"),
    ],
    "番茄炒蛋": [
        ("鸡蛋", 2, "pcs"),
        ("番茄", 2, "pcs"),
        ("洋葱", 0.5, "pcs"),
    ],
    "鸡胸沙拉": [
        ("鸡胸", 200, "g"),
        ("生菜", 120, "g"),
        ("番茄", 1, "pcs"),
    ],
    "蘑菇汤": [
        ("蘑菇", 150, "g"),
        ("洋葱", 1, "pcs"),
        ("牛奶", 200, "ml"),
    ],
    "洋葱土豆炖鸡": [
        ("鸡胸", 200, "g"),
        ("土豆", 2, "pcs"),
        ("洋葱", 1, "pcs"),
    ],
    "牛奶燕麦": [
        ("牛奶", 250, "ml"),
        ("酸奶", 150, "ml"),
    ],
    "炒面": [
        ("面条", 200, "g"),
        ("胡萝卜", 1, "pcs"),
        ("洋葱", 0.5, "pcs"),
    ],
    "蔬菜沙拉": [
        ("生菜", 150, "g"),
        ("番茄", 1, "pcs"),
        ("胡萝卜", 1, "pcs"),
    ],
}


def seed() -> None:
    db.init_db()
    if db.count_rows("items") == 0:
        db.insert_items(ITEMS)

    if db.count_rows("recipes") == 0:
        db.insert_recipes(RECIPES)

    items = {item["name"]: item for item in db.list_items()}
    recipes = {recipe["name"]: recipe for recipe in db.list_recipes()}

    if db.count_rows("recipe_ingredients") == 0:
        ingredients = []
        for recipe_name, ings in RECIPE_INGREDIENTS.items():
            recipe_id = recipes[recipe_name]["recipe_id"]
            for item_name, qty, unit in ings:
                ingredients.append(
                    {
                        "recipe_id": recipe_id,
                        "item_id": items[item_name]["item_id"],
                        "quantity": qty,
                        "unit": unit,
                    }
                )
        db.insert_recipe_ingredients(ingredients)


if __name__ == "__main__":
    seed()
    print("Seed completed")
