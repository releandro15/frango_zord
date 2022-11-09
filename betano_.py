import http.client
import json
import math
import unidecode
import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time

class Betano:

    @classmethod
    def getCotacoes(cls):
        import requests
        from bs4 import BeautifulSoup
        import json
        import unidecode

        jogos = []

        def make_events_page(events):

            return newData

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
        }

        # Pegando eventos da primeira página
        res = requests.get('https://br.betano.com/sport/futebol/jogos-de-hoje/', headers=headers)
        soup_data = BeautifulSoup(res.text, 'html.parser')
        body = soup_data.find('body')
        scripts = body.findChildren('script')
        first_page = json.loads(scripts[0].text.replace('window["initial_state"]=', ''))
        events_firstpage = first_page['data']['blocks'][0]['events']
        lastId = events_firstpage[len(events_firstpage) - 1]['id']

        for event in events_firstpage:
            newData = ''
            for market in event['markets']:
                if market['name'] == "Total de Gols Mais/Menos":
                    for selection in market['selections']:
                        if selection['name'] == 'Mais de 2.5':
                            odds_goals_over = selection['price']
                            newData = {
                                "id": event['id'],
                                "home_team": event['participants'][0]['name'],
                                "away_team": event['participants'][1]['name'],
                                "chave_jogo": (unidecode.unidecode(
                                    event['participants'][0]['name'][:10] + '_X_' + event['participants'][1]['name'][
                                                                                   :10])).replace(' ', '').replace('-', '').replace('.', ''),
                                "start_time": datetime.datetime.fromtimestamp(int(str(event['startTime'])[:-3])).strftime('%d/%m/%Y %H:%M'),
                                "odds_goals_over": odds_goals_over
                            }
                if newData != "":
                    print("Betano:  " + newData['home_team'] + " x " + newData['away_team'])
                    jogos.append(newData)

        # Percorrendo demais páginas
        i = True
        while i:
            try:
                res = requests.get('https://br.betano.com/api/sport/futebol/jogos-de-hoje/?latestId=' + lastId,
                                   headers=headers)
                data = res.json()
                events_page = data['data']['blocks'][0]['events']
                lastId = events_page[len(events_page) - 1]['id']

                for event in events_page:
                    newData = ''
                    for market in event['markets']:
                        if market['name'] == "Total de Gols Mais/Menos":
                            for selection in market['selections']:
                                if selection['name'] == 'Mais de 2.5':
                                    odds_goals_over = selection['price']
                                    newData = {
                                        "id": event['id'],
                                        "home_team": event['participants'][0]['name'],
                                        "away_team": event['participants'][1]['name'],
                                        "chave_jogo": (unidecode.unidecode(
                                            event['participants'][0]['name'][:10] + '_X_' + event['participants'][1][
                                                                                               'name'][
                                                                                           :10])).replace(' ', '').replace('-', '').replace('.', ''),
                                        "start_time": datetime.datetime.fromtimestamp(int(str(event['startTime'])[:-3])).strftime('%d/%m/%Y %H:%M'),
                                        "odds_goals_over": odds_goals_over
                                    }
                        if newData != "":
                            print("Betano:  " + newData['home_team'] + " x " + newData['away_team'])
                        jogos.append(newData)
            except:
                i = False

        return jogos

    def getSaldo(self):
        print('Iniciando captura do saldo da Betano')
        service = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=service)
        navegador.get("https://br.betano.com/myaccount/login")
        time.sleep(2)
        navegador.find_element(By.XPATH, '//*[@id="username"]').send_keys("releandro15@gmail.com")
        navegador.find_element(By.XPATH, '//*[@id="password"]').send_keys("10202233+ac")
        navegador.find_element(By.XPATH, '//*[@id="app"]/div/main/div/section/div/form/button').click()
        time.sleep(1)
        saldo_betano = (navegador.find_element(By.XPATH, '//*[@id="js-main-balances-container"]/div[2]/div[1]/div[1]/label[2]').text).replace('R$', '')
        print('O saldo disponível na Betano é '+saldo_betano)
        navegador.quit()
        return float(saldo_betano.replace('.', '').replace(',', '.'))

"""
dol = Betano()
dol.getSaldo()

with open('data.json', 'w') as f:
    json.dump(dol.getCotacoes(), f)
exit()

"""