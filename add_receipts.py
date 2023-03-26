from typing import Any
from helpers import prompt_list_input, prompt_text_input, dictionary_keys_to_list
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
    if not re.match(r'\d{4}-\d{2}-\d{2}', current):
        raise errors.ValidationError(
            '', reason='Date format not allowed, please change it')
    return True


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

    booking_day = prompt_text_input(
        key_value='Buchungstag',
        message=
        'Receipt date in the folowing format YEAR-MONTH_DAY (e.g. 2020-07-08)',
        validation=booking_day_validation)

    amount = prompt_text_input(
        key_value='Umsatz in EUR',
        message=
        'Amount of money in the folowing format (e.g -5804.34 or +19.24) comma values are not allowed',
        validation=amount_validation)

    category = prompt_list_input(
        key_value='Category',
        message="To which category corresponds this receipt",
        choices=first_categories)

    subcategory = prompt_list_input(
        key_value='Subcategory',
        message="To which subcategory corresponds this receipt",
        choices=categories[category])

    # questions = [
    #     prom
    #     inquirer.Text(
    #         'Buchungstag', message="Receipt date in the folowing format YEAR-MONTH_DAY (e.g. 2020-07-08)", validate=buchungstag_validation),
    #     inquirer.Text(
    #         'Umsatz in EUR', message="Amount of money in the folowing format (e.g -5804.34 or 19.24) comma values are not allowed", validate=amount_validation),
    #     inquirer.Text('Auftraggeber', message="Buy description"),
    #     inquirer.List(
    #         'Category', message="To which category corresponds this receipt", choices=first_categories),
    #     inquirer.List(
    #                 'Subcategory', message="To which subcategory corresponds this receipt", choices=first_categories)

    # ]

    # answers = inquirer.prompt(questions)
    answers['Buchungstag'] = booking_day
    answers['Kategorie'] = category
    answers['Umsatz in EUR'] = amount
    answers['Subkategorie'] = subcategory

    return answers


# def substract_caja_chica(month: int, dafr: pd.DataFrame) -> None:
#     value_caja_chica = dafr.loc[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month), 'Umsatz in EUR']
#     value_receipts = dafr.loc[(dafr['Buchungstext'] == 'receipts') & (dafr['Month'] == month), 'Umsatz in EUR'].sum()
#     final_value = value_caja_chica.iloc[0] + value_receipts
#     index = dafr.index[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month)]
#     dafr['Umsatz in EUR'][index] = final_value


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


    df = df.append(receipts_details, ignore_index=True)
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
        answers = get_receipts_details()
        print(answers)
        add_receipts_to_csv(answers)
