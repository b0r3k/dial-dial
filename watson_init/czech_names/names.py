import pandas as pd
import json

# Data from archived files from 22.9.2018 version of MVČR website https://www.mvcr.cz/clanek/cetnost-jmen-a-prijmeni.aspx
# https://web.archive.org/web/20180922062314/https://www.mvcr.cz/clanek/cetnost-jmen-a-prijmeni.aspx

# Data look like (for name, in surname "JMÉNO" is replaced by "PŘÍJMENÍ"):
#                  JMÉNO  0  1899  1900  1901  1902  1903  1904  1905  1906  1907  ...  2008  2009  2010  2011  2012  2013  2014  2015  2016  2017  3000
# 0                 A-MI  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     1
# 1                A-RIA  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     1
# 2          AADAM SAMER  0     0     0     0     0     0     0     0     0     0  ...     1     0     0     0     0     0     0     0     0     0     1
# 3                AADIV  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     1     0     1
# 4                AAGOT  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     1
# ...                ... ..   ...   ...   ...   ...   ...   ...   ...   ...   ...  ...   ...   ...   ...   ...   ...   ...   ...   ...   ...   ...   ...
# 64994         VASILIJE  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     3
# 64995         VASILIKA  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     6
# 64996         VASILIKI  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0    39
# 64997  VASILIKI-HELENA  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     1
# 64998  VASILIKI-ZUZANA  0     0     0     0     0     0     0     0     0     0  ...     0     0     0     0     0     0     0     0     0     0     1

# # Convert surname data to csv for better handling
# df_dict = pd.read_excel('surnames-freq.xls', sheet_name=None)
# frames = df_dict.values()
# df = pd.concat(frames)
# df.to_csv('surnames-freq.csv', encoding='utf-8')

# # Convert name data to csv for better handling
# df_dict = pd.read_excel('names-freq.xls', sheet_name=None)
# frames = df_dict.values()
# df = pd.concat(frames)
# df.to_csv('names-freq.csv', encoding='utf-8')


# Find names with 2000 and more occurances
common_names = []
df_names = pd.read_csv('names-freq.csv')
df_names.sort_values(by=[df_names.columns[-1]], inplace=True, ascending=False, ignore_index=True)
for i in range(1, 1000):
    if (df_names.loc[i, df_names.columns[-1]]) < 500:
        break
    else:
        common_names.append(df_names.loc[i, "JMÉNO"].lower())
print(common_names)
print(len(common_names))

# Find surnames with 2000 and more occurances
common_surnames = []
df_surnames = pd.read_csv('surnames-freq.csv')
df_surnames.sort_values(by=[df_surnames.columns[-1]], inplace=True, ascending=False, ignore_index=True)
for i in range(1, 1000):
    if (df_surnames.loc[i, df_surnames.columns[-1]]) < 500:
        break
    else:
        common_surnames.append(df_surnames.loc[i, "PŘÍJMENÍ"].lower())
print(common_surnames)
print(len(common_surnames))

# Dump all the names to json
with open('names.json', 'w+', encoding='utf-8') as file:
    json.dump(common_names+common_surnames, file, indent=1, ensure_ascii=False)