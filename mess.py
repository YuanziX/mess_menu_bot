import pytz
import pandas as pd
from datetime import datetime

time_slot = [845, 1345, 1830, 2045]


def _getDateTime():
    dt = datetime.now(pytz.timezone("Asia/Kolkata"))
    return [dt.time().hour * 100 + dt.time().minute, dt.date().day]


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
    clean_menu.columns = clean_menu.iloc[1].to_list()
    clean_menu = clean_menu.iloc[2:]
    clean_menu.reset_index(drop=True, inplace=True)
    clean_menu = clean_menu.replace(r"\s+", " ", regex=True)
    clean_menu[["DAYS", "DATES"]] = (
        clean_menu.iloc[:, 0].str.split(" ", expand=True, n=1).iloc[:, :2]
    )

    clean_menu.rename(columns={"BREAK FAST": "BREAKFAST"}, inplace=True)
    clean_menu = clean_menu[["DAYS", "DATES", "BREAKFAST", "LUNCH", "SNACKS", "DINNER"]]

    new_mess_menu = pd.DataFrame()

    for ind, row in clean_menu.iterrows():
        try:
            for i in row["DATES"].split(","):
                new_mess_menu[int(i.strip())] = row
        except AttributeError:
            try:
                new_mess_menu[int(row["DATES"])] = row
            except ValueError:
                pass

    return new_mess_menu


def get_meal(mess_menu: pd.DataFrame, date: int, meal_index: int):
    return mess_menu.loc[:, date].iloc[meal_index]


def next_n_meals(mess_menu: pd.DataFrame, n: int):
    meals = []
    dt = _getDateTime()

    for index, item in enumerate(time_slot):
        if dt[0] <= item:
            meal_index = index + 2
            break
    else:
        meal_index = 2
        dt[1] += 1

    meals.append(get_meal(mess_menu, dt[1], meal_index))

    for i in range(n - 1):
        if meal_index == 5:
            meal_index = 2
            dt[1] += 1
        else:
            meal_index += 1
        meals.append(get_meal(mess_menu, dt[1], meal_index))

    return meals


def next_meal(mess_menu: pd.DataFrame):
    next_n_meals(mess_menu, 1)


def next_four_meal(mess_menu: pd.DataFrame):
    next_n_meals(mess_menu, 4)
