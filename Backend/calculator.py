import json

#load food database
def load_foods(): #when function is called, return food data
    with open("Backend/foods.json", "r") as file: #read file
        return json.load(file) #converts to python dict

#Calculate total macros for food entries
def calculate_total(food_entries, foods):
    #food_entries: list of food name and grams
    #dict to store totals
    total = {
        "Calories": 0,
        "Protein (g)": 0,
        "Carbs (g)": 0,
        "Fat (g)": 0
    }
    
    for food_name, grams in food_entries: #loop through food entries
        food_name = food_name.lower() #prevents case sensitivity issues
        if food_name not in foods: #checks if food is in db
            print(f"Warning: '{food_name}' not found in database. Skipping.")
            continue
        
        food = foods[food_name] #gets food data from db
        multiplier = grams / 100 

        total["Calories"] += food["calories_per_100g"] * multiplier
        total["Protein (g)"] += food["protein_per_100g"] * multiplier
        total["Carbs (g)"] += food["carbs_per_100g"] * multiplier
        total["Fat (g)"] += food["fat_per_100g"] * multiplier

    # Round totals
    total = {k: round(v, 2) for k, v in total.items()}
    return total

# --- Run the food tracker ---
def run_food_tracker():
    foods = load_foods()
    food_entries = []

    print("\n=== Food Tracker ===")
    print("Enter the foods you ate today (type 'done' when finished)\n")

    while True:
        food_name = input("Food name: ")
        if food_name.lower() == "done":
            break

        try:
            grams = float(input("Amount in grams: "))
        except ValueError:
            print("Please enter a valid number for grams.")
            continue

        food_entries.append((food_name, grams))

    totals = calculate_total(food_entries, foods)

    print("\n=== TOTAL DAILY MACROS ===")
    for k, v in totals.items():
        print(f"{k}: {v}")

    return totals