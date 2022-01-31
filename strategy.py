import threading
import time
import xAPIConnector
import socket
import ssl
import json
import indicadores
import mailError



"""
max_variability

margin = lo que compré
free_margin = balance - margin +- beneficio
margin_level = patrimonio * 100 / margin
patrimonio = balance +- beneficio
valor_del_contrato
volumen
beneficio neto = volumen * valor_lote * (precio_actual - precio_apertura) = valor_contrato * (precio_actual - precio_apertura)
perdida_maxima = velumen * valor_lote * (- max_variability)

"""


"""
702.58, 704.35, 1770

max_variability = 703.06 - 693 = 10
balance = 13500
margin = 3500
patrimonio = 10000 + 3500 - 600 = 12900
margin_level = 12900 * 100 / 3500 ) = 365.57 %
perdida_maxima = 0.01 * 100000 * -10 = -10000
patrimonio_minimo = 13500 - 10000  = 3500
minimum_margin_level = 3500 * 100 / 3500 = 100% 

"""

def maxima_apuesta_posible(balance: float, margen: float, maxima_variabilidad: float, precio_compra: float, valor_lote: float):
    const_nivel_margen_minimo = 50

    lista_volumen = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]

    vol_maximo = 0.0
    for vol in lista_volumen:
        print("Calculo con: ", vol)
        perdida_maxima = vol * valor_lote * (maxima_variabilidad)
        patrimonio_minimo = balance - perdida_maxima
        print("Patrimonio minimo; ", patrimonio_minimo)
        nivel_margen_minimo = 100 * patrimonio_minimo / margen
        print("Nivel margen min: ", nivel_margen_minimo)

        if nivel_margen_minimo < const_nivel_margen_minimo:
            return vol_maximo
        vol_maximo = vol

    return vol

def calcular_profit_compra(volumen, valor_lote, precio_compra, precio_final):
    return volumen * valor_lote * (precio_final - precio_compra)

def calcular_profit_compraa(precio_compra, precio_final):
    return (precio_final - precio_compra)*700

def movimiento_emas(client: xAPIConnector.APIClient, emas_anteriores: dict, emas_actuales: dict, symbol: str, ultimo_precio, ultimo_200, mercado_anterior, vol_signal: bool, margen_symbol, sl):
    emas_anteriores_l = list(emas_anteriores.keys())
    emas_actuales_l = list(emas_actuales.keys())
    mercado_actual = tipo_de_mercado(ultimo_200, ultimo_precio)  # True = Alcista, False = Bajista
    print("Ultimo 200 y ultimo precio: "+str(ultimo_200)+"    "+str(ultimo_precio))
    print("Mercado actual: ", mercado_actual)
    if mercado_anterior != mercado_actual:
        cerrar_transacciones(symbol, client)

    precio_compra, precio_venta = precios_symbol(symbol, client)
    margen_libre = obtener_margen_libre(client)

    if mercado_actual and ultimo_200 < emas_actuales["ema_20"] and ultimo_200 < emas_actuales['ema_5']:
        if emas_anteriores_l[0] == "ema_5" and emas_actuales_l[1] == "ema_5" and vol_signal:
            client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd=0, offset=0, order=0, price=precio_compra, sl=sl, symbol=symbol, tp=0.0, type=0, volume=1)))
            mailError.sendmail("felipe.zxkq@gmail.com", "Abre compra de "+symbol, "EMAS anteriores: " + str(emas_anteriores) + "\nEMAs actuales: " + str(emas_actuales))
            print("Cambiaron de lugar, comprar")  # Orden decompra
        elif emas_actuales_l[0] == "ema_5" and emas_anteriores_l[1] == "ema_5":
            cerrar_transacciones(symbol, client)
            print("Hay que cerrar la operación de compra")
            mailError.sendmail("felipe.zxkq@gmail.com", "Cierre compra de "+symbol, "EMAS anteriores: " + str(emas_anteriores) + "\nEMAas actuales: " + str(emas_actuales))
    elif not mercado_actual and ultimo_200 > emas_actuales['ema_20'] and ultimo_200 > emas_actuales['ema_5']:
        if emas_actuales_l[0] == "ema_5" and emas_anteriores_l[1] == "ema_5" and vol_signal:
            client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd=1, offset=0, order=0, price=precio_venta, sl=sl, symbol=symbol, tp=0.0, type=0, volume=1)))
            print("Cambiaron de lugar, shortear")  # Orden de venta
            mailError.sendmail("felipe.zxkq@gmail.com", "Abre shorteo de "+symbol, "EMAS anteriores: " + str(emas_anteriores) + "\nEMAas actuales: " + str(emas_actuales))
        elif emas_anteriores_l[0] == "ema_5" and emas_actuales_l[1] == "ema_5":
            mailError.sendmail("felipe.zxkq@gmail.com", "Cierre shorteo de "+symbol, "EMAS anteriores: " + str(emas_anteriores) + "\nEMAas actuales: " + str(emas_actuales))
            cerrar_transacciones(symbol, client)
    return mercado_actual


def tipo_de_mercado(ultimo_200, ultimo_precio):
    if ultimo_200 < ultimo_precio:
        return True
    else:
        return False

def cerrar_transacciones(symbol, client):
    trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
    precio_compra, precio_venta= precios_symbol(symbol, client)
    for trade in trades:
        volumen = trade['volume']
        if trade['symbol'] == symbol:
            order = trade['order']
            client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= trade['cmd'], customComment="a", expiration=0, order=order, price=precio_compra, sl=0, tp=0, symbol=symbol, type=2, volume=volumen)))
            
def mover_stop_loss(symbol, client, nuevo_piso, compra_o_venta):
    trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
    precio_compra, precio_venta= precios_symbol(symbol, client)
    for trade in trades:
        volumen = trade['volume']
        if trade['symbol'] == symbol:
            order = trade['order']
            client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= trade['cmd'], customComment="a", expiration=0, order=order, price=precio_compra, sl=nuevo_piso, tp=0, symbol=symbol, type=3, volume=volumen)))
            
def precios_symbol(symbol, client):
    datos_symbol = client.commandExecuteAndRespond('getSymbol',  dict(symbol = symbol))['returnData']
    precio_compra = datos_symbol['ask']
    precio_venta = datos_symbol['bid']
    return precio_compra, precio_venta

def obtener_margen_symbol(symbol, client):
    lote_min = client.commandExecuteAndRespond('getSymbol',  dict(symbol = symbol))['returnData']['lotMin']
    margen_symbol = client.commandExecuteAndRespond('getMarginTrade',  dict(symbol=symbol, volume=lote_min))['returnData']['margin']
    print("El margen es: ", margen_symbol)
    return margen_symbol

def obtener_margen_libre(client):
    balances_cuenta = client.commandExecuteAndRespond('getMarginLevel')['returnData']
    margen_libre = balances_cuenta['margin_free']
    return margen_libre

def cuanto_comprar(margen_libre, costo_margen):
    division = int(margen_libre/costo_margen)
    return int(division*7/10)  # compra un valor cercano al 70% del margen libre en la cuenta


#cuanto_comprar(100000, 7000)
    

            

#movimiento_emas(False, dict(ema_5=1.0, ema_20=2.0), dict(ema_20=1.0, ema_5=1.2))

# min: 1684, max: 2070, med = 1877, variacion: 20.5%  // min: 693, max: 841, med: 767, variacion: 19%
print("Maxima apuesta: ", maxima_apuesta_posible(22420, 4030, 15, 808, 100000))

#print("Maxima apuesta: ", maxima_apuesta_posible(11800, 3499, 10.6, 700.4, 100000))

# Oro
#print("Profit: ", calcular_profit_compra(0.01, 181400, 1814, 1815))

# Oro2
#print("Profit: ", calcular_profit_compraa(0.01, 181400, 1814, 1815))

# usdclp
#print("Profit: ", calcular_profit_compra(0.01, 100000, 700.38, 699.44))
