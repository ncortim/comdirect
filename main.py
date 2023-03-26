from prepare_csv import create_dataframe, create_dataframe_accounting_csv, categorize_purchases, save_df_to_csv, get_file_name
from add_receipts import cash_receipts
import os
import shutil


def main():
    new_filename = get_file_name()

    if new_filename:

        accounting_file = get_file_name(accounting_filename=True)

        new_df = create_dataframe(filename=new_filename)

        try:
            new_df = create_dataframe(filename=new_filename)
            accounting_df = create_dataframe_accounting_csv(accounting_file)
        except ValueError:
            print("""
                ##############################################################################
                ##############################################################################
                accounting.csv file does not exist yet in ./outputs directory. Creating file...
                ##############################################################################
                ##############################################################################
            """)

        try:
            new_df = categorize_purchases(new_df, accounting_df)
        except NameError:
            new_df = categorize_purchases(new_df)

        save_df_to_csv(new_df, new_filename)

        cash_receipts()
    else:
        cash_receipts()

    try:
        shutil.copy(new_filename, './raw_files/')
        os.remove(new_filename)
    except TypeError:
        pass

    print("""
    ##############################################################################
    ##############################################################################
    Thanks for using this tool, see you next time
    ##############################################################################
    ##############################################################################
    """)


if __name__ == "__main__":
    main()
