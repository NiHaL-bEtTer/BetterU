# main.py
# Load food data, take user input, calculate nutrition targets, suggest foods

import pandas as pd
from calculator import calculate_bmr, calculate_tdee, adjust_calories, calculate_macros

# --- Load USDA food dataset ---
usda_foods = pd.read_csv("data/comprehensive_foods_usda.csv")
usda_foods = usda_foods.fillna(0)  # fill missing nutrition values

# Convert to list of dictionaries for easy querying
food_records = usda_foods.to_dict(orient="records")

# --- Sample user input ---
user = {
    "weight": 70,   # kg
    "height": 175,  # cm
    "age": 18,
    "sex": "male",
    "activity_factor": 1.55,  # moderate
    "goal": "bulk",
    "protein_per_kg": 1.8
}

# --- Calculate nutrition targets ---
bmr = calculate_bmr(user["weight"], user["height"], user["age"], user["sex"])
tdee = calculate_tdee(bmr, user["activity_factor"])
adjusted_calories = adjust_calories(tdee, user["goal"])
macros = calculate_macros(adjusted_calories, user["protein_per_kg"], user["weight"])

print("===== Nutrition Targets =====")
print(f"Calories: {int(adjusted_calories)} kcal")
print(f"Protein: {macros['protein_g']} g")
print(f"Fat: {macros['fat_g']} g")
print(f"Carbs: {macros['carbs_g']} g")

# --- Suggest foods (simple example: high protein) ---
high_protein_foods = [f for f in food_records if f["protein_g"] >= 15]
top5_protein = high_protein_foods[:5]  # pick first 5

print("\n===== High-Protein Foods =====")
for f in top5_protein:
    print(f"{f['food_name']} - Protein: {f['protein_g']}g, Calories: {f['calories']} kcal")