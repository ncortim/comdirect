import inquirer
from categories import categories
from typing import Callable


def dictionary_keys_to_list(categories: dict) -> list:
    """gets keys in a dictionary and returns them in a list

    Args:
        categories (dict): a dictionary

    Returns:
        list: a list with input dictionary keys
    """

    first_categories = list()

    for i in categories:
        first_categories.append(i)

    return first_categories


def prompt_list_input(key_value: str, message: str, choices: list) -> str:
    """aks users in a CLI to choose for a given option

    Args:
        key_value (str): key name under wich users response will be stored
        message (str): message to user
        choices (list): list of options for user to pick

    Returns:
        str: chosen option
    """
    questions = [inquirer.List(
        key_value,
        message=message,
        choices=choices,
    )]
    answers = inquirer.prompt(questions)

    return answers[key_value]


def prompt_text_input(key_value: str, message: str,
                      validation: Callable) -> str:
    """asks user in a CLI to input a value

    Args:
        key_value (str): key name under which user's response will be stored
        message (str): message to user
        validation (Callable): function to validate user's input

    Returns:
        str: user's input value
    """
    questions = [
        inquirer.Text(
            key_value,
            message=message,
            validate=validation,
        )
    ]
    answers = inquirer.prompt(questions)

    return answers[key_value]

def ask_for_category_and_subcategory(message: str, first_categories: list) -> str:
    """prompt for category and subcategory selection.

    Args:
        message (str): question ansked for obtaining category
        first_categories (list): list of first categories

    Returns:
        str: _description_
    """
    category = prompt_list_input(key_value='category',
                                         message=message,
                                         choices=first_categories)

    subcategories = ['cancel']
    subcategories.extend(categories[category])

    subcategory = prompt_list_input(key_value='subcategory',
                                            message=message,
                                            choices=subcategories)
    
    return category, subcategory
  
def get_key_by_value(dictionary: dict, value_to_find: str) -> str:
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
