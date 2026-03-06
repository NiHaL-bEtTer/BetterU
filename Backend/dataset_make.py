import pandas as pd # getting the library pandas to read the csv file and manipulate the data
import json # importing the json library to convert the data into json format

INPUT_FILE = "D:\\AM - GRADE 10\\BetterU\\Data\\comprehensive_foods_usda.csv" # creating the path to the intial file that we will convert to json 
OUTPUT_FILE = "D:\\AM - GRADE 10\\BetterU\\Data\\foodsList.json" # this is the path of the file that we will create

COLUMNS = [ # here we create a list of all the columns that we want to keep from the csv file, used to filter 

"food_name",
"data_type",
"food_category",
"calories",
"carbs_g",
"calcium_mg",
"fat_g",
"protein_g",
"saturated_fat_g",
"vitamin_c_mg",
"fiber_g",
"iron_mg",
"sodium_mg",
"sugar_g",
"cholesterol_mg",
"health_score",
"food_type"

]

dataset = pd.read_csv(INPUT_FILE) # create a variable called dataset, and using pandas, we read the csv file from the input file, our foods csv, we save it in our dataset variable

dataset = dataset[COLUMNS]  # here we filter the dataset to keep only the columns we want



dataset = dataset.fillna(0) # here we fill all the empty values in the dataset with 0, this is because when we convert to json, we want to have a value for every key, and if there is an empty value, it will cause problems when we try to access it later on

foods = dataset.to_dict(orient="records") # here we convert the dataset to a list of dictionaries, where each dictionary represents a food item, and the keys are the column names, and the values are the values for that food item

with open(OUTPUT_FILE, "w", encoding="utf-8") as file: # here we open the output file, which is the json file that we will create, we open it in write mode, and we specify the encoding to be utf-8 to support all characters
    json.dump(foods, file, indent=2) # here we use the json library to dump the list of dictionaries into the file, we specify the indent to be 2 to make it more readable

print(f"Converted {len(foods)} foods to JSON.") # here we print out the number of foods that we converted to json, this is just for confirmation that the process worked and to see how many foods we have in our database