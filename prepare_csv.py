from helpers import prompt_list_input, dictionary_keys_to_list
import pandas as pd
import glob
import os
import re
from categories import categories
from typing import Union


def get_file_name(accounting_filename: bool = False) -> Union[str, bool]:
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


def create_dataframe(filename: str) -> pd.DataFrame:
    """Given a csv file with transactions (comdirect bank),
    it formats and returns a pandas dataframe

    Args:
        filename (str): filename placed in directory ./inputs

    Returns:
        pd.DataFrame: formatted pandas dataframe ready for further analysis
    """
    # read csv file, skip header and footer and encoding umlaut
    # create a dataframe
    df = pd.read_csv(filename,
                     encoding="ISO-8859-1",
                     sep=';',
                     skiprows=4,
                     skipfooter=4,
                     engine='python')

    # change format euro decimals and thousands
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(".", "", regex=True)
    df["Umsatz in EUR"] = df["Umsatz in EUR"].str.replace(
        ",", ".", regex=True).astype(float)

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
                df.loc[idx, 'Auftraggeber'] = detailed_purchaser
            else:
                df.loc[idx, 'Auftraggeber'] = purchaser
        # i.split(':', 1)[1].split(':', 1)[0].split('Buchungstext')[0].strip()
        elif description == ' Buchungstext':
            df.loc[idx, 'Auftraggeber'] = re.compile(
                r'\d{4}-\d{2}-\d{2}').split(i)[0].split(':', 1)[1].strip()
        elif description == 'Empfänger':
            df.loc[idx, 'Auftraggeber'] = re.compile(r'Kto').split(i)[0].split(
                ':', 1)[1].strip()

    # extract buchungstext from purchase
    for idx, i in enumerate(df['Buchungstext']):
        description = i.split(':', 2)[-1].strip()
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

    # create a new colum for months
    df['Month'] = df['Buchungstag'].dt.strftime('%b')

    # create a new column for years
    df['Year'] = df['Buchungstag'].dt.strftime('%Y')

    return df


def create_dataframe_accounting_csv(filename: str) -> pd.DataFrame:
    """creates a pandas dataframe from accounting.csv file. This file
    is located in ./outputs directory and contains the records of all 
    transactions

    Args:
        filename (str): path to file

    Returns:
        pd.DataFrame: pandas dataframe
    """

    df = pd.read_csv(filename, encoding="ISO-8859-1", sep=',')

    return df


def save_df_to_csv(df: pd.DataFrame, filename: str) -> None:
    """saves formatted pandas dataframe to csv file. Output file is called
    accounting.csv and is located in ./outputs directory

    Args:
        df (pd.DataFrame): pandas dataframes
        filename (str): path to filename
    """
    # if accounting.csv exists then append values to it without header and indexes
    # esle create a new one
    if os.path.isfile('./outputs/accounting.csv'):
        df.to_csv('./outputs/accounting.csv',
                  mode='a',
                  header=False,
                  index=False)
    else:
        df.to_csv('./outputs/accounting.csv', index=False)


def categorize_purchases(new_df: pd.DataFrame,
                         accounting_df: pd.DataFrame = None) -> pd.DataFrame:
    """give a new dataframe as input, it guides the user to categorize new entries.
    Categorization occurs through asking in the command line interface. Repeated entries
    will be categorized automatically

    Args:
        new_df (pd.DataFrame): pandas dataframe with new data
        accounting_df (pd.DataFrame, optional): pandas dataframe with all existing 
        transactions (historical data). Defaults to None.

    Raises:
        ValueError: if accounting_df is not given

    Returns:
        pd.DataFrame: dataframe with new categorized entries
    """

    first_categories = dictionary_keys_to_list(categories=categories)

    for idx, i in enumerate(new_df["Auftraggeber"]):
        # check in value already present in categories dict
        try:
            if i in accounting_df['Auftraggeber'].values:
                match_indexes = accounting_df[accounting_df['Auftraggeber'] ==
                                              i].index.values
                repeated_category = accounting_df.at[match_indexes[0],
                                                     'Kategorie']
                repeated_subcategory = accounting_df.at[match_indexes[0],
                                                        'Subkategorie']
                new_df.at[idx, 'Kategorie'] = repeated_category
                new_df.at[idx, 'Subkategorie'] = repeated_subcategory
            else:
                raise ValueError
        except (TypeError, ValueError):
            euro = new_df.at[idx, 'Umsatz in EUR']
            message = f'Select category: {i}  EURO: {euro}?'

            category = prompt_list_input(key_value='category',
                                         message=message,
                                         choices=first_categories)

            new_df.at[idx, 'Kategorie'] = category

            subcategory = prompt_list_input(key_value='subcategory',
                                            message=message,
                                            choices=categories[category])
            new_df.at[idx, 'Subkategorie'] = subcategory

    return new_df

