import asyncio
import datetime
import aiohttp
import requests
import unidecode
from bs4 import BeautifulSoup
import json

class Betano:
    @classmethod
    def getJogos(cls):
        jogos = []

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

        for event_firstpage in events_firstpage:
            jogos.append(event_firstpage['url'])

        # Percorrendo demais páginas
        i = True
        while i:
            try:
                res = requests.get('https://br.betano.com/api/sport/futebol/jogos-de-hoje/?latestId=' + lastId,
                                   headers=headers)
                data = res.json()
                events_page = data['data']['blocks'][0]['events']
                lastId = events_page[len(events_page) - 1]['id']

                for event_page in events_page:
                    jogos.append(event_page['url'])

            except:
                i = False

        return jogos

    def montaJson(self, casa, fora, inicio, mercado, odds_betano):
        inicio = datetime.datetime.fromtimestamp(int(str(inicio)[:-3])).strftime('%d/%m/%Y %H:%M')
        return {
            "casa": casa,
            "fora": fora,
            "chave": (unidecode.unidecode(casa+' x '+fora)),
            "inicio": inicio,
            "mercado": mercado,
            "odds_betano": odds_betano
        }

    async def getDados(self, session, url):
        try:
            async with session.get(url) as resp:
                data = await resp.json()
                qtd_mkts = len(data['data']['markets'])
                maior = 0
                url = url+'?bt='+str(qtd_mkts)
                async with session.get(url) as resp:
                    data = await resp.json()
                    print(data['data']['event']['name'])
                    return (data['data']['event'])
        except:
            print('Erro Betano')

    async def getCotacoes(self, jogos_betano):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for jogo in jogos_betano:
                url = 'https://br.betano.com/api'+jogo
                tasks.append(asyncio.ensure_future(self.getDados(session, url)))

            data = await asyncio.gather(*tasks)
            return data

    def filtraMercados(self, jogos_cotacoes):
        jogos_filtrados = []
        for jogo in jogos_cotacoes:
            casa = jogo['participants'][0]['name']
            fora = jogo['participants'][1]['name']
            inicio = jogo['startTime']
            mercados = jogo['markets']
            for mercadox in mercados:
                if mercadox['name'] == 'Total de Gols Mais/Menos':
                    for selection in mercadox['selections']:
                        mercado = 'Total Gols '+selection['name']
                        odds_betano = selection['price']
                        jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_betano))
                if mercadox['name'] == 'Ambas equipes Marcam':
                    for selection in mercadox['selections']:
                        mercado = mercadox['name']+' '+selection['name']
                        odds_betano = selection['price']
                        jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_betano))
                if mercadox['name'] == 'Total de gols Mais/Menos - 1° Tempo':
                    for selection in mercadox['selections']:
                        mercado = 'Total Gols 1T '+selection['name']
                        odds_betano = selection['price']
                        jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_betano))
                if mercadox['name'] == 'Chance Dupla':
                    for selection in mercadox['selections']:
                        mercado = 'Chance Dupla '+selection['name']
                        odds_betano = selection['price']
                        jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_betano))

        return jogos_filtrados


"""
dol = Betano()
cotacoes = asyncio.run(dol.getCotacoes(dol.getJogos()))
filt = dol.filtraMercados(cotacoes)

with open('data.json', 'w') as f:
    json.dump(filt, f)
exit()
"""