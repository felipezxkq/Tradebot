from numpy import true_divide
import pandas as pd
import xAPIConnector
import time
import json
import math
from datetime import datetime

# Indicadores y operaciones

def obtener_emas(client: xAPIConnector.APIClient, symbol):
    startTime = client.commandExecuteAndRespond('getServerTime')
    startTime = startTime['returnData']['time'] - 259200*1000
    data = client.commandExecute('getChartLastRequest',  dict(info = dict(period= 5, start = startTime, symbol=symbol)))
    velas = data['returnData']['rateInfos']
    #print(velas)
    cierres = []
    for vela in velas:
        cierres.append(vela['open'] + vela['close'])
    #print("Cierres: ", cierres)
    ultimo_volumen = velas[-1]['vol'] 
    data = dict(cierres = cierres)

    print("Primer vela: ", cierres[0])
    print("Ultima vela: ", cierres[-1])
    velas_5 = pd.DataFrame(data)
    promedio_5 = velas_5.ewm(span=5).mean()
    ultimo_ema_5 = promedio_5["cierres"].iloc[-1]
    print("Ultimo avg EMA 5 es: ", ultimo_ema_5)

    velas_20 = pd.DataFrame(data)
    promedio_20 = velas_20.ewm(span=20).mean()
    ultimo_ema_20 = promedio_20["cierres"].iloc[-1]
    print("Ultimo avg EMA 20 es: ", ultimo_ema_20)

    velas_200 = pd.DataFrame(data)
    promedio_200 = velas_200.ewm(span=200).mean()
    ultimo_ema_200 = promedio_200["cierres"].iloc[-1]
    print("Ultimo avg EMA 200 es: ", ultimo_ema_200)

    return ultimo_ema_5, ultimo_ema_20, ultimo_ema_200, cierres[-1], ultimo_volumen

# Además da un estimado de cuanto debería ser el SL
def obtener_emas_cambiantes_por_seg(client: xAPIConnector.APIClient, symbol, velas_anteriores):
    cierres = velas_anteriores
    precio_compra, precio_venta = precios_symbol(symbol, client)
    #print("Ultimo antes: ",precio_venta)
    precio_venta_esp, exponencia = convertir_al_mismo_orden_de_magnitud(cierres[-1], precio_venta)
    #print("Ultimo precio: ", precio_venta_esp)
    cierres.append(precio_venta_esp)
    data = dict(cierres = cierres)

    #print("Primer vela: ", cierres[0])
    #print("Ultima vela: ", cierres[-1])
    velas_5 = pd.DataFrame(data)
    promedio_5 = velas_5.ewm(span=5).mean()
    ultimo_ema_5 = promedio_5["cierres"].iloc[-1]
    #print("Ultimo avg EMA 5 es: ", ultimo_ema_5)
    

    velas_20 = pd.DataFrame(data)
    promedio_20 = velas_20.ewm(span=20).mean()
    ultimo_ema_20 = promedio_20["cierres"].iloc[-1]
    #print("Ultimo avg EMA 20 es: ", ultimo_ema_20)

    velas_200 = pd.DataFrame(data)
    promedio_200 = velas_200.ewm(span=200).mean()
    ultimo_ema_200 = promedio_200["cierres"].iloc[-1]
    #print("Ultimo avg EMA 200 es: ", ultimo_ema_200)

    # Para que las emas vuelvan a cruzarse (señal de cerrar posición), la distancia entre el precio actual y la ema_5 tiene que ser igual o mayor a la distancia que estaban
    # cuando se abrió la posición, pero en el sentido contrario
    if ultimo_ema_5 > ultimo_ema_20:
        diferencia_stop_loss = round(4*abs((ultimo_ema_5/pow(10, exponencia) - precio_venta)), exponencia)
    else:
        diferencia_stop_loss = round(2.4*abs((ultimo_ema_5/pow(10, exponencia) - precio_compra)), exponencia)
    #print("Diferencia stop loss es: ", diferencia_stop_loss)

    emas_dict = dict(ema_5= ultimo_ema_5, ema_20= ultimo_ema_20)
    emas = dict(sorted(emas_dict.items(), key=lambda item: item[1]))
    return diferencia_stop_loss, precio_venta_esp, ultimo_ema_200, emas

def obtener_velas_anteriores(client: xAPIConnector.APIClient, symbol):
    startTime = client.commandExecuteAndRespond('getServerTime')
    startTime = startTime['returnData']['time'] - 259200*1000
    data = client.commandExecute('getChartLastRequest',  dict(info = dict(period= 5, start = startTime, symbol=symbol)))
    velas = data['returnData']['rateInfos']
    ultima_vela = velas[-1]
    ultimo_volumen = velas[-1]['vol'] 
    cierres = []
    for vela in velas:
        cierres.append(vela['open'] + vela['close'])

    return ultimo_volumen, cierres, ultima_vela

def maxima_apuesta_posible(balance: float, margen: float, maxima_variabilidad: float, precio_compra: float, valor_lote: float):
    const_nivel_margen_minimo = 50

    lista_volumen = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07]

    vol_maximo = 0.0
    for vol in lista_volumen:
        perdida_maxima = vol * valor_lote * (maxima_variabilidad)
        patrimonio_minimo = balance - perdida_maxima
        nivel_margen_minimo = 100 * patrimonio_minimo / margen

        if nivel_margen_minimo < const_nivel_margen_minimo:
            return vol_maximo
        vol_maximo = vol
    return vol

def calcular_profit_compra(volumen, valor_lote, precio_compra, precio_final):
    return volumen * valor_lote * (precio_final - precio_compra)

def calcular_profit_compraa(precio_compra, precio_final):
    return (precio_final - precio_compra)*700

def tipo_de_mercado(ultimo_200, ultimo_precio):
    if ultimo_200 < ultimo_precio:
        return True
    else:
        return False

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

def obtener_balance_patrimonio_y_nivel_margen(client):
    balances_cuenta = client.commandExecuteAndRespond('getMarginLevel')['returnData']
    return balances_cuenta['balance'], balances_cuenta['equity'], balances_cuenta['margin_level']

def cuanto_comprar(margen_libre, costo_margen):
    division = int(margen_libre/costo_margen)
    return int(division*7/10)  # compra un valor cercano al 70% del margen libre en la cuenta

def verifica_transaccion(symbol, client):
    trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
    precio_compra, precio_venta= precios_symbol(symbol, client)
    for trade in trades:
        volumen = trade['volume']
        if trade['symbol'] == symbol:
            print("Hay un trade abierto de: ", trade['symbol'])
            return True
    return False

def convertir_al_mismo_orden_de_magnitud(numero_con_orden_deseado, numero_a_cambiar_magnitud):
    orden_de_magnitud_deseado = math.floor(math.log(numero_con_orden_deseado, 10))
    orden_de_magnitud_actual = math.floor(math.log(numero_a_cambiar_magnitud, 10))

    if orden_de_magnitud_deseado > orden_de_magnitud_actual:
        exponente = orden_de_magnitud_deseado-orden_de_magnitud_actual
        numero_a_cambiar_magnitud = numero_a_cambiar_magnitud*pow(10, exponente)
        
    else:
        exponente = orden_de_magnitud_actual-orden_de_magnitud_deseado
        numero_a_cambiar_magnitud = numero_a_cambiar_magnitud/pow(10, exponente)

    return numero_a_cambiar_magnitud, exponente  # Devuelve como quedaría el número al final y el exponente que se necesitó


def encontrar_sl(precio_venta: float, sl_diff: float, compra: bool, spread):
    numero_decimales = str(precio_venta)[::-1].find('.')
    """
    if symbol=="EURUSD":
        diff_symbol = 0.00032
    elif symbol=="USDJPY":
        diff_symbol = 0.00032

    else:
        diff_symbol = 0.00015
        if compra:
            return round(precio_venta*(1-diff_symbol), numero_decimales)
        else:
            return round(precio_venta*(1+diff_symbol), numero_decimales)

    if compra:
        return round(precio_venta - diff_symbol, numero_decimales)
    else:
        return round(precio_venta + diff_symbol, numero_decimales)
        """
    if compra:
        return round(precio_venta - 3*spread, numero_decimales)
    else:
        return round(precio_venta + 3*spread, numero_decimales)

def cumple_condiciones_cruce_ema(mercado_alcista: bool, emas_anteriores, emas_actuales, ultimo_200):
    if mercado_alcista:
        if emas_actuales['ema_5'] < ultimo_200 or emas_actuales['ema_20'] < ultimo_200 or emas_anteriores['ema_20'] < ultimo_200 or emas_anteriores['ema_5'] < ultimo_200:
            return False
        if emas_actuales['ema_5'] < emas_anteriores['ema_5']:
            return False
    else:
        if emas_actuales['ema_5'] > ultimo_200 or emas_actuales['ema_20'] > ultimo_200 or emas_anteriores['ema_20'] > ultimo_200 or emas_anteriores['ema_5'] > ultimo_200:
            return False
        if emas_actuales['ema_5'] > emas_anteriores['ema_5']:
            return False
    return True

def sacar_diferencia_emas(ema_5, ema_20):
    return abs(ema_5 - ema_20)/ema_5

a = [1, 2, 3, 4]

#print(encontrar_sl(1.21664, 1, True))

#print(encontrar_sl(1.234, 0.12346, True))

#print("Maxima apuesta: ", maxima_apuesta_posible(2600, 3600, 21, 718, 100000))


#print("Tiempo: ", time.localtime().tm_min % 5 == 0 and time.localtime().tm_sec < 10)