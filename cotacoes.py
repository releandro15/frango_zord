import pandas as pd

print("Nomalizando nomes Dollar")
pd_cotacoes_dollar = pd.read_excel(r'cotacoes_dollar.xlsx', sheet_name='Sheet1')
pd_normalize_teams = pd.read_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\Nomalize.xlsm', sheet_name='Dollar')

m = pd.merge(pd_cotacoes_dollar, pd_normalize_teams, how='left', left_on=['home_team'], right_on=['Dollar'])
m = m.drop(columns=['home_team', 'Dollar', 'Confere']).rename(columns={'Betano': 'home_team'})
m = pd.merge(m, pd_normalize_teams, how='left', left_on=['away_team'], right_on=['Dollar'])
m = m.drop(columns=['away_team', 'Dollar', 'Confere']).rename(columns={'Betano': 'away_team'})

m.to_excel("output.xlsx")