import pandas as pd
import unidecode
import unidecode as unidecode

print("Nomalizando nomes Dollar")
pd_cotacoes_dollar = pd.read_excel(r'cotacoes_dollar.xlsx', sheet_name='Sheet1')
pd_normalize_teams = pd.read_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\Nomalize.xlsm', sheet_name='Dollar')

"""
for index_cotacoes, row_cotacoes in pd_cotacoes_dollar.iterrows():
    altera_home = ''
    altera_away = ''
    for index_normalize, row_normalize in pd_normalize_teams.iterrows():
        if row_cotacoes['home_team'] == row_normalize['Dollar'] and row_normalize['Betano'] != '':
            pd_cotacoes_dollar.iloc[index_cotacoes, pd_cotacoes_dollar.columns.get_loc('home_team')] = row_normalize['Betano']
            altera_home = row_normalize['Betano']
        if row_cotacoes['away_team'] == row_normalize['Dollar'] and row_normalize['Betano'] != '':
            pd_cotacoes_dollar.iloc[index_cotacoes, pd_cotacoes_dollar.columns.get_loc('away_team')] = row_normalize['Betano']
            altera_away = row_normalize['Betano']
        pd_cotacoes_dollar.iloc[index_cotacoes, pd_cotacoes_dollar.columns.get_loc('chave_jogo')] = (unidecode.unidecode(
            (altera_home if altera_home != '' else row_cotacoes['home_team'])[:10] + '_X_' +
            (altera_away if altera_away != '' else row_cotacoes['away_team'])[:10])).replace(' ', '').replace(
                                    '-', '').replace('.', '') + '#' + row_cotacoes['chave_jogo'].split('#')[1]

"""
m = pd.merge(pd_cotacoes_dollar, pd_normalize_teams, how='left', left_on=['home_team'], right_on=['Dollar'])
for index_m, row_m in m.iterrows():
    if pd.isna(row_m['Betano']):
        m.iloc[index_m, m.columns.get_loc('Betano')] = row_m['home_team']
m = m.drop(columns=['home_team', 'Dollar', 'Confere']).rename(columns={'Betano': 'home_team'})

m = pd.merge(m, pd_normalize_teams, how='left', left_on=['away_team'], right_on=['Dollar'])
for index_m, row_m in m.iterrows():
    if pd.isna(row_m['Betano']):
        m.iloc[index_m, m.columns.get_loc('Betano')] = row_m['away_team']
m = m.drop(columns=['away_team', 'Dollar', 'Confere']).rename(columns={'Betano': 'away_team'})

for index_m, row_m in m.iterrows():
    m.iloc[index_m, m.columns.get_loc('chave_jogo')] = (unidecode.unidecode(
        row_m['home_team'][:10] + '_X_' +
        row_m['away_team'][:10])).replace(' ', '').replace(
        '-', '').replace('.', '') + '#' + row_m['chave_jogo'].split('#')[1]

m = m[['id', 'home_team', 'away_team', 'chave_jogo', 'start_date', 'tipo_dollar', 'odds_dollar']]

m.to_excel("output.xlsx")