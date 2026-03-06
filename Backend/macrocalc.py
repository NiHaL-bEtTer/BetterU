def calculate_nutrition(weight, height, age, gender, activity_level, goal):

    height_m = height / 100
    bmi = weight / (height_m ** 2)

    if gender.lower() == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }

    tdee = bmr * activity_multipliers[activity_level.lower()]

    if goal.lower() == "fat loss":
        calories = tdee - 500
        protein_per_kg = 2.2
    elif goal.lower() == "muscle gain":
        calories = tdee + 300
        protein_per_kg = 2.0
    else:  # maintain fitness
        calories = tdee
        protein_per_kg = 1.8

    protein = weight * protein_per_kg
    protein_calories = protein * 4

    fat = (calories * 0.25) / 9
    fat_calories = fat * 9

    carbs = (calories - protein_calories - fat_calories) / 4

    return {
        "BMI": round(bmi, 2),
        "BMR": round(bmr, 2),
        "TDEE": round(tdee, 2),
        "Calories": round(calories, 2),
        "Protein (g)": round(protein, 2),
        "Fat (g)": round(fat, 2),
        "Carbs (g)": round(carbs, 2)
    }

