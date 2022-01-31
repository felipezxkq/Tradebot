import threading
import time
import xAPIConnector, strategy
import socket
import ssl
import json
import indicadores
import mailError
import jugada
from datetime import datetime


class Tradebot(object):

    def __init__(self, interval = 2):
        self.interval = interval
        self.cond = threading.Condition()
        self.thread = threading.Thread(target=self.run, args=())
        self.thread.daemon = True
        self.stopped = threading.Event()
        self.mercado_alcista = True
        self.order = None
        self.hizo_operacion_euro = False

        userId = 12160431
        password = 'Primocuenta123'
        self.client = xAPIConnector.APIClient()
        loginResponse = self.client.execute(xAPIConnector.loginCommand(userId=userId, password=password))
        xAPIConnector.logger.info(str(loginResponse)) 
        if(loginResponse['status'] == False):
            print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))

        ultimo_5, ultimo_20, ultimo_200, self.ultimo_precio_anterior = indicadores.obtener_emas(self.client, "EURUSD")

            
        #data = client.commandExecute('getProfitCalculation',  dict(closePrice = 1.20615, cmd=0, openPrice = 1.19942, symbol='EURUSD', volume=0.1))
        self.thread.start()  

    def run(self):
        while True:
            tiempo = time.localtime()
            ultimo_5, ultimo_20, ultimo_200, self.ultimo_precio = indicadores.obtener_emas(self.client, "EURUSD")
            if self.ultimo_precio != self.ultimo_precio_anterior:
                mailError.sendmail("felipe.zxkq@gmail.com", "Cambiaron las velas", "En el tiempo: "+str(tiempo)+" \n"+"ultimo_precio anterior: "+str(self.ultimo_precio_anterior)+"\n"+"ultimo_precio actual: "+str(self.ultimo_precio))
            self.ultimo_precio_anterior = self.ultimo_precio
            time.sleep(2)
        

    def connect_to_stram_api(self):

        pass

bot = Tradebot()
print("caca")
time.sleep(144000)