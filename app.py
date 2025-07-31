import streamlit as st
from daily_tracker import get_weekly_summary
from datetime import date
from ocr_utils import extract_text_from_image, parse_nutrition_info
from daily_tracker import export_daily_log_csv
from calorie_utils import (
    calculate_bmr,
    calculate_maintenance,
    calculate_goal_calories,
    calories_from_macros
)
from daily_tracker import add_entry, get_daily_log, get_meal_log
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nutrition OCR Tracker", page_icon="🍎")
st.title("📸 Nutrition Label Scanner & Calorie Tracker 🚀")  # added 🚀 emoji

# --- Upload Section ---
uploaded_file = st.file_uploader("Upload a nutrition label photo", type=["jpg", "png", "jpeg"])
if uploaded_file:
    text = extract_text_from_image(uploaded_file)
    st.subheader("📝 Extracted Text")
    st.code(text)

    parsed = parse_nutrition_info(text)
    st.subheader("📊 Parsed Nutrition Info")

    cols = st.columns(3)
    cols[0].metric("🔥 Calories", f"{int(parsed.get('calories', 0))} kcal")
    cols[1].metric("💪 Protein", f"{round(parsed.get('protein', 0), 1)}g")
    cols[2].metric("🥑 Fat", f"{round(parsed.get('fat', 0), 1)}g")

    cols2 = st.columns(3)
    cols2[0].metric("🍞 Carbs", f"{round(parsed.get('carbohydrate', 0), 1)}g")
    cols2[1].metric("🍬 Sugar", f"{round(parsed.get('sugar', 0), 1)}g")
    cols2[2].metric("🌾 Fiber", f"{round(parsed.get('fiber', 0), 1)}g")

    servings = st.number_input("How many servings?", min_value=1, max_value=10, value=1)
    meal = st.selectbox("Meal Type", ["🍳 Breakfast", "🍔 Lunch", "🍽 Dinner", "🍎 Snack"])

    if st.button("➕ Add to Daily Log"):
        add_entry(parsed, servings, meal)
        st.success(f"Added to {meal}!")

# --- Daily Log Section ---
st.markdown("---")
st.subheader("📅 Today's Intake")
daily_log = get_daily_log()

if daily_log:
    st.write("### Nutrient Summary Today")
    dcols = st.columns(3)
    dcols[0].metric("🔥 Calories", f"{int(daily_log.get('calories', 0))} kcal")
    dcols[1].metric("💪 Protein", f"{round(daily_log.get('protein', 0), 1)}g")
    dcols[2].metric("🥑 Fat", f"{round(daily_log.get('fat', 0), 1)}g")

    dcols2 = st.columns(3)
    dcols2[0].metric("🍞 Carbs", f"{round(daily_log.get('carbohydrate', 0), 1)}g")
    dcols2[1].metric("🍬 Sugar", f"{round(daily_log.get('sugar', 0), 1)}g")
    dcols2[2].metric("🌾 Fiber", f"{round(daily_log.get('fiber', 0), 1)}g")
else:
    st.info("No entries logged yet today.")

# --- Meal Breakdown ---
st.markdown("---")
st.subheader("🍽 View by Meal")
meal_choice = st.selectbox("Select Meal", ["🍳 Breakfast", "🍔 Lunch", "🍽 Dinner", "🍎 Snack"])
meal_log = get_meal_log(meal_choice)

if meal_log:
    st.write(f"### {meal_choice} Intake")
    combined = {
        "calories": sum(item.get("calories", 0) for item in meal_log),
        "protein": sum(item.get("protein", 0) for item in meal_log),
        "fat": sum(item.get("fat", 0) for item in meal_log),
        "carbohydrate": sum(item.get("carbohydrate", 0) for item in meal_log),
        "sugar": sum(item.get("sugar", 0) for item in meal_log),
        "fiber": sum(item.get("fiber", 0) for item in meal_log),
    }

    mcols = st.columns(3)
    mcols[0].metric("🔥 Calories", f"{int(combined['calories'])} kcal")
    mcols[1].metric("💪 Protein", f"{round(combined['protein'], 1)}g")
    mcols[2].metric("🥑 Fat", f"{round(combined['fat'], 1)}g")

    mcols2 = st.columns(3)
    mcols2[0].metric("🍞 Carbs", f"{round(combined['carbohydrate'], 1)}g")
    mcols2[1].metric("🍬 Sugar", f"{round(combined['sugar'], 1)}g")
    mcols2[2].metric("🌾 Fiber", f"{round(combined['fiber'], 1)}g")
else:
    st.info("No entries for that meal yet.")

# --- Calorie Needs Calculator ---
st.markdown("---")
st.subheader("⚙️ Calorie Needs & Goal Planner")

col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender", ["male", "female"])
    age = st.number_input("Age", min_value=10, max_value=100, value=22)
    weight = st.number_input("Weight (kg)", value=93.0)
    height = st.number_input("Height (cm)", value=180.0)

with col2:
    activity_levels = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }
    activity_label = st.selectbox("Activity Level", list(activity_levels.keys()))
    activity_multiplier = activity_levels[activity_label]
    goal = st.selectbox("Goal", ["Maintain", "Slow Cut", "Aggressive Cut", "Slow Bulk", "Aggressive Bulk"])

if st.button("🔥 Calculate My Plan"):
    bmr = calculate_bmr(gender, weight, height, age)
    maintenance = calculate_maintenance(bmr, activity_multiplier)
    goal_cals = calculate_goal_calories(maintenance, goal)

    st.success(f"🧠 Your BMR is ~{int(bmr)} kcal")
    st.info(f"⚖️ Maintenance Calories: ~{int(maintenance)} kcal/day")

    if "Cut" in goal:
        st.warning(f"✂️ Goal: {goal} → Eat ~{int(goal_cals)} kcal/day")
    elif "Bulk" in goal:
        st.success(f"📈 Goal: {goal} → Eat ~{int(goal_cals)} kcal/day")
    else:
        st.info(f"🎯 Goal: {goal} → Eat ~{int(goal_cals)} kcal/day")

    if daily_log and "calories" in daily_log:
        current_cals = daily_log["calories"]
        ratio = min(current_cals / goal_cals, 1.0)
        st.progress(ratio, text=f"{int(current_cals)} / {int(goal_cals)} kcal consumed")

    st.write("### 🧁 Macro Distribution (Calories)")
    macro_cals = calories_from_macros(daily_log)
    labels = list(macro_cals.keys())
    sizes = list(macro_cals.values())

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)


st.markdown("---")
st.subheader("📤 Export")

if st.button("📥 Export Today's Log as CSV"):
    df = export_daily_log_csv()
    if df is not None and not df.empty:
        st.dataframe(df)
        st.download_button(
            label="Download CSV",
            data=df.to_csv(index=False).encode(),
            file_name=f"nutrition_log_{date.today()}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data to export yet.")

# --- Weekly Trend Section ---
# --- Weekly Trend Section ---
st.markdown("---")
st.subheader("📆 Weekly Nutrition Trends")

df_week = get_weekly_summary()
if not df_week.empty:
    available_metrics = ["calories", "protein", "carbohydrate", "fat"]
    nutrient_labels = {
        "calories": "🔥 Calories",
        "protein": "💪 Protein",
        "carbohydrate": "🍞 Carbs",
        "fat": "🥑 Fat"
    }

    selected = st.multiselect(
        "Choose nutrients to display", 
        options=available_metrics,
        default=available_metrics
    )

    if selected:
        chart_data = df_week.set_index("date")[selected]
        chart_data.columns = [nutrient_labels[n] for n in selected]
        st.line_chart(chart_data)
        st.caption("Macronutrient intake over the past 7 days")
    else:
        st.warning("Select at least one nutrient to display.")
else:
    st.info("No data available for the past 7 days.")


