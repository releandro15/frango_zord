import asyncio
import http.client
import json
import aiohttp
import unidecode
from datetime import datetime, timedelta
import pandas as pd


class Dollar:

    @classmethod
    def getJogos(cls):
        jogos = []

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

            for jogo in data:
                jogos.append(jogo['_id'])

        return jogos

    def montaJson(self, casa, fora, inicio, mercado, odds_dollar):
        inicio = (datetime.strptime(inicio, '%Y-%m-%dT%H:%M:%S.%f%z') + timedelta(hours=-4)).strftime("%d/%m/%Y %H:%M")
        return {
            "casa": casa,
            "fora": fora,
            "chave": (unidecode.unidecode(casa+' x '+fora)),
            "inicio": inicio,
            "mercado": mercado,
            "odds_dollar": odds_dollar
        }
    async def getDados(self, session, url):
        headers = {
            'Origin': 'https://www.dollar.bet'
        }
        try:
            async with session.get(url, headers=headers) as resp:
                data = await resp.json()
                print(f"Dollar {data['home_team']} - {data['away_team']}")
                return (data)
        except:
            print('Erro Dollar')

    async def getCotacoes(self, jogos_dollar):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for jogo in jogos_dollar:
                url = 'https://slark.ngx.bet/event/' + jogo
                tasks.append(asyncio.ensure_future(self.getDados(session, url)))

            data = await asyncio.gather(*tasks)
            return data

    def filtraMercados(self, jogos_cotacoes):
        jogos_filtrados = []
        for jogo in jogos_cotacoes:
            casa = jogo['home_team']
            fora = jogo['away_team']
            inicio = jogo['date']
            for mercadox in jogo['odds']['full_time']['goals_over_under']:
                mercado = 'Total Gols '+('Mais de ' if mercadox['header']=='UNDER' else 'Menos de ')+mercadox['name']
                odds_dollar = mercadox['value']
                jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))
            for mercadox in jogo['odds']['first_time']['goals_over_under']:
                mercado = 'Total Gols 1T '+('Mais de ' if mercadox['header']=='UNDER' else 'Menos de ')+mercadox['name']
                odds_dollar = mercadox['value']
                jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))

            mercado = 'Ambas equipes Marcam Não'
            odds_dollar = jogo['odds']['full_time']['both_teams_to_score_yes']['value']
            jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))

            mercado = 'Ambas equipes Marcam Sim'
            odds_dollar = jogo['odds']['full_time']['both_teams_to_score_no']['value']
            jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))

            mercado = 'Chance Dupla 1X'
            odds_dollar = jogo['odds']['full_time']['away']['value']
            jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))

            mercado = 'Chance Dupla X2'
            odds_dollar = jogo['odds']['full_time']['home']['value']
            jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))

            mercado = 'Chance Dupla 12'
            odds_dollar = jogo['odds']['full_time']['draw']['value']
            jogos_filtrados.append(self.montaJson(casa, fora, inicio, mercado, odds_dollar))


        return jogos_filtrados

    def normalizeDollar(self, pd_cotacoes_dollar):
        print("Nomalizando nomes Dollar")
        pd_normalize_teams = pd.read_excel(r'normalize\newNomalize.xlsx',
                                           sheet_name='Dollar')

        # Novo método de normalização de nomes
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
            m.iloc[index_m, m.columns.get_loc('chave')] = (unidecode.unidecode(row_m['casa'] + ' x ' + row_m['fora']))

        return m[['casa', 'fora', 'chave', 'inicio', 'mercado', 'odds_dollar']]


"""dol = Dollar()
cotacoes = asyncio.run(dol.getCotacoes(dol.getJogos()))
filt = dol.filtraMercados(cotacoes)

with open('data.json', 'w') as f:
    json.dump(filt, f)
exit()
"""