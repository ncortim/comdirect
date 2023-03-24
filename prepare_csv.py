import typing
import shutil
import json
import pandas as pd
import glob
import os
import re
from categories import categories
import inquirer


def get_file_name(accounting_filename: bool = False):
# def get_file_name() -> typing.Union[str, bool]:
    """
    Gets name of file if is present in current directory,
    otherwise returns false

    Returns:
        typing.Union[str, bool]: [str -> name of file
        bool -> false if file does not exist in directory]
    """
    if accounting_filename:
        filename = glob.glob('./outputs/accounting.csv')
        if filename:
            return filename[0]
        return False
    else:
        filename = glob.glob('./inputs/umsaetze*')
        if filename:
            return filename[0]
        return False

def get_key_by_value(dictionary: dict, value_to_find: str) -> typing.Any:
    """
    Given a value it returns the corresponding
    key in a dictionary 

    Args:
        dict ([type]): [description]
        valueToFind ([type]): [description]

    Returns:
        [type]: [description]
    """
    for k, v in dictionary.items():
        if value_to_find in v:
            return k
        # return None

def create_dataframe(filename:str) -> pd.DataFrame:

    # read csv file, skip header and footer and encoding umlaut
    # create a dataframe
    df = pd.read_csv(filename,
                    encoding="ISO-8859-1",
                    sep=';',
                    skiprows=4,
                    skipfooter=7,
                    engine='python')
    
    # change format euro decimals and thousands
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(".", "", regex=True)
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(",", ".", regex=True).astype(float)

    # drop rows with status 'offen'
    df = df[df.Buchungstag != 'offen']

    # drop last column 'Unnamed: 5'
    df.drop(df.columns[-1], axis=1, inplace=True)

    # drop second column 'Wertstellung (Valuta)'
    df.drop(df.columns[1], axis=1, inplace=True)

    # extract company's name where purchase was made
    # from Buchungstext column and save it to Auftraggeber
    for idx, i in enumerate(df['Buchungstext']):
        description = i.split(':', 1)[0]
        if description == 'Auftraggeber':
            purchaser = i.split(':', 2)[1].split('Buchungstext')[0].strip()
            if purchaser == 'Lastschrift aus Kartenzahlung':
                detailed_purchaser = i.split(':', 2)[2].split('//')[0].strip()
                df.loc[idx, 'Auftraggeber'] =  detailed_purchaser
            else:
                df.loc[idx, 'Auftraggeber'] =  purchaser
        # i.split(':', 1)[1].split(':', 1)[0].split('Buchungstext')[0].strip()
        elif description == ' Buchungstext':
            df.loc[idx, 'Auftraggeber'] = re.compile(
                r'\d{4}-\d{2}-\d{2}').split(i)[0].split(':', 1)[1].strip()
        elif description == 'Empfänger':
            df.loc[idx, 'Auftraggeber'] = re.compile(r'Kto').split(i)[0].split(
                ':', 1)[1].strip()


    # extract buchungstext from purchase
    for idx, i in enumerate(df['Buchungstext']):
        description = i.split(':',2)[-1].strip()
        df.loc[idx, 'Beschreibung'] = description

    # create a new category
    df['Kategorie'] = ''

    # create subcategory
    df['Subkategorie'] = ''

    df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)

    mapping_types_conversion = {
        'Vorgang': 'string',
        'Buchungstext': 'string',
        # 'Auftraggeber': 'string',
        # 'Beschreibung': 'string',
        'Kategorie': 'string',
        'Subkategorie': 'string'
    }

    df = df.astype(mapping_types_conversion)

    # df['Kategorie'].astype

        # create a new colum for months
    df['Month'] = df['Buchungstag'].dt.strftime('%b')

    # create a new column for years
    df['Year'] = df['Buchungstag'].dt.strftime('%Y')
    # print(df.dtypes)
    # print(df)

    return df

def prompt_question(purchaser: str, booking_detail: str, choices: list, euro: float) -> str:
    questions = [
            inquirer.List(
                'category',
                message=f'Select category: {purchaser}  EURO: {euro}?',
                choices=choices)
        ]
    answers = inquirer.prompt(questions)

    return answers['category']

def create_dataframe_accounting_csv(filename:str) -> pd.DataFrame:

    df = pd.read_csv(filename, encoding="ISO-8859-1",sep=',')

    return df


def save_df_to_csv(df: pd.DataFrame) -> None:
    # if cuentas_full.csv exists then append values to it without header and indexes
    # esle create a new one
    if os.path.isfile('./outputs/accounting.csv'):
        df.to_csv('./outputs/accounting.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('./outputs/accounting.csv', index=False)

def categorize_purchases(new_df: pd.DataFrame, accounting_df: pd.DataFrame = None) -> pd.DataFrame:


    first_categories = list()

    for i in categories:
        first_categories.append(i)

    for idx, i in enumerate(new_df["Auftraggeber"]):
        # check in value already present in categories dict
        try:
            if i in accounting_df['Auftraggeber'].values:
                match_indexes = accounting_df[accounting_df['Auftraggeber']==i].index.values
                repeated_category = accounting_df.at[match_indexes[0], 'Kategorie']
                repeated_subcategory = accounting_df.at[match_indexes[0], 'Subkategorie']
                new_df.at[idx, 'Kategorie'] = repeated_category
                new_df.at[idx, 'Subkategorie'] = repeated_subcategory
            else:               
                raise ValueError
        except (TypeError, ValueError):     
            category = prompt_question(i, new_df.at[idx, 'Beschreibung'],first_categories, new_df.at[idx, 'Umsatz in EUR'])

            new_df.at[idx, 'Kategorie'] = category

            subcategory = prompt_question(i, new_df.at[idx, 'Beschreibung'], categories[category], new_df.at[idx, 'Umsatz in EUR'])
            new_df.at[idx, 'Subkategorie'] = subcategory

        
    return new_df


new_filename = get_file_name()

accounting_file = get_file_name(accounting_filename=True)

new_df = create_dataframe(filename=new_filename)


try:
    new_df = create_dataframe(filename=new_filename)
    accounting_df = create_dataframe_accounting_csv(accounting_file)
except ValueError:
    print("file does not exist yet")

try:
    new_df = categorize_purchases(new_df, accounting_df)
except NameError:
    new_df = categorize_purchases(new_df)

save_df_to_csv(new_df)

shutil.copy(new_filename, './raw_files/')
os.remove(new_filename)