import socket
import ssl
import json
import api_connection
import pandas as pd
import xAPIConnector
import time
import logging
import indicadores
import strategy


userId = 12160431
password = 'Primocuenta123'
client = xAPIConnector.APIClient()
loginResponse = client.execute(xAPIConnector.loginCommand(userId=userId, password=password))
xAPIConnector.logger.info(str(loginResponse)) 
if(loginResponse['status'] == False):
    print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
    

ssid = loginResponse['streamSessionId']
#sclient = xAPIConnector.APIStreamClient(ssId=ssid, tickFun=xAPIConnector.procTickExample, tradeFun=xAPIConnector.procTradeExample, profitFun=xAPIConnector.procProfitExample, tradeStatusFun=xAPIConnector.procTradeStatusExample)
#sclient.subscribeCandles('ZECBTC')

"""datos_symbol = client.commandExecute('getSymbol',  dict(symbol = "EURUSD"))['returnData']
precio_compra = datos_symbol['ask']
precio_venta = datos_symbol['bid']
print(client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= 1, customComment="callao lacra", expiration=0, order=275436154, price=precio_compra, sl=0, tp=0, symbol="EURUSD", type=2, volume=0.01))))
"""

#profitt = client.commandExecute('getSymbol',  dict(symbol = "EURUSD"))['returnData']


"""datos_symbol = client.commandExecute('getSymbol',  dict(symbol = "EURUSD"))['returnData']
precio_compra = datos_symbol['ask']
precio_venta = datos_symbol['bid']
order = client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd=1, offset=0, order=0, price=precio_venta, sl=0.0, symbol="EURUSD", tp=0.0, type=0, volume=0.01)))
order = order['returnData']['order']
print("Número de orden: ", order)

trades = client.commandExecute('getTrades',  dict(openedOnly=True))['returnData']
position = None
for trade in trades:
    print("Order: ", trade['position'])
    print("O")
    if trade['symbol'] == "EURUSD":
        order = trade['order']

print(position)
print(client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd= 1, customComment="callao lacra", expiration=0, order=order, price=precio_compra, sl=0, tp=0, symbol="EURUSD", type=2, volume=0.01))))
"""


#data = client.commandExecute('getProfitCalculation',  dict(closePrice = 1.21576, cmd=0, openPrice = 1.21446, symbol='EURUSD', volume=0.01))
#print("Profit: ", data)
#strategy.obtener_margen_symbol("EURUSD", client)
#strategy.mover_stop_loss("EURUSD", client, 1.22070, 1)
#a, b, c, ultimo_precio, e = indicadores.obtener_emas(client, "EURUSD")
#print("Ultimo precio es: ",ultimo_precio)
print("Precios symbol: ",strategy.precios_symbol("EURUSD", client))

#indicadores.obtener_emas(client, "BITCOIN")

time.sleep(5)
#sclient.disconnect()
client.disconnect()



