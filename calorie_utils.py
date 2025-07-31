def calculate_bmr(sex, weight, height, age):
    bmr = 10 * weight + 6.25 * height - 5 * age
    bmr += 5 if sex == "male" else -161
    return bmr

def calculate_maintenance(bmr, activity_multiplier):
    return bmr * activity_multiplier

def calculate_goal_calories(maintenance, goal):
    modifiers = {
        "Maintain": 1.0,
        "Slow Cut": 0.85,
        "Aggressive Cut": 0.75,
        "Slow Bulk": 1.10,
        "Aggressive Bulk": 1.20
    }
    return maintenance * modifiers[goal]

def calories_from_macros(log):
    protein = log.get("protein", 0)
    carbs = log.get("carbohydrate", 0)
    fat = log.get("fat", 0)

    return {
        "Protein": round(protein * 4, 1),
        "Carbs": round(carbs * 4, 1),
        "Fat": round(fat * 9, 1)
    }
