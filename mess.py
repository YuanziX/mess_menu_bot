import re
import pytz
import pandas as pd
from datetime import datetime, timedelta

time_slot = {900: "BREAKFAST", 1400: "LUNCH", 1830: "SNACKS", 2100: "DINNER"}
dayOfTheWeek = {
    0: "MONDAY",
    1: "TUESDAY",
    2: "WEDNESDAY",
    3: "THURSDAY",
    4: "FRIDAY",
    5: "SATURDAY",
    6: "SUNDAY",
}


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


def _getTimeWeekDayDateLastDate():
    dt = datetime.now(pytz.timezone("Asia/Kolkata"))
    return (
        dt.time().hour * 100 + dt.time().minute,
        dt.date().weekday(),
        dt.date().day,
        last_day_of_month(dt).day,
    )


def _getNextMeal(time):
    for key in sorted(time_slot.keys()):
        if time < key:
            return key, time_slot[key]
    return 900, time_slot[900]  # Return breakfast if after 2100


def capitalize(string):
    if isinstance(string, list):
        return _capitalize_array(string)

    return _capitalize_string(string)


def _capitalize_array(string: list) -> str:
    for index, item in enumerate(string):
        string[index] = _capitalize_string(item)
    return string


def _capitalize_string(string: str) -> str:
    return string[0].upper() + string[1:].lower()


def get_meal(mess_menu: pd.DataFrame, day: str, date: int, meal_time: int, meal_name: str):
    meals = mess_menu.loc[day]
    meal_index = list(time_slot.values()).index(meal_name)
    meal = meals.iloc[meal_index]
    return f"```{capitalize(meal_name)}\n{meal}```"


def next_n_meals(mess_menu: pd.DataFrame, n: int):
    time, week_day, date, last_day = _getTimeWeekDayDateLastDate()
    next_meal_time, next_meal_name = _getNextMeal(time)
    
    meals = []
    current_day = None
    for _ in range(n):
        day = dayOfTheWeek[week_day]
        if day != current_day:
            meals.append(f"\n*{date} - {day}*")
            current_day = day
        
        meals.append(get_meal(mess_menu, day, date, next_meal_time, next_meal_name))
        
        # Move to the next meal
        time = next_meal_time
        next_meal_time, next_meal_name = _getNextMeal(time + 1)
        
        # Check if we've reached the end of the day
        if next_meal_time == 900:  # This means we're moving to breakfast of the next day
            week_day = (week_day + 1) % 7
            date = (date % last_day) + 1
            current_day = None  # Reset current_day to print the new day
    
    return "\n".join(meals)


def clean_mess_menu(file_location: str) -> pd.DataFrame:
    """
    Reads an messy excel mess menu, cleans it, and saves it as a CSV.

    Args:
        file_path: Path to the excel file containing the mess menu.

    Returns:
        dataframe object: Cleaned mess menu.
    """
    menu = pd.read_excel(file_location)
    clean_menu = menu.dropna(axis=0, how="all").dropna(axis=1, how="all")
    clean_menu.columns = clean_menu.iloc[0].to_list()
    clean_menu = clean_menu.iloc[1:]
    clean_menu.index = clean_menu.iloc[:, 0]
    clean_menu = clean_menu.drop("DAYS", axis=1)
    clean_menu = clean_menu.replace(r"\s+", " ", regex=True)
    clean_menu.rename(columns={"BREAK FAST": "BREAKFAST"}, inplace=True)

    return clean_menu


if __name__ == "__main__":
    print(next_n_meals(clean_mess_menu("mess_menus\\FINAL_VEG_NONVEG_SEPTEMBER_MENU.xlsx"), 5))
