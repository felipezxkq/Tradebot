from numpy import true_divide
import pandas as pd
import xAPIConnector
import time
import json
import math
from datetime import datetime


def cerrar_transacciones(symbol, client):  # accion
    trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
    precio_compra, precio_venta= precios_symbol(symbol, client)
    for trade in trades:
        volumen = trade['volume']
        if trade['symbol'] == symbol:
            order = trade['order']
            client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= trade['cmd'], customComment="a", expiration=0, order=order, price=precio_compra, sl=0, tp=0, symbol=symbol, type=2, volume=volumen)))
            
def mover_stop_loss(symbol, client, precio_anterior, sl_actual):  # accion
    trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
    precio_compra, precio_venta= precios_symbol(symbol, client)
    for trade in trades:
        volumen = trade['volume']
        if trade['symbol'] == symbol:
            print("SI HAY UNA OPERACION DE: ", symbol)
            order = trade['order']
            if trade['cmd'] == 0:
                ultimo_precio = precio_venta
                if precio_anterior < ultimo_precio:
                    diferencia = ultimo_precio - precio_anterior
                    nuevo_sl = sl_actual + diferencia
                    client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= trade['cmd'], customComment="a", expiration=0, order=order, price=precio_compra, sl=nuevo_sl, tp=0, symbol=symbol, type=3, volume=volumen)))
                    return ultimo_precio, nuevo_sl
                else:
                    return ultimo_precio, sl_actual
            elif trade['cmd'] == 1:
                ultimo_precio = precio_compra
                if precio_anterior > ultimo_precio:
                    diferencia = precio_anterior - ultimo_precio
                    nuevo_sl = sl_actual - diferencia
                    client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= trade['cmd'], customComment="a", expiration=0, order=order, price=precio_compra, sl=nuevo_sl, tp=0, symbol=symbol, type=3, volume=volumen)))
                    return ultimo_precio, nuevo_sl
                else:
                    return ultimo_precio, sl_actual