import http.client
import json
import math
import unidecode

class BetanoBkp:

    @classmethod
    def getCotacoes(cls):
        jogos = []
        countEvents = 0

        conn = http.client.HTTPSConnection("br.betano.com")
        conn.request("GET", "/api/upcomingcoupon/?sid=FOOT&day=Friday")
        res = conn.getresponse()
        data = res.read()
        data = json.loads(data.decode("utf-8"))

        events = data['data']['coupons'][0]['subNavItems'][1]['events']
        lastId = data['data']['coupons'][0]['subNavItems'][1]['events'][len(events)-1]['id']
        totalEvents = data['data']['coupons'][0]['subNavItems'][1]['totalEvents']
        countEvents = countEvents + len(events)

        for x in range(math.trunc(totalEvents/25)):
            conn.request("GET", "/api/upcomingcoupon/?sid=FOOT&day=Friday&latestId="+lastId)
            res = conn.getresponse()
            data = res.read()
            data = json.loads(data.decode("utf-8"))
            events = data['data']['coupons'][0]['subNavItems'][1]['events']
            if len(events) >= 1:
                lastId = data['data']['coupons'][0]['subNavItems'][1]['events'][len(events)-1]['id']
                countEvents = countEvents + len(events)

                for event in events:
                    newData = ''
                    for market in event['markets']:
                        if market['name']=="Total de Gols Mais/Menos" :
                            for selection in market['selections']:
                                if selection['name']=='Mais de 2.5':
                                    odds_goals_over = selection['price']
                                    newData = {
                                        "id": event['id'],
                                        "home_team": event['participants'][0]['name'],
                                        "away_team": event['participants'][1]['name'],
                                        "chave_jogo": unidecode.unidecode(event['participants'][0]['name'][:3] + '_X_' + event['participants'][1]['name'][:3]),
                                        "start_time": event['startTime'],
                                        "odds_goals_over": odds_goals_over
                                    }
                    if newData != "":
                        print("Betano:  " + newData['home_team'] + " x " + newData['away_team'])
                        jogos.append(newData)
            return jogos

"""
dol = Betano()
dol.getCotacoes()

with open('data.json', 'w') as f:
    json.dump(dol.getCotacoes(), f)
exit()
"""