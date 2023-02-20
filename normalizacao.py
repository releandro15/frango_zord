import pandas as pd

pd_jogos_dollar = pd.read_excel(r'cotacoes_dollar.xlsx', sheet_name='Sheet1').drop_duplicates(subset='chave')[['casa', 'fora']]
pd_jogos_betano = pd.read_excel(r'cotacoes_betano.xlsx', sheet_name='Sheet1').drop_duplicates(subset='chave')[['casa', 'fora']]
pd_normalize_teams = pd.read_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\newNomalize.xlsx', sheet_name='Dollar')

pd_times_fora = pd.merge(pd_jogos_dollar, pd_jogos_betano, on=['casa'])[['fora_x', 'fora_y']]
pd_times_casa = pd.merge(pd_jogos_dollar, pd_jogos_betano, on=['fora'])[['casa_x', 'casa_y']]

pd_times_fora.columns = ['Dollar', 'Betano']
pd_times_casa.columns = ['Dollar', 'Betano']

pd_times = pd.concat([pd_times_fora, pd_times_casa])

pd_times['Confere'] = pd_times['Dollar']==pd_times['Betano']

pd_times = pd_times[(pd_times['Confere'] == False)]

pd_times.to_excel("tst-norms.xlsx")

print("Normalizado "+str(len(pd_times)))

pd_normalize_teams = pd.concat([pd_normalize_teams, pd_times])

pd_normalize_teams.to_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\newNomalize.xlsx', sheet_name='Dollar', index=False)

