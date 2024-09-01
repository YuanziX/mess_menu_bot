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


def _getMealType(time):
    for key in time_slot.keys():
        if time < key:
            return time_slot[key]

    return None


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


def get_meal(mess_menu: pd.DataFrame, date: int, day: str, meal_type: str):
    meal_items = mess_menu.loc[day, meal_type]

    parts = re.split(r"(\d\))", meal_items)

    formatted_items = ""
    i = 1
    while i < len(parts):
        number = parts[i].strip() if i < len(parts) else ""
        item = parts[i + 1].strip() if (i + 1) < len(parts) else ""

        if item:
            formatted_items += f"{' ' * 8}{number} {item}\n"

        i += 2

    if not re.search(r"\d\)", meal_items):
        formatted_items = f"{' ' * 8}{meal_items.strip()}"

    return f"{date} - {capitalize(day)}: {capitalize(meal_type)}\n{formatted_items}"


def next_n_meals(mess_menu: pd.DataFrame, n: int):
    meals = []
    current_time, current_day, current_date, last_date = _getTimeWeekDayDateLastDate()
    day_count = 0

    while len(meals) < n:
        if current_date > last_date:
            break

        day_index = (current_day + day_count) % 7
        day = dayOfTheWeek[day_index]

        if day_count == 0:
            start_meal = _getMealType(current_time)
        else:
            start_meal = None

        meal_started = start_meal is None
        for _, meal_type in time_slot.items():
            if not meal_started and meal_type == start_meal:
                meal_started = True

            if meal_started:
                meal = get_meal(mess_menu, current_date + day_count, day, meal_type)
                meals.append(meal)

                if len(meals) == n:
                    return meals
        meals[-1] = meals[-1] + "\n"
        day_count += 1

    return meals
