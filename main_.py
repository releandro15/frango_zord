import asyncio
from datetime import datetime
import time
import dollar_ as dollar
import betano_ as betano
import pandas as pd
import requests
import unidecode

start_time = datetime.now()
#Dados telegram
TOKEN = "5620155598:AAECYDQbpOLE9rcgVFUZ3ZoUkcNjnYSXQ_w"
chat_id = "-1001845830961"

cotacoes_betano = betano.Betano().filtraMercados(asyncio.run(betano.Betano().getCotacoes(betano.Betano().getJogos())))
pd_cotacoes_betano = pd.json_normalize(cotacoes_betano)

cotacoes_dollar = dollar.Dollar().filtraMercados(asyncio.run(dollar.Dollar().getCotacoes(dollar.Dollar().getJogos())))
pd_cotacoes_dollar = pd.json_normalize(cotacoes_dollar)

print("Nomalizando nomes Dollar")
pd_normalize_teams = pd.read_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\Nomalize.xlsm', sheet_name='Dollar')

#Novo método de normalização de nomes
m = pd.merge(pd_cotacoes_dollar, pd_normalize_teams, how='left', left_on=['casa'], right_on=['Dollar'])
for index_m, row_m in m.iterrows():
    if pd.isna(row_m['Betano']):
        m.iloc[index_m, m.columns.get_loc('Betano')] = row_m['casa']
m = m.drop(columns=['casa', 'Dollar', 'Confere']).rename(columns={'Betano': 'casa'})

m = pd.merge(m, pd_normalize_teams, how='left', left_on=['fora'], right_on=['Dollar'])
for index_m, row_m in m.iterrows():
    if pd.isna(row_m['Betano']):
        m.iloc[index_m, m.columns.get_loc('Betano')] = row_m['fora']
m = m.drop(columns=['fora', 'Dollar', 'Confere']).rename(columns={'Betano': 'fora'})

for index_m, row_m in m.iterrows():
    m.iloc[index_m, m.columns.get_loc('chave')] = (unidecode.unidecode(row_m['casa'] + ' x ' +row_m['fora']))

pd_cotacoes_dollar = m[['casa', 'fora', 'chave', 'inicio', 'mercado', 'odds_dollar']]


m = pd.merge(pd_cotacoes_betano, pd_cotacoes_dollar, how='inner', on=['chave', 'mercado'])

range_over = 1/m['odds_betano']
range_under = 1/m['odds_dollar']
m['aposta_betano'] = (range_over/(range_over + range_under))*100
m['aposta_dollar'] = (range_under/(range_over + range_under))*100
m['retorno_percentual'] = (m['aposta_betano']*m['odds_betano'])-100
m_tomail = m[['casa_x', 'fora_x', 'chave', 'inicio_x', 'mercado', 'odds_betano', 'odds_dollar', 'aposta_betano', 'aposta_dollar', 'retorno_percentual']]
filter_positive = m_tomail[(m_tomail['retorno_percentual'] >= 1)]
m_tomail = m_tomail.sort_values(by=['retorno_percentual'], ascending=False)


print("Enviando resultados no Telegram")
if (len(filter_positive.index)>0):
    filter_positive.to_excel("cotacoes_retorno.xlsx")
    for index, row in filter_positive.iterrows():
        mensage = ''
        url = ''
        chave_msg = f"{row['chave']}|{row['inicio_x']}|{round(row['retorno_percentual'], 2)};\n"
        f = open("jogos.txt", "r")
        if chave_msg not in f.read():
            mensage = '🔥 *ACHEI UMA APOSTA* 🔥\n\n'
            mensage = f"{mensage}*{row['casa_x']} x {row['fora_x']}* \n"
            mensage = f"{mensage}{row['inicio_x']}\n\n"
            mensage = f"{mensage}*Mercado: *{row['mercado']}\n\n"
            mensage = f"{mensage}*Odds Betano: *{round(row['odds_betano'], 2)}\n"
            mensage = f"{mensage}*Odds Dollar: *{round(row['odds_dollar'], 2)}\n\n"
            mensage = f"{mensage}*Aposta Betano: *{round(row['aposta_betano'], 2)}\n"
            mensage = f"{mensage}*Aposta Dollar: *{round(row['aposta_dollar'], 2)}\n\n"
            mensage = f"{mensage}*🤑 Retorno: *{round(row['retorno_percentual'], 2)}\n"
            url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensage}&parse_mode=Markdown"
            requests.get(url)
            f = open("jogos.txt", "a")
            f.write(chave_msg)
            f.close()

end_time = datetime.now()
msg_log = ''
msg_log = '*FRANGO LOGs*\n'
msg_log = f"{msg_log}*Inicio: *{start_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
msg_log = f"{msg_log}*Fim: *{end_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
msg_log = f"{msg_log}*Duração: *{format(end_time - start_time)}\n"
url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=-1001628925345&text={msg_log}&parse_mode=Markdown"
requests.get(url)



