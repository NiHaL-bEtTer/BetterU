# calculator.py
# Handles all nutrition calculations

def calculate_bmr(weight, height, age, sex):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    weight in kg, height in cm, age in years, sex 'male'/'female'
    """
    if sex.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    else:
        return 10 * weight + 6.25 * height - 5 * age - 161

def calculate_tdee(bmr, activity_factor):
    """
    Total Daily Energy Expenditure
    activity_factor: sedentary=1.2, light=1.375, moderate=1.55, active=1.725, very_active=1.9
    """
    return bmr * activity_factor

def adjust_calories(tdee, goal):
    """
    Adjust calories based on goal: bulk/cut/maintain
    """
    if goal.lower() == "bulk":
        return tdee + 400  # +300-500 kcal typical
    elif goal.lower() == "cut":
        return tdee - 400
    else:
        return tdee  # maintain

def calculate_macros(calories, protein_per_kg, weight):
    """
    Calculate protein, fat, carb grams based on total calories and protein/kg
    """
    protein_grams = protein_per_kg * weight
    protein_calories = protein_grams * 4
    fat_calories = calories * 0.25  # 25% calories from fat
    fat_grams = fat_calories / 9
    carb_calories = calories - (protein_calories + fat_calories)
    carb_grams = carb_calories / 4
    return {
        "protein_g": round(protein_grams, 1),
        "fat_g": round(fat_grams, 1),
        "carbs_g": round(carb_grams, 1)
    }