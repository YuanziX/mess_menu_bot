import re
import pytz
import pandas as pd
from datetime import datetime

time_slot = {
    (730, 845): "BREAKFAST",
    (1230, 1345): "LUNCH",
    (1730, 1830): "SNACKS",
    (1930, 2045): "DINNER",
}


def _getDateTime():
    dt = datetime.now(pytz.timezone('Asia/Kolkata'))
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


def _clean_menu_entry(string: str):
    return capitalize(re.sub(r"\s+", " ", string))


def _meal_name(col: int):
    return list(time_slot.values())[col]


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
    clean_menu = clean_menu.iloc[2:-1]
    clean_menu.reset_index(drop=True, inplace=True)
    clean_menu = clean_menu.replace(r"\s+", " ", regex=True)
    clean_menu[["DAYS", "DATES"]] = clean_menu.iloc[:,0].str.split(" ", expand=True, n = 1).iloc[
        :, :2
    ]
    try:
        clean_menu.rename(columns={'BREAK FAST': 'BREAKFAST'}, inplace=True)
    except:
        pass
    clean_menu = clean_menu[
        ["DAYS", "DATES", "BREAKFAST", "LUNCH", "SNACKS", "DINNER"]
    ]

    new_mess_menu = pd.DataFrame()

    for ind, row in clean_menu.iterrows():
        try:
            for i in row['DATES'].split(','):
                new_mess_menu[int(i.strip())] = row
        except:
            try:
                new_mess_menu[int(row['DATES'])] = row
            except:
                pass

    return new_mess_menu


def next_meal(mess_menu: pd.DataFrame):
    dt = _getDateTime()

    for index, item in enumerate(time_slot.items()):
        if dt[0] <= item[0][1]:
            col = item[1]
            break
    else:
        col = "BREAKFAST"
        dt[1] += 1

    for index, date in enumerate(mess_menu.DATES):
        dates = [int(i) for i in date.replace(' ', '').split(",")]
        if dt[1] in dates:
            row = index
            break

    return f"Next meal is {capitalize(col)}. The meal contains {_clean_menu_entry(mess_menu[col][row])}."


def add_to_meals(meals: list, col: int, row: int, mess_menu: pd.DataFrame):
    meal = _meal_name(col)
    meals.append(f"{capitalize(meal)}: {_clean_menu_entry(mess_menu[meal][row])}")



def next_four_meals(mess_menu: pd.DataFrame):
    dt = _getDateTime()
    meals = []
    for ind, item in enumerate(time_slot.items()):
        if dt[0] <= item[0][1]:
            col = ind
            break
    else:
        col = 0
        dt[1] += 1

    for ind, date in enumerate(mess_menu.DATES):
        dates = [int(i) for i in date.replace(' ', '').split(",")]
        if dt[1] in dates:
            row = ind
            break
    
    add_to_meals(meals, col, row, mess_menu)

    while len(meals) < 4:
        col = col + 1
        if col >= 4:
            col %= 4
            row = (row + 1) % mess_menu.shape[0]
        add_to_meals(meals, col, row, mess_menu)

    return meals