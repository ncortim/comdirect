import typing
import json
import pandas as pd
import glob
import os
import re
import inquirer
from inquirer import errors

categories = ['comida fuera', 'comida casa', 'bebida', 'drogerie', 'caja chica', 'medicina', 'vestimenta', 'educacion', 'home improvement',
              'tiempo libre', 'gasolina', 'transporte', 'bankkonto', 'miete', 'handy', 'versicherung', 'ingreso franzi', 'ingreso nicolas', 'zinsen', 'bundesagentur fuer arbeit - familienkasse']


def askAddReceipts() -> bool:
    askAddReceipts = input(
        "Do you want to add receipts by hand? Please, answer yes(y) or no(n): ")
    while askAddReceipts.lower() != 'y' and askAddReceipts.lower() != 'n':
        askAddReceipts = input(
            "Try again, please answer yes(y) or no(n). Do you want to add receipts by hand: ")
        if askAddReceipts.lower() == 'y':
            # print('add receipts - TRUE')
            return True
        elif askAddReceipts.lower() == 'y':
            # print('stop adding receipts -FALSE')
            return False
    if askAddReceipts.lower() == 'y':
        # print('add receipts - TRUE')
        return True
    elif askAddReceipts.lower() == 'n':
        # print('stop adding receipts -FALSE')
        return False


def buchungstag_validation(answers, current):
    if not re.match(r'\d{4}-\d{2}-\d{2}', current):
        raise errors.ValidationError(
            '', reason='Date format not allowed, please change it')
    return True


def amount_validation(answers, current):
    if not re.match(r'^[-+]\d*(\.\d+)?$', current):
        raise errors.ValidationError(
            '', reason='Money format not allowed, please change it')

    return True


def addReceipts() -> dict:
    questions = [
        inquirer.Text(
            'Buchungstag', message="Receipt date in the folowing format YEAR-MONTH_DAY (e.g. 2020-07-08)", validate=buchungstag_validation),
        inquirer.Text(
            'Umsatz in EUR', message="Amount of money in the folowing format (e.g -5804.34 or 19.24) comma values are not allowed", validate=amount_validation),
        inquirer.Text('Auftraggeber', message="Buy description"),
        inquirer.List(
            'Category', message="To which category corresponds this receipt", choices=categories,)
    ]

    answers = inquirer.prompt(questions)

    return answers

# def substract_caja_chica(month: int, dafr: pd.DataFrame) -> None:
#     value_caja_chica = dafr.loc[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month), 'Umsatz in EUR']
#     value_receipts = dafr.loc[(dafr['Buchungstext'] == 'receipts') & (dafr['Month'] == month), 'Umsatz in EUR'].sum()
#     final_value = value_caja_chica.iloc[0] + value_receipts
#     index = dafr.index[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month)]
#     dafr['Umsatz in EUR'][index] = final_value




def addReceiptsToCsv(x: dict):
    try:
        df = pd.read_csv('cuentas_full.csv')
        df = df.append(x, ignore_index=True)
        df['Buchungstext'] = df['Buchungstext'].fillna(value='receipts')
        # substract_caja_chica()
        df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)


        # # create a new colum for months
        df['Month'] = df['Buchungstag'].dt.strftime('%b')

        # # create a new column for years
        df['Year'] = df['Buchungstag'].dt.strftime('%Y')
        df.fillna('NaN')
        df.to_csv('cuentas_full.csv', index=False)
    except OSError:
        print()
        print('ERROR: There is no file named cuentas_full.csv in the current directory')
        print()




def cashReceipts():
    while askAddReceipts():
        answers = addReceipts()
        print(answers)
        addReceiptsToCsv(answers)
