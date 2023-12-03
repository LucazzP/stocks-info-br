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
        investidorTenData = getDataInvestidor10(ticker)
        if ticker in lista:
            result = dict(lista[ticker])
        else:
            result = investidorTenData
        if result:
            result['margemEbitda'] = investidorTenData['margemEbitda']
            result['payout'] = investidorTenData['payout']
            result['vpa'] = investidorTenData['vpa']
            result['lpa'] = investidorTenData['lpa']
            result['freeFloat'] = investidorTenData['freeFloat']
            result['tagAlong'] = investidorTenData['tagAlong']
            result['segmentoDeListagem'] = investidorTenData['segmentoDeListagem']
            result['nAcoes'] = investidorTenData['noTotalDePapeis']
            result['mktValue'] = investidorTenData['valorDeMercado']

        return jsonify(result)
    else:
        return jsonify(lista)


app.run(debug=True)
