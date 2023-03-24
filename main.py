from comdirect.prepare_csv import get_file_name, prepare_csv_file, save_df
from comdirect.add_receipts import cashReceipts

def main():
    filename = get_file_name()
    if filename:
        df = prepare_csv_file(filename)
        save_df(df)
        cashReceipts()
    else:
        cashReceipts()
        

if __name__ == "__main__":
    main()
