import asyncio
from datetime import datetime
import dollar_ as dollar
import betano_ as betano
import pandas as pd
import requests

start_time = datetime.now()
#Dados telegram
TOKEN = "5620155598:AAECYDQbpOLE9rcgVFUZ3ZoUkcNjnYSXQ_w"
chat_id = "739396029"

cotacoes_betano = betano.Betano().filtraMercados(asyncio.run(betano.Betano().getCotacoes(betano.Betano().getJogos())))
pd_cotacoes_betano = pd.json_normalize(cotacoes_betano)
pd_cotacoes_betano.to_excel("cotacoes_betano.xlsx")

cotacoes_dollar = dollar.Dollar().filtraMercados(asyncio.run(dollar.Dollar().getCotacoes(dollar.Dollar().getJogos())))
pd_cotacoes_dollar = dollar.Dollar().normalizeDollar(pd.json_normalize(cotacoes_dollar))
pd_cotacoes_dollar.to_excel("cotacoes_dollar.xlsx")

m = pd.merge(pd_cotacoes_betano, pd_cotacoes_dollar, how='inner', on=['chave', 'mercado'])

range_over = 1/m['odds_betano']
range_under = 1/m['odds_dollar']
m['aposta_betano'] = (range_over/(range_over + range_under))*100
m['aposta_dollar'] = (range_under/(range_over + range_under))*100
m['retorno_percentual'] = (m['aposta_betano']*m['odds_betano'])-100
m_tomail = m[['casa_x', 'fora_x', 'chave', 'inicio_x', 'mercado', 'odds_betano', 'odds_dollar', 'aposta_betano', 'aposta_dollar', 'retorno_percentual']]
filter_positive = m_tomail[(m_tomail['retorno_percentual'] >= 0.01)]
m_tomail = m_tomail.sort_values(by=['retorno_percentual'], ascending=False)

#m_tomail.to_excel("comuns.xlsx")


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

print("Enviando logs no Telegram")
end_time = datetime.now()
msg_log = ''
msg_log = '*FRANGO iLOGs*\n'
msg_log = f"{msg_log}*Inicio: *{start_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
msg_log = f"{msg_log}*Fim: *{end_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
msg_log = f"{msg_log}*Duração: *{format(end_time - start_time)}\n"
msg_log = f"{msg_log}*Mercados Betano: *{str(len(cotacoes_betano))}\n"
msg_log = f"{msg_log}*Mercados Dollar: *{str(len(cotacoes_dollar))}\n"
msg_log = f"{msg_log}*Comu  m: *{str(len(m_tomail))}\n"
msg_log = f"{msg_log}*>=1: *{str(len(filter_positive))}\n"
url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id=-1001628925345&text={msg_log}&parse_mode=Markdown"
requests.get(url)
