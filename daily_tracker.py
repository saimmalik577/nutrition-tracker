# --- daily_tracker.py ---
import json
import os
from datetime import date
import pandas as pd

log_file = f"data/{date.today()}.json"

def add_entry(entry, servings, meal_type):
    if not os.path.exists("data"):
        os.makedirs("data")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            data = json.load(f)
    else:
        data = {}
    if meal_type not in data:
        data[meal_type] = []
    multiplied = {k: v * servings for k, v in entry.items()}
    data[meal_type].append(multiplied)
    with open(log_file, "w") as f:
        json.dump(data, f)

def get_daily_log():
    if not os.path.exists(log_file):
        return {}
    with open(log_file, "r") as f:
        data = json.load(f)
    all_entries = [item for meal in data.values() for item in meal]
    result = {
        "calories": sum(e.get("calories", 0) for e in all_entries),
        "protein": sum(e.get("protein", 0) for e in all_entries),
        "fat": sum(e.get("fat", 0) for e in all_entries),
        "carbohydrate": sum(e.get("carbohydrate", 0) for e in all_entries),
        "sugar": sum(e.get("sugar", 0) for e in all_entries),
        "fiber": sum(e.get("fiber", 0) for e in all_entries)
    }
    return result

def get_meal_log(meal_type):
    if not os.path.exists(log_file):
        return []
    with open(log_file, "r") as f:
        data = json.load(f)
    return data.get(meal_type, [])

def export_daily_log_csv():
    if not os.path.exists(log_file):
        return None
    with open(log_file, "r") as f:
        data = json.load(f)
    rows = []
    for meal, entries in data.items():
        for entry in entries:
            entry["meal"] = meal
            rows.append(entry)
    df = pd.DataFrame(rows)
    return df

from datetime import datetime, timedelta
import os
import pandas as pd

def get_weekly_summary():
    base_dir = "data"
    today = datetime.today().date()
    records = []

    for i in range(7):
        day = today - timedelta(days=i)
        filename = os.path.join(base_dir, f"{day}.csv")
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            total = df[["calories", "protein", "fat", "carbohydrate", "sugar", "fiber"]].sum().to_dict()
            total["date"] = day.strftime("%a %d")
            records.append(total)

    if records:
        return pd.DataFrame(records).sort_values("date")
    else:
        return pd.DataFrame()
