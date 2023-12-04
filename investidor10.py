#!/usr/bin/env python3
import http.cookiejar
import json
import sys
import urllib.parse
import urllib.request
import time
from collections import OrderedDict
from decimal import Decimal

from bs4 import BeautifulSoup
from unidecode import unidecode


async def get_data(ticker, refresh=False):
    file_name = 'cache/' + ticker + '.json'
    try:
        with open(file_name, 'r') as file:
            data_loaded = json.load(file)
            date = data_loaded['date'] if 'date' in data_loaded else 1701625668
            # print("Cache encontrado")
            if data_loaded:
                # print("Utilizando cache")
                # reparse dict values using fromStringToCorrectType
                data_loaded = {k: fromStringToCorrectType(v) for k, v in data_loaded.items()}
                # if cache date is older than 15 days, update cache
                if (time.time() - date) > 1296000:
                    if refresh:
                        print("Cache antigo, atualizando.")
                        data_loaded = await get_refreshed_data(ticker)
                    else:
                        print("Cache antigo, mas não atualizando.")
                return data_loaded
    except FileNotFoundError:
        print("Arquivo não encontrado. Atualizando dados.")

    if refresh:
        print("Atualizando dados.")
        return await get_refreshed_data(ticker)
    print("Dados não encontrados. Ative o refresh para atualizar.")
    return dict()


async def get_refreshed_data(ticker):
    file_name = 'cache/' + ticker + '.json'
    url = 'https://investidor10.com.br/acoes/' + ticker

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; rv:2.2) Gecko/20110201'),
                         ('Accept', 'text/html, text/plain, text/css, text/sgml, */*;q=0.01')]

    try:
        # link = await asyncio.get_event_loop().run_in_executor(None, opener.open, url)
        link = opener.open(url)
        content = link.read().decode('utf-8')
    except Exception as err:
        print(err)
        print("Ticker: " + ticker + ", Erro ao abrir a página. Verifique se o ticker está correto. " + url)
        if str(err) == "HTTP Error 404: Not Found":
            print("Ticker não encontrado, salvando arquivo vazio.")
            with open(file_name, 'w') as file:
                json.dump({'date': time.time()}, file)
        return dict()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Find the div with id 'table-indicators'
    indicators_div = soup.find('div', id='table-indicators')
    company_numbers_div = soup.find('div', id='table-indicators-company')

    result = OrderedDict()

    # Check if the div was found
    if indicators_div:
        for cell in indicators_div.find_all(name="div", recursive=False):
            title = remove_acentos(str(cell.find(name="span").contents[0]).strip())
            value = todecimal(str(cell.find(name="div").find_next().contents[0]).strip())
            result.update({
                to_camel_case(title): float(value)
            })
    else:
        print("Div 'table-indicators' not found.")

    if company_numbers_div:
        for cell in company_numbers_div.find_all(name="div", recursive=False):
            title = remove_acentos(str(cell.find_all_next(name="span")[0].contents[0]).strip())
            try:
                value = str(cell.find_all_next(name="span")[1].contents[3].contents[0]).strip()
            except Exception:
                value = str(cell.find_all_next(name="span")[1].contents[0]).strip()
            value = fromStringToCorrectType(value)
            result.update({
                to_camel_case(title): value
            })
    else:
        print("Div 'table-indicators-company' not found.")

    # Add date to the result
    result.update({
        'date': time.time()
    })

    with open(file_name, 'w') as file:
        json.dump(result, file)

    return result


# Function to convert keys to camelCase
def to_camel_case(s):
    s = s.replace('.', '').replace(' / ', ' ').replace('/', ' ').replace(' - ', ' ')
    parts = s.split()
    return parts[0].lower() + ''.join(x.capitalize() for x in parts[1:])


def fromStringToCorrectType(value: str):
    try:
        value = todecimal(value)
    except Exception:
        value = value
    return value


def todecimal(string):
    if (string == "-"):
        return 0
    string = string.replace('.', '')
    string = string.replace(',', '.')

    if (string.endswith('%')):
        string = string[:-1]
        return float(Decimal(string) / 100)
    # R$ 7.697.073.000
    elif string.startswith('R$'):
        string = string[2:]
        return float(Decimal(string))
    else:
        return float(Decimal(string))


def remove_acentos(text):
    return unidecode(text)


if __name__ == '__main__':
    # from waitingbar import WaitingBar

    # progress_bar = WaitingBar('[*] Downloading...')
    result = get_data(sys.argv[1])
    # progress_bar.stop()

    print(json.dumps(result, indent=4))
