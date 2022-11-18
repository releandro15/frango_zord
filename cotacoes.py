import asyncio
import json
import random
import time
import pandas as pd
import requests
import aiohttp
import asyncio
import time

cotacoes_betano = pd.read_excel('cotacoes_betano.xlsx', sheet_name='Sheet1').drop_duplicates(subset=['url_betano']).dropna()
cotacoes_betano['url_betano'] = 'https://br.betano.com/api'+cotacoes_betano['url_betano']
cotacoes_betano = cotacoes_betano['url_betano'].tolist()

resultados = []

start_time = time.time()


async def get_pokemon(session, url):
    try:
        async with session.get(url) as resp:
            data = await resp.json()
            print(data['data']['event']['name'])
            return (data['data']['event'])
    except:
        print('Erro betano')


async def main():

    async with aiohttp.ClientSession() as session:

        tasks = []
        for number in cotacoes_betano:
            url = number
            tasks.append(asyncio.ensure_future(get_pokemon(session, url)))

        tst = await asyncio.gather(*tasks)

        with open('data.json', 'w') as f:
            json.dump(tst, f)


        """for pokemon in original_pokemon:
            print(pokemon)"""

asyncio.run(main())
print("--- %s seconds ---" % (time.time() - start_time))