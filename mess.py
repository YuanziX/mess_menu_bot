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


def get_meals(mess_menu: pd.DataFrame, day: str, date: int):
    """
    Get the meals for a particular day.

    Args:
        mess_menu: Cleaned mess menu.
        day: Day for which the meals are to be fetched.

    Returns:
        dict: Meals for the given day.
    """
    meals = mess_menu.loc[day]
    meals = meals.to_list()

    for index, meal in enumerate(meals):
        meals[index] = f"```{capitalize(time_slot[list(time_slot)[index]])}\n{meal}```"

    return f"*{date} - {day}*\n\n" + "\n\n".join(meals)


def nday_meals(mess_menu: pd.DataFrame, nday: int):
    time, week_day, date, last_day = _getTimeWeekDayDateLastDate()
    if time > 2100:
        week_day = (week_day + 1) % 7

    meals = []
    for _ in range(nday):
        meals.append(get_meals(mess_menu, dayOfTheWeek[week_day], date))
        week_day = (week_day + 1) % 7

    return meals
