import typing
import json
import pandas as pd
import glob
import os
import re
import inquirer


def get_file_name():
# def get_file_name() -> typing.Union[str, bool]:
    """
    Gets name of file if is present in current directory,
    otherwise returns false

    Returns:
        typing.Union[str, bool]: [str -> name of file
        bool -> false if file does not exist in directory]
    """
    filename = glob.glob('umsaetze*')
    if filename:
        return filename[0]
    return False


def getKeysByValue(dictionary: dict, valueToFind: str) -> typing.Any:
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
        if valueToFind in v:
            return k
        # return None


def prepare_csv_file(filename: str) -> typing.Any:

    # read csv file, skip header and footer and encoding umlaut
    # create a dataframe
    df = pd.read_csv(filename,
                     encoding="ISO-8859-1",
                     sep=';',
                     skiprows=4,
                     skipfooter=4,
                     engine='python')

    # change format euro decimals and thousands
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(".", "")
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(",", ".").astype(float)

    # drop last column 'Unnamed: 5'
    df.drop(df.columns[-1], axis=1, inplace=True)

    # drop second column 'Wertstellung (Valuta)'
    df.drop(df.columns[1], axis=1, inplace=True)

    # extract company's name where purchase was made
    # from Buchungstext column and save it to Auftraggeber
    for idx, i in enumerate(df['Buchungstext']):
        description = i.split(':', 1)[0]
        if description == 'Auftraggeber':
            df.loc[idx, 'Auftraggeber'] = i.split(':', 1)[1].split(
                ':', 1)[0].split('Buchungstext')[0].strip()
        elif description == ' Buchungstext':
            df.loc[idx, 'Auftraggeber'] = re.compile(
                r'\d{4}-\d{2}-\d{2}').split(i)[0].split(':', 1)[1].strip()
        elif description == 'Empfänger':
            df.loc[idx, 'Auftraggeber'] = re.compile(r'Kto').split(i)[0].split(
                ':', 1)[1].strip()

    # drop rows with status 'offen'
    df = df[df.Buchungstag != 'offen']

    # create a new category
    df['Category'] = ''

    # define categories
    categories = [
        'comida fuera', 'comida casa', 'bebida', 'drogerie', 'caja chica',
        'medicina', 'vestimenta', 'educacion', 'home improvement',
        'tiempo libre', 'gasolina', 'transporte', 'bankkonto', 'miete',
        'handy', 'versicherung', 'ingreso franzi', 'ingreso nicolas', 'zinsen',
        'bundesagentur fuer arbeit - familienkasse'
    ]

    # list with shop's names
    shopsNames = []

    # populate shopsNames list with data from df (data frame)
    for i in df['Auftraggeber']:
        shopsNames.append(i.lower())
        # shopsNames.append(i)

    # remove duplicates from shopsNames
    shopsNamesUnique = list(set(shopsNames))

    # create a dictionary for storing shops according to categories
    categories_dict: dict = {key: [] for key in categories}

    # store the dictionary as json file
    # create a file if not existent and dump categories_dict
    # only used the first time, keep uncommented, otherwise will delete all categorized_shops
    if os.path.isfile('categorized_shops.json'):
        with open('categorized_shops.json') as json_file:
            categories_dict = json.load(json_file)
    else:
        with open('categorized_shops.json', 'w') as json_file:
            json.dump(categories_dict, json_file)

    # loop through each available shop and assing it to a category
    for i in shopsNamesUnique:
        # check in value already present in categories dict
        if i in [x for v in categories_dict.values() for x in v]:
            pass
        else:
            questions = [
                inquirer.List(
                    'category',
                    message=f'to what category belongs this shop: {i.upper()}?',
                    choices=categories)
            ]
            # 'category', message='to what category belongs this shop: {i.upper()}?', choices=categories)]
            answers = inquirer.prompt(questions)
            categories_dict[answers["category"]].append(i)

    # save categories dictionry as json file
    with open('categorized_shops.json', 'w') as json_file:
        json.dump(categories_dict, json_file)

    # assign each defined category to respective row in dataframe df
    for idx, i in enumerate(df['Auftraggeber']):
        key = getKeysByValue(categories_dict, i.lower())
        df.iloc[idx, df.columns.get_loc('Category')] = key

    # change date format
    df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)

    # create a new colum for months
    df['Month'] = df['Buchungstag'].dt.strftime('%b')

    # create a new column for years
    df['Year'] = df['Buchungstag'].dt.strftime('%Y')

    # remove raw data file
    os.remove(filename)

    return df


def save_df(df: pd.DataFrame):
    # if cuentas_full.csv exists then append values to it without header and indexes
    # esle create a new one
    if os.path.isfile('cuentas_full.csv'):
        df.to_csv('cuentas_full.csv', mode='a', header=False, index=False)
    else:
        df.to_csv('cuentas_full.csv', index=False)
