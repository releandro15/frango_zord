import asyncio
import time

from py._path.svnwc import cache

import dollar as dollar
import betano as betano
import pandas as pd
import win32com.client
import requests
import unidecode

start_time = time.time()
#Dados telegram
TOKEN = "5620155598:AAECYDQbpOLE9rcgVFUZ3ZoUkcNjnYSXQ_w"
chat_id = "-1001845830961"


mensage = ''
mensage = f"Comecei a executar novamente"
url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensage}&parse_mode=Markdown"
#requests.get(url)


"""
saldo_dollar = dollar.Dollar().getSaldo()
saldo_betano = betano.Betano().getSaldo()
#print('Saldo Dollar: '+str(saldo_dollar))
#print('Saldo Betamp: '+str(saldo_betano))
casa_menor_saldo = ''
menor_saldo = 0

if(saldo_betano<=saldo_dollar):
    casa_menor_saldo = 'betano'
    menor_saldo = saldo_betano
else:
    casa_menor_saldo = 'dollar'
    menor_saldo = saldo_dollar

"""

cotacoes_betano = betano.Betano().getCotacoes()
#start_time = time.time()
#cotacoes_betano = betano.Betano().getDemaisMercados(cotacoes_betano)
cotacoes_betano = asyncio.run(betano.Betano().getDemaisMercadoos(cotacoes_betano))
#end_time = time.time()
pd_cotacoes_betano = pd.json_normalize(cotacoes_betano)
pd_cotacoes_betano = pd_cotacoes_betano.drop_duplicates(subset=['chave_jogo'])

cotacoes_dollar = dollar.Dollar().getCotacoes()
#cotacoes_dollar = dollar.Dollar().getDemaisMercados(cotacoes_dollar)
cotacoes_dollar = asyncio.run(dollar.Dollar().getDemaisMercadoos(cotacoes_dollar))
pd_cotacoes_dollar = pd.json_normalize(cotacoes_dollar)

pd_cotacoes_dollar.to_excel("output.xlsx")

print("Nomalizando nomes Dollar")
pd_normalize_teams = pd.read_excel(r'C:\Users\ran_l\OneDrive\Pessoal\Pense e Enriqueça\Cotações\Nomalize.xlsm', sheet_name='Dollar')

#Novo método de normalização de nomes
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

pd_cotacoes_dollar = m[['id', 'home_team', 'away_team', 'chave_jogo', 'start_date', 'tipo_dollar', 'odds_dollar']]


m = pd.merge(pd_cotacoes_betano, pd_cotacoes_dollar, how='inner', on='chave_jogo')

#m['odds_goals_under'] = 2.5
range_over = 1/m['odds_betano']
range_under = 1/m['odds_dollar']
m['aposta_betano'] = (range_over/(range_over + range_under))*100
m['aposta_dollar'] = (range_under/(range_over + range_under))*100
m['retorno_percentual'] = (m['aposta_betano']*m['odds_betano'])-100
m_tomail = m[['home_team_x', 'away_team_x', 'chave_jogo', 'start_date', 'tipo_betano', 'odds_betano', 'odds_dollar', 'aposta_betano', 'aposta_dollar', 'retorno_percentual']]
filter_positive = m_tomail[(m_tomail['retorno_percentual'] > 0)]
m_tomail = m_tomail.sort_values(by=['retorno_percentual'], ascending=False)


print("Enviando e-mail")
outlook = win32com.client.Dispatch('outlook.application')
mail = outlook.CreateItem(0)

body = '<h3>Segue as cotações com retornos</h3>'+m_tomail.to_html()+'<br/><p>Segue as cotações da betano</p>'+pd_cotacoes_betano.to_html()+'<br/><p>Segue as cotações da dollar</p>'+pd_cotacoes_dollar.to_html()

mail.To = 'releandro15@gmail.com'
mail.Subject = 'Cotações Teste 1.5'
mail.HTMLBody = body
mail.CC = 'ga.leandro.ma@gmail.com'
mail.Send()


mensage = f"Terminei a execução, se deu algum positivo vc vai receber abaixo"
url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensage}&parse_mode=Markdown"
#requests.get(url)

print("Enviando Telegram")
if (len(filter_positive.index)>0):
    filter_positive.to_excel("cotacoes_retorno.xlsx")
    for index, row in filter_positive.iterrows():
        mensage = ''
        url = ''
        chave_msg = f"{row['chave_jogo']}|{row['start_date']}|{round(row['retorno_percentual'], 2)};\n"
        f = open("jogos.txt", "r")
        if chave_msg in f.read():
            mensage = f"{mensage}*{row['home_team_x']} x {row['away_team_x']}* \n"
            mensage = f"{mensage}{row['start_date']}\n\n"
            mensage = f"{mensage}*Jogo já enviado*"
            url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensage}&parse_mode=Markdown"
            #requests.get(url)
        else:
            mensage = '🔥 *ACHEI UMA APOSTA* 🔥\n\n'
            mensage = f"{mensage}*{row['home_team_x']} x {row['away_team_x']}* \n"
            mensage = f"{mensage}{row['start_date']}\n\n"
            mensage = f"{mensage}*Mercado: *{row['tipo_betano'].replace('Sim', '')}\n\n"
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


        """
        message_bytes = mensage.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')
        print(base64_message)
        """
else:
    mensage = "😞 Triste! \n" \
              "Garimpei tudo, mas não achei nenhum jogo com retorno positivo.\n" \
              "Enviei no e-mail tudo o que achei, dê um confere lá.\n" \
              "Daqui 30 minutos tento novamente. Até mais! 👋"


pd_times_betano = pd.read_excel('betano.xlsx', sheet_name='Sheet1')
times_casa_betano = pd_cotacoes_betano.rename(columns={'home_team': 'betano'})['betano']
times_fora_betano = pd_cotacoes_betano.rename(columns={'away_team': 'betano'})['betano']

pd_times_betano = pd.concat([times_casa_betano, times_fora_betano], ignore_index=False)
pd_times_betano = pd_times_betano.drop_duplicates()
pd_times_betano.to_excel("betano.xlsx", index=False)

pd_times_dollar = pd.read_excel('dollar.xlsx', sheet_name='Sheet1')
times_casa_dollar = pd_cotacoes_dollar.rename(columns={'home_team': 'dollar'})['dollar']
times_fora_dollar = pd_cotacoes_dollar.rename(columns={'away_team': 'dollar'})['dollar']

pd_times_dollar = pd.concat([times_casa_dollar, times_fora_dollar], ignore_index=False)
pd_times_dollar = pd_times_dollar.drop_duplicates()
pd_times_dollar.to_excel("dollar.xlsx", index=False)

"""
print("Calculando aposta")
if(m_tomail.iloc[0]['retorno_percentual'] > 0):
    mensagem = "*Atenção*\n Outro encontrado! Olhe no e-mail"
    url = f" https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={mensagem}&parse_mode=Markdown"
    requests.get(url)

    if(casa_menor_saldo=='dollar'):
        aposta_dollar = menor_saldo
        aposta_betano = (menor_saldo * m_tomail.iloc[0]['aposta_betano'])/m_tomail.iloc[0]['aposta_dollar']
    else:
        aposta_betano = menor_saldo
        aposta_dollar = (menor_saldo * m_tomail.iloc[0]['aposta_dollar'])/m_tomail.iloc[0]['aposta_betano']

    print('Valor aposta Dollar: '+str(aposta_dollar))
    print('Valor aposta Betano: '+str(aposta_betano))

    outlook = win32com.client.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)

    mail.To = 'releandro15@gmail.com'
    mail.Subject = 'Apostar agora'
    mail.HTMLBody = '<h3>Aposta Betano</h3>' + str(round(aposta_betano, 2)) + '<h3>Aposta Dollar</h3>' + str(round(aposta_dollar, 2)) + '<br/><h3>Segue detalhes da aposta</h3>' + pd.DataFrame(m_tomail.iloc[0]).to_html()
    #mail.CC = 'ga.leandro.ma@gmail.com'
    mail.Send()
"""

end_time = time.time()
print("--- %s seconds ---" % (end_time - start_time))

#m.to_excel("output.xlsx")





