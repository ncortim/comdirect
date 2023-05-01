from prepare_csv import get_file_name
import pandas as pd

name = get_file_name(accounting_filename=True)


df = pd.read_csv(filepath_or_buffer=name)

df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)
mapping_types_conversion = {
    'Vorgang': 'category',
    'Buchungstext': 'string',
    'Auftraggeber': 'string',
    'Beschreibung': 'string',
    'Kategorie': 'category',
    'Subkategorie': 'category',
    'Month': 'category',
    'Year': 'category'
}
df = df.astype(mapping_types_conversion)
# create a new colum for months
# df['Month'].astype('datetime64[ns]')
# df['Month'] = df['Buchungstag'].dt.strftime('%b')
# create a new column for years
# df['Year'] = df['Buchungstag'].dt.strftime('%Y')



# months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


df['Month'] = pd.to_datetime(df.Month, format='%b', errors='coerce').dt.month
df1 = df.groupby(['Kategorie', 'Month', 'Year']).sum()
df1 = df.groupby(['Subkategorie', 'Month', 'Year']).sum()
df1 = df1.unstack().unstack(fill_value=0)
# df1 = df1.unstack()
# df1 = df1.reset_index()

df1 = df1.fillna(0)

# define total row with summed up values
df1['Total'] = df1.sum(axis=1)

# define total row with 
# summed up values
df1.loc['Total'] = df1.sum()
# df1.first()
# df1
df1.to_html('report.html')