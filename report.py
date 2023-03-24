import pandas as pd 
import os

os.system('cp cuentas_full.csv cuentas_full_report.csv ') 
df = pd.read_csv("cuentas_full_report.csv")



def substract_caja_chica(month: int, dafr: pd.DataFrame) -> None:
    value_caja_chica = dafr.loc[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month), 'Umsatz in EUR']
    value_receipts = dafr.loc[(dafr['Buchungstext'] == 'receipts') & (dafr['Month'] == month), 'Umsatz in EUR'].sum()
    
    try:
        final_value = abs(value_caja_chica.iloc[0]) - abs(value_receipts)
        index = dafr.index[(dafr['Category'] == 'caja chica') & (dafr['Month'] == month)]
        dafr['Umsatz in EUR'][index] = final_value
    except IndexError:
        # print('no values for month ' + month)
        pass



months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# months = df['Month'].values.tolist()
# months_unique = set(months)

# df['Month'] = pd.Categorical(df['Month'], categories=months, ordered=True)
df['Buchungstag'] = pd.to_datetime(df['Buchungstag'], dayfirst=True)
df['Year'] = df['Year'].astype(str)


# sum_all_cajas_chicas = df.loc[(df['Category'] == 'caja chica') & (df['Month'] == 'Sep'), 'Umsatz in EUR'].sum()
# indexes_all_cajas_chicas = df.loc[(df['Category'] == 'caja chica') & (df['Month'] == 'Sep'), 'Umsatz in EUR'].index
# df.iloc[indexes_all_cajas_chicas[0], df.columns.get_loc('Umsatz in EUR')] = sum_all_cajas_chicas


# for idx, i in enumerate(indexes_all_cajas_chicas):
#     if idx == 0:
#         pass
#     else:
#         df = df.drop(i)

# for i in months:
#     substract_caja_chica(i, df)

for i in months:
    sum_all_cajas_chicas = df.loc[(df['Category'] == 'caja chica') & (df['Month'] == i), 'Umsatz in EUR'].sum()
    indexes_all_cajas_chicas = df.loc[(df['Category'] == 'caja chica') & (df['Month'] == i), 'Umsatz in EUR'].index
    try:
        df.iloc[indexes_all_cajas_chicas[0], df.columns.get_loc('Umsatz in EUR')] = sum_all_cajas_chicas
    except IndexError:
        pass
    for idx, j in enumerate(indexes_all_cajas_chicas):
        if idx == 0:
            pass
        else:
            df = df.drop(j)
    substract_caja_chica(i, df)

df['Month'] = pd.to_datetime(df.Month, format='%b', errors='coerce').dt.month


# df['Total'] = df.sum(axis=1)

df1 = df.groupby(['Category', 'Month', 'Year']).sum()
df1 = df1.unstack().unstack(fill_value=0)
# df1 = df1.unstack()
# df1 = df1.reset_index()

df1 = df1.fillna(0)

# # define total row with summed up values
df1['Total'] = df1.sum(axis=1)

# # define total row with 
# summed up values
df1.loc['Total'] = df1.sum()
# df1.first()
df1