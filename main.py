from prepare_csv import create_dataframe, create_dataframe_accounting_csv, categorize_purchases, save_df_to_csv, get_file_name
from add_receipts import cash_receipts
import os
import shutil
#from comdirect.prepare_csv import get_file_name, prepare_csv_file, save_df
#from comdirect.add_receipts import cashReceipts


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

        #filename = get_file_name()
        #if filename:
        #    df = prepare_csv_file(filename)
        #    save_df(df)
        cash_receipts()
    else:
        cash_receipts()


    try:
        shutil.copy(new_filename, './raw_files/')
        os.remove(new_filename)
        print("""
            ##############################################################################
            ##############################################################################
            Thanks for using this tool, see you next time
            ##############################################################################
            ##############################################################################
        """)
    except TypeError:
        print("""
            ##############################################################################
            ##############################################################################
            Thanks for using this tool, see you next time
            ##############################################################################
            ##############################################################################
        """)

if __name__ == "__main__":
    main()
