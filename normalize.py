import pandas as pd

def similar(str1, str2):
    str1 = str1 + ' ' * (len(str2) - len(str1))
    str2 = str2 + ' ' * (len(str1) - len(str2))
    return sum(1 if i == j else 0
               for i, j in zip(str1, str2)) / float(len(str1))

pd_dollar = pd.read_excel('dollar.xlsx', sheet_name='Sheet1')
pd_betano = pd.read_excel('betano.xlsx', sheet_name='Sheet1')

for index_dollar, row_dollar in pd_dollar.iterrows():
    for index_betano, row_betano in pd_betano.iterrows():
        res = similar(str(row_dollar['dollar']), str(row_betano['betano']))
        if res > 0.70:
            print(f"{row_dollar['dollar']}|{row_betano['betano']}|{str(res)}")
