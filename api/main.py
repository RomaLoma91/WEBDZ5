from datetime import datetime, timedelta
from sys import argv
from aiohttp import ClientSession, TCPConnector, ClientConnectionError
import asyncio
import logging

def get_days_to(date_from: int):
    today = datetime.now()
    if date_from > 10:
        return 'No more then 10 days!'
    new_date = today - timedelta(days=date_from)
    return new_date.strftime('%d.%m.%Y')

async def request(url):
    try:
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f'Error status [{response.status}] - {url}')
    except ClientConnectionError as error:
        logging.error(f'Connection error - {error}')

async def make_request(days: int):
    tasks = []
    
    for i in range(days):
        url = f'https://api.privatbank.ua/p24api/exchange_rates?date={get_days_to(i)}'
        task = asyncio.create_task(request(url))
        tasks.append(task)

    return await asyncio.gather(*tasks)

async def show_data() -> dict:
    api_data = []
    data = await make_request(user)

    for element in data:
        usd, *_ = list(filter(lambda element: element.get('currency') == 'USD', element['exchangeRate']))
        eur, *_ = list(filter(lambda element: element.get('currency') == 'EUR', element['exchangeRate']))
        api_data.append({f'{element["date"]}': {"EUR": {"sale": eur['saleRate'], "buy": eur['purchaseRate']}, "USD": {"sale": usd['saleRate'], "buy": usd['purchaseRate']}}})

    return api_data

if __name__ == '__main__':
    user = int(argv[1])

    if user > 10:
        print('No more then 10 days!')
    else: 
        result = asyncio.run(show_data())
        print(result)