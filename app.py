#!/usr/bin/env python3

from flask import Flask, jsonify, request
from fundamentus import get_data
from investidor10 import get_data as getDataInvestidor10
from datetime import datetime

app = Flask(__name__)

# First update
lista, dia = dict(get_data()), datetime.strftime(datetime.today(), '%d')
lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in lista.items()}


@app.route("/")
def json_api():
    global lista, dia
    
    ticker = request.args.get('ticker')
    
    # Then only update once a day
    if dia != datetime.strftime(datetime.today(), '%d'):
        lista, dia = dict(get_data()), datetime.strftime(datetime.today(), '%d')
        lista = {outer_k: {inner_k: float(inner_v) for inner_k, inner_v in outer_v.items()} for outer_k, outer_v in lista.items()}
        
    if ticker:
        investidor10Data = getDataInvestidor10(ticker)
        if ticker in lista:
            result = dict(lista[ticker])
        else:
            result = investidor10Data
        if result:
            result['margemEbitda'] = investidor10Data['margemEbitda']
            result['payout'] = investidor10Data['payout']
            result['vpa'] = investidor10Data['vpa']
            result['lpa'] = investidor10Data['lpa']
            result['freeFloat'] = investidor10Data['freeFloat']
            result['tagAlong'] = investidor10Data['tagAlong']
            result['segmentoDeListagem'] = investidor10Data['segmentoDeListagem']
            result['nAcoes'] = investidor10Data['noTotalDePapeis']
            result['mktValue'] = investidor10Data['valorDeMercado']

        return jsonify(result)
    else:
        return jsonify(lista)


if __name__ == "__main__":
    app.run()
