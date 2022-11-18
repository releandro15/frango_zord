import asyncio
import http.client
import json

import aiohttp
import requests
import unidecode
from selenium import webdriver
from sockshandler import merge_dict
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd



class Dollar:

    @classmethod
    def getCotacoes(dia):
        jogos = []
        odds_goals_under = 0

        conn = http.client.HTTPSConnection("slark.ngx.bet")
        payload = ''
        headers = {
            'Origin': 'https://www.dollar.bet'
        }
        for i in range(2):
            dta = (datetime.strptime(datetime.today().strftime('%m/%d/%Y'), '%m/%d/%Y') + timedelta(
                days=i)).strftime('%m/%d/%Y')
            print(f"Buscando jogos na Dollar do dia {dta}")
            conn.request("GET", "/event?type=SOCCER&date=" + dta, payload, headers)
            res = conn.getresponse()
            data = res.read()
            data = json.loads(data.decode("utf-8"))

            for d in data:
                    all_odds = d['odds']['full_time']

                    for odds in all_odds.keys():
                        if odds == 'goals_over_under':
                            arr = all_odds['goals_over_under']
                            for element in arr:
                                if element['name'] == "2.5" and element['header'] == 'UNDER':
                                    odds_goals_under = element['value']
                            jogo_goals_over_under = {
                                "id": d['_id'],
                                "home_team": d['home_team'],
                                "away_team": d['away_team'],
                                "chave_jogo": (
                                    unidecode.unidecode(
                                        d['home_team'][:10] + '_X_' + d['away_team'][:10])).replace(' ',
                                                                                                          '').replace(
                                    '-', '').replace('.', '') + '#2.5',
                                "start_date": (datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%f%z') + timedelta(
                                    hours=-4)).strftime("%d/%m/%Y %H:%M"),
                                "tipo_dollar": "Gols-2.5",
                                "odds_dollar": odds_goals_under
                            }
                            jogos.append(jogo_goals_over_under)

                        if odds == 'both_teams_to_score_no':
                            jogo_both_teams_to_score_no = {
                                "id": d['_id'],
                                "home_team": d['home_team'],
                                "away_team": d['away_team'],
                                "chave_jogo": (
                                    unidecode.unidecode(
                                        d['home_team'][:10] + '_X_' + d['away_team'][:10])).replace(' ',
                                                                                                          '').replace(
                                    '-', '').replace('.', '') + '#ambas',
                                "start_date": (datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S.%f%z') + timedelta(
                                    hours=-4)).strftime("%d/%m/%Y %H:%M"),
                                "tipo_dollar": "Ambas Marcam Não",
                                "odds_dollar": all_odds['both_teams_to_score_no']['value']
                            }
                            jogos.append(jogo_both_teams_to_score_no)
                    print(f"#Dolar: {d['home_team']} x {d['away_team']}")

        return jogos


    async def getDados(self, session, url):
        headers = {
            'Origin': 'https://www.dollar.bet'
        }
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                print(f"Pegando {data['home_team']} - {data['away_team']}")
                return (data)
        except:
            print('Erro Dollar')

    def getDemaisMercados(self, cotacoes_dollar):
        cotacoes_dollar = pd.json_normalize(cotacoes_dollar).dropna()
        cotacoes_dollar = cotacoes_dollar.drop_duplicates(subset=['id'])
        #cotacoes_dollar['start_date'] = pd.to_datetime(cotacoes_dollar['start_date'], format='%d/%m/%y %H:%M').dt.strftime('%Y-%m-%d %H:%M:%S')
        #cotacoes_dollar = cotacoes_dollar[(cotacoes_dollar['start_date'] >= (datetime.strptime(datetime.today().strftime('%m/%d/%Y'), '%m/%d/%Y') + timedelta(
                #days=0)).strftime('%m/%d/%Y')) & (cotacoes_dollar['start_date'] <= (datetime.strptime(datetime.today().strftime('%m/%d/%Y'), '%m/%d/%Y') + timedelta(
                #days=1)).strftime('%m/%d/%Y'))]

        conn = http.client.HTTPSConnection("slark.ngx.bet")
        headers = {
            'Origin': 'https://www.dollar.bet'
        }
        newData = ''
        jogos = []
        jogo_goals_over_under = ''

        for index, jogo in cotacoes_dollar.iterrows():
            try:
                res = requests.get('https://slark.ngx.bet/event/' + jogo['id'],
                                   headers=headers)
                data = res.json()
                all_odds = data['odds']['first_time']

                print("Pegando jogo "+jogo['home_team']+" x "+jogo['away_team'])

                for odds in all_odds.keys():
                    if odds == 'goals_over_under':
                        arr = all_odds['goals_over_under']
                        for element in arr:
                            if element['name'] == "1.5" and element['header'] == 'UNDER':
                                odds_goals_under = element['value']
                                jogo_goals_over_under = {
                                    "id": jogo['id'],
                                    "home_team": jogo['home_team'],
                                    "away_team": jogo['away_team'],
                                    "chave_jogo": jogo['chave_jogo'].split('#')[0]+"#1.5_1T",
                                    "start_date": jogo['start_date'],
                                    "tipo_dollar": "-1.5 1T",
                                    "odds_dollar": odds_goals_under
                                }
                                jogos.append(jogo_goals_over_under)
            except:
                print("Erro dollar")

        return jogos

    async def getDemaisMercadoos(self, cotacoes_dollar):
        cotacoes_dollar = pd.json_normalize(cotacoes_dollar).drop_duplicates(subset=['id']).dropna()
        cotacoes_dollar['url_dollar'] = 'https://slark.ngx.bet/event/' + cotacoes_dollar['id']
        list_cotacoes_dollar = cotacoes_dollar['url_dollar'].tolist()
        jogos = []

        async with aiohttp.ClientSession() as session:
            tasks = []
            for number in list_cotacoes_dollar:
                url = number
                tasks.append(asyncio.ensure_future(self.getDados(session, url)))

            data = await asyncio.gather(*tasks)

        #markets = data['markets']
        for item in data:
            all_odds = item['odds']['first_time']

            for odds in all_odds.keys():
                if odds == 'goals_over_under':
                    arr = all_odds['goals_over_under']
                    for element in arr:
                        if element['name'] == "1.5" and element['header'] == 'UNDER':
                            odds_goals_under = element['value']
                            jogo_goals_over_under = {
                                "id": item['_id'],
                                "home_team": item['home_team'],
                                "away_team": item['away_team'],
                                "chave_jogo": (
                                    unidecode.unidecode(
                                        item['home_team'][:10] + '_X_' + item['away_team'][:10])).replace(' ',
                                                                                                          '').replace(
                                    '-', '').replace('.', '') + '#2.5',
                                "start_date": (datetime.strptime(item['date'], '%Y-%m-%dT%H:%M:%S.%f%z') + timedelta(
                                    hours=-4)).strftime("%d/%m/%Y %H:%M"),
                                "tipo_dollar": "-1.5 1T",
                                "odds_dollar": odds_goals_under
                            }
                            jogos.append(jogo_goals_over_under)
        return jogos

    def getSaldo(self):
        print('Iniciando captura do saldo da Dollar Bet')
        service = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=service)
        navegador.get("https://www.dollar.bet/home/events-area")
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="menu-top"]/div[1]/div[4]/div/div/button/span').click()
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="mat-input-0"]').send_keys("releandro15")
        navegador.find_element(By.XPATH, '//*[@id="mat-input-1"]').send_keys("10202233+ac")
        navegador.find_element(By.XPATH,
                               '//*[@id="app-component-view"]/app-window-plus2/div/app-home-mobile-plus2/div/div/div/app-events-area-plus2/div/app-events-area-mobile-plus2/mat-drawer-container/mat-drawer[2]/div/app-menu-login-sidebar-mobile-plus2/div/div/div[1]/form/div[2]/button[2]').click()
        time.sleep(2)
        saldo_dollar = (navegador.find_element(By.XPATH,
                                               '//*[@id="app-component-view"]/app-window-plus2/div/app-home-mobile-plus2/div/div/div/app-events-area-plus2/div/app-events-area-mobile-plus2/mat-drawer-container/mat-drawer[2]/div/app-menu-login-sidebar-mobile-plus2/div/div/div/div/div[1]/div[1]/span').text).replace(
            'R$ ', '')
        print('O saldo disponível na Dollar Bet é ' + saldo_dollar)
        navegador.quit()
        return float(saldo_dollar.replace('.', '').replace(',', '.'))

"""
dol = Dollar()
dol.getCotacoes()

# dol.apostar()

with open('data.json', 'w') as f:
    json.dump(dol.getCotacoes(), f)
exit()
"""