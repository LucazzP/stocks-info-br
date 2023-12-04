#!/usr/bin/env python3
import asyncio

from flask import Flask, jsonify, request
from fundamentus import get_data
from investidor10 import get_data as getDataInvestidor10
from datetime import datetime
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)

app = Flask(__name__)

# First update
lista, dia = dict(get_data()), datetime.strftime(datetime.today(), '%d')
lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in lista.items()}


# create routine to update data once a day
@scheduler.task('cron', id='update_data', hour=12) # every day at noon
async def update_data():
    global lista, dia
    print("Updating data...")
    # Then only update once a day
    if dia != datetime.strftime(datetime.today(), '%d'):
        lista, dia = dict(get_data()), datetime.strftime(datetime.today(), '%d')
        lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in lista.items()}
    # get investidor10 data
    await asyncio.gather(*[getDataInvestidor10(ticker, refresh=True) for ticker in lista])


@app.route("/")
async def json_api():
    global lista, dia
    
    ticker = request.args.get('ticker')
        
    if ticker:
        investidor10Data = await getDataInvestidor10(ticker)
        if ticker in lista:
            fundamentusData = dict(lista[ticker])
        else:
            fundamentusData = dict()
        result = merge_datas(fundamentusData, investidor10Data)

        return jsonify(result)
    else:
        results = await asyncio.gather(*[getDataInvestidor10(ticker) for ticker in lista])
        for i in range(len(lista)):
            stock: str = list(lista.keys())[i]
            investidor10Data = results[i]
            fundamentusData = dict(lista[stock])
            result = merge_datas(fundamentusData, investidor10Data)
            lista[stock] = result
        return jsonify(lista)


def merge_datas(fundamentusData: dict, investidor10Data: dict) -> dict:
    result = dict(fundamentusData)
    if investidor10Data and 'valorDeMercado' in investidor10Data:
        result['margemEbitda'] = investidor10Data['margemEbitda']
        result['payout'] = investidor10Data['payout']
        result['vpa'] = investidor10Data['vpa']
        result['lpa'] = investidor10Data['lpa']
        result['freeFloat'] = investidor10Data['freeFloat']
        result['tagAlong'] = investidor10Data['tagAlong']
        result['segmentoDeListagem'] = investidor10Data['segmentoDeListagem']
        result['nAcoes'] = investidor10Data['noTotalDePapeis']
        result['mktValue'] = investidor10Data['valorDeMercado']
    return result


if __name__ == "__main__":
    # run update routine in background
    asyncio.ensure_future(update_data())
    # run flask app
    app.run()
