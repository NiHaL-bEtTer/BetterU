"""
calculator.py
-------------
Pure deterministic nutrition calculator.
No AI, no external dependencies — standard Python only.

Formulas used: Mifflin-St Jeor
"""


def calculate_bmi(weight, height_cm):
    """
    Calculate Body Mass Index.

    Args:
        weight    (float): body weight in kg
        height_cm (float): height in centimetres

    Returns:
        float: BMI rounded to 1 decimal place
    """
    if weight <= 0:
        raise ValueError("Weight must be a positive number.")
    if height_cm <= 0:
        raise ValueError("Height must be a positive number.")

    height_m = height_cm / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)


def calculate_bmr(age, sex, weight, height_cm):
    """
    Calculate Basal Metabolic Rate using the Mifflin-St Jeor equation.

    Male:   BMR = (10 × weight) + (6.25 × height) − (5 × age) + 5
    Female: BMR = (10 × weight) + (6.25 × height) − (5 × age) − 161

    Args:
        age       (int):   age in years
        sex       (str):   'male' or 'female'
        weight    (float): body weight in kg
        height_cm (float): height in centimetres

    Returns:
        float: BMR in kcal/day rounded to 1 decimal place
    """
    if age <= 0:
        raise ValueError("Age must be a positive number.")
    if weight <= 0:
        raise ValueError("Weight must be a positive number.")
    if height_cm <= 0:
        raise ValueError("Height must be a positive number.")

    sex = sex.lower().strip()
    if sex not in ("male", "female"):
        raise ValueError("Sex must be 'male' or 'female'.")

    bmr = (10 * weight) + (6.25 * height_cm) - (5 * age)
    bmr += 5 if sex == "male" else -161
    return round(bmr, 1)


def calculate_tdee(bmr, activity_level):
    """
    Calculate Total Daily Energy Expenditure.
    Multiplies BMR by an activity factor.

    Activity factors:
        sedentary  : 1.2   (little or no exercise)
        light      : 1.375 (1–3 days/week)
        moderate   : 1.55  (3–5 days/week)
        active     : 1.725 (6–7 days/week)
        very_active: 1.9   (hard training every day)

    Args:
        bmr            (float): basal metabolic rate in kcal/day
        activity_level (str):   one of the keys listed above

    Returns:
        float: TDEE in kcal/day rounded to 1 decimal place
    """
    activity_factors = {
        "sedentary":   1.2,
        "light":       1.375,
        "moderate":    1.55,
        "active":      1.725,
        "very_active": 1.9,
    }

    activity_level = activity_level.lower().strip()
    if activity_level not in activity_factors:
        valid = ", ".join(activity_factors.keys())
        raise ValueError(
            f"Invalid activity level '{activity_level}'. Choose from: {valid}"
        )

    return round(bmr * activity_factors[activity_level], 1)


def calculate_goal_calories(tdee, goal):
    """
    Adjust TDEE based on the user's fitness goal.

    Adjustments:
        bulk     : +400 kcal
        maintain :   ±0 kcal
        cut      : −400 kcal

    Args:
        tdee (float): total daily energy expenditure in kcal/day
        goal (str):   'bulk', 'maintain', or 'cut'

    Returns:
        float: recommended daily calories rounded to 1 decimal place
    """
    adjustments = {
        "bulk":     400,
        "maintain":   0,
        "cut":     -400,
    }

    goal = goal.lower().strip()
    if goal not in adjustments:
        valid = ", ".join(adjustments.keys())
        raise ValueError(f"Invalid goal '{goal}'. Choose from: {valid}")

    return round(tdee + adjustments[goal], 1)


def calculate_macros(weight, calorie_target):
    """
    Calculate daily macronutrient targets.

    Rules:
        Protein : 1.8 g per kg of body weight  (4 kcal/g)
        Fat     : 25% of total calories         (9 kcal/g)
        Carbs   : remaining calories            (4 kcal/g)

    Args:
        weight         (float): body weight in kg
        calorie_target (float): recommended daily calorie intake

    Returns:
        dict: {
            'protein_g': float,
            'fat_g':     float,
            'carbs_g':   float
        }
    """
    if weight <= 0:
        raise ValueError("Weight must be a positive number.")
    if calorie_target <= 0:
        raise ValueError("Calorie target must be a positive number.")

    protein_g = round(1.8 * weight, 1)
    fat_g     = round((0.25 * calorie_target) / 9, 1)

    protein_kcal  = protein_g * 4
    fat_kcal      = fat_g * 9
    remaining_kcal = calorie_target - protein_kcal - fat_kcal
    carbs_g = round(max(remaining_kcal / 4, 0), 1)  # never negative

    return {
        "protein_g": protein_g,
        "fat_g":     fat_g,
        "carbs_g":   carbs_g,
    }


def full_nutrition_calculation(user_data):
    """
    Run a complete nutrition calculation from a single user data dict.

    Expected keys in user_data:
        age      (int)   – years
        sex      (str)   – 'male' or 'female'
        weight   (float) – kg
        height   (float) – cm
        activity (str)   – sedentary | light | moderate | active | very_active
        goal     (str)   – bulk | maintain | cut

    Args:
        user_data (dict): user physical profile

    Returns:
        dict: {
            'bmi':                  float,
            'bmr':                  float,
            'tdee':                 float,
            'recommended_calories': float,
            'macros': {
                'protein_g': float,
                'fat_g':     float,
                'carbs_g':   float
            }
        }

    Raises:
        ValueError: if any required field is missing or invalid
    """
    required = {"age", "sex", "weight", "height", "activity", "goal"}
    missing  = required - user_data.keys()
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(sorted(missing))}")

    age      = user_data["age"]
    sex      = user_data["sex"]
    weight   = user_data["weight"]
    height   = user_data["height"]
    activity = user_data["activity"]
    goal     = user_data["goal"]

    bmi                  = calculate_bmi(weight, height)
    bmr                  = calculate_bmr(age, sex, weight, height)
    tdee                 = calculate_tdee(bmr, activity)
    recommended_calories = calculate_goal_calories(tdee, goal)
    macros               = calculate_macros(weight, recommended_calories)

    return {
        "bmi":                  bmi,
        "bmr":                  bmr,
        "tdee":                 tdee,
        "recommended_calories": recommended_calories,
        "macros":               macros,
    }