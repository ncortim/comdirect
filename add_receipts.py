from typing import Any
from helpers import prompt_text_input, dictionary_keys_to_list, ask_for_category_and_subcategory
import pandas as pd
import re
from inquirer import errors
from categories import categories


def ask_add_receipts() -> bool:
    """asks user if receipts should be added by hand

    Returns:
        bool: True is user wants to add receipts. False otherwise
    """
    confirm_add_receipts = input(
        "Do you want to add receipts by hand? Please, answer yes(y) or no(n): "
    )
    while confirm_add_receipts.lower() != 'y' and confirm_add_receipts.lower(
    ) != 'n':
        confirm_add_receipts = input(
            "Try again, please answer yes(y) or no(n). Do you want to add receipts by hand: "
        )
        if confirm_add_receipts.lower() == 'y':
            # print('add receipts - TRUE')
            return True
        elif confirm_add_receipts.lower() == 'y':
            # print('stop adding receipts -FALSE')
            return False
    if confirm_add_receipts.lower() == 'y':
        # print('add receipts - TRUE')
        return True
    elif confirm_add_receipts.lower() == 'n':
        # print('stop adding receipts -FALSE')
        return False


def booking_day_validation(answers, current):
    """validate booking data input

    Args:
        answers (_type_): _description_
        current (_type_): _description_

    Raises:
        errors.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    if current == 'c':
        return True
    if not re.match(r'\d{4}-\d{2}-\d{2}', current):
        raise errors.ValidationError(
            '', reason='Date format not allowed, please change it')
    try:
        # date_object = datetime.strptime(current, '%Y-%m-%d')
        pd.to_datetime(current)
        return True
    except ValueError:
        return False

def amount_validation(answers, current):
    """validate amount data input.

    Args:
        answers (_type_): _description_
        current (_type_): _description_

    Raises:
        errors.ValidationError: _description_

    Returns:
        _type_: _description_
    """
    if current == 'c':
        return True
    if not re.match(r'^[-+]\d*(\.\d+)?$', current):
        raise errors.ValidationError(
            '', reason='Money format not allowed, please change it')

    return True


def get_receipts_details() -> dict:
    """get receipts information from user input

    Returns:
        dict: dictionary with receipts information
    """

    first_categories = dictionary_keys_to_list(categories=categories)

    answers = {
        'Buchungstag': '',
        'Umsatz in EUR': '',
        'Kategorie': '',
        'Subkategorie': '',
    }

    category_message = 'To which category corresponds this receipt'

    booking_day = prompt_text_input(
        key_value='Buchungstag',
        message=
        'Receipt date in the folowing format YEAR-MONTH_DAY (e.g. 2020-07-08). Type "c" to cancel and go back',
        validation=booking_day_validation)

    if booking_day == 'c':
        return False
    
    amount = prompt_text_input(
        key_value='Umsatz in EUR',
        message=
        'Amount of money in the folowing format (e.g -5804.34 or +19.24) comma values are not allowed. Type "c" to cancel',
        validation=amount_validation)

    if amount == 'c':
        return False
    

    category, subcategory = ask_for_category_and_subcategory(message=category_message, first_categories=first_categories)

    while subcategory == 'cancel':
        category, subcategory = ask_for_category_and_subcategory(message=category_message, first_categories=first_categories)

    answers['Buchungstag'] = booking_day
    answers['Kategorie'] = category
    answers['Umsatz in EUR'] = amount
    answers['Subkategorie'] = subcategory

    # TODO add logger -> print(answers)    
    add_receipts_to_csv(answers)


def add_receipts_to_csv(receipts_details: dict) -> Any:
    """add categorized receipts to accounting.csv file
    """
    try:
        df = pd.read_csv('./outputs/accounting.csv')

    except OSError:
        print("""
        ########################################################################
        ########################################################################
        'ERROR: There is no file named accounting.csv in the outputs directory'
        Creating a new file...
        ########################################################################
        ########################################################################
        """)
        df = pd.DataFrame

        columns = [
            'Buchungstag', 'Vorgang', 'Buchungstext', 'Umsatz in EUR',
            'Auftraggeber', 'Beschreibung', 'Kategorie', 'Subkategorie',
            'Month', 'Year'
        ]

        df = pd.DataFrame(columns=columns)

    index = len(df.index)
    df_receipt = pd.DataFrame(data=receipts_details, index=[index])
    df = pd.concat([df, df_receipt])
    # df = df.append(receipts_details, ignore_index=True)
    df['Buchungstext'] = df['Buchungstext'].fillna(value='receipts')
    df['Vorgang'] = df['Vorgang'].fillna(value='Barauszahlung')

    # substract_caja_chica()
    df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)

    # # create a new colum for months
    df['Month'] = df['Buchungstag'].dt.strftime('%b')

    # # create a new column for years
    df['Year'] = df['Buchungstag'].dt.strftime('%Y')
    df.fillna('NaN')
    df.to_csv('./outputs/accounting.csv', index=False)


def cash_receipts():
    """run add receipts functions
    """
    while ask_add_receipts():
        get_receipts_details()
        # print(answers)
        # add_receipts_to_csv(answers)
