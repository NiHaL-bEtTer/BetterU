from calculator import run_food_tracker

# --- Function to generate recommended macros based on profile ---
def generate_macro_goals(profile):
    """
    profile: dict with weight (kg), height (cm), age, gender, activity_level (1-3), goal
    Returns recommended calories and macros.
    """
    weight = profile["weight"]
    height = profile["height"]
    age = profile["age"]
    gender = profile["gender"].lower()
    activity_level = int(profile["activity_level"])
    goal = profile["goal"].lower()

    # --- BMR calculation (Mifflin-St Jeor) ---
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # --- Activity multiplier ---
    activity_multipliers = {
        1: 1.375,  # 1-3 days/week light activity
        2: 1.55,   # moderate activity 3-5 days/week
        3: 1.725   # heavy activity 6-7 days/week
    }
    tdee = bmr * activity_multipliers.get(activity_level, 1.2)  # default sedentary 1.2

    # --- Adjust calories based on goal ---
    if goal == "fat loss":
        calories = tdee * 0.8  # 20% deficit
    elif goal == "muscle gain":
        calories = tdee * 1.15  # 15% surplus
    else:  # maintain fitness
        calories = tdee

    # --- Macro split ---
    protein = 1.8 * weight  # grams
    fat = 0.25 * calories / 9  # grams
    carbs = (calories - (protein * 4 + fat * 9)) / 4  # grams

    # Round numbers
    calories = round(calories)
    protein = round(protein, 1)
    fat = round(fat, 1)
    carbs = round(carbs, 1)

    return {
        "Calories": f"{calories} kcal",
        "Protein": f"{protein} g",
        "Carbs": f"{carbs} g",
        "Fat": f"{fat} g"
    }

# --- Main program ---
def main():
    print("=== Welcome to Fitness AI ===\n")

    # --- User profile ---
    profile_saved = False
    user_profile = {}

    while True:
        print("\nWhat would you like to do?")
        print("1. Enter or update profile info")
        print("2. Track foods for calories/macros")
        print("3. View recommended daily macros")
        print("4. Exit")

        choice = input("Select an option (1/2/3/4): ")

        if choice == "1":
            try:
                weight = float(input("Enter your weight (kg): "))
                height = float(input("Enter your height (cm): "))
                age = int(input("Enter your age: "))
                gender = input("Enter your gender (male/female): ")
                activity_level = int(input("Enter activity level (1-3): "))
                goal = input("Enter your goal (fat loss/muscle gain/maintain fitness): ")

                user_profile = {
                    "weight": weight,
                    "height": height,
                    "age": age,
                    "gender": gender,
                    "activity_level": activity_level,
                    "goal": goal
                }

                profile_saved = True
                print("\nProfile saved!")
            except ValueError:
                print("Please enter valid numbers for weight, height, age, and activity level.")

        elif choice == "2":
            if not profile_saved:
                print("Please enter your profile info first (option 1).")
                continue
            run_food_tracker()

        elif choice == "3":
            if not profile_saved:
                print("Please enter your profile info first (option 1).")
                continue
            print("\n=== Recommended Daily Macros ===")
            macro_goals = generate_macro_goals(user_profile)
            for k, v in macro_goals.items():
                print(f"{k}: {v}")

        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()