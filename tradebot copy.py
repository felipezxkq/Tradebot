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
        self.emas_buscadas = False

        userId = 12262181
        password = 'Primocuenta123'
        self.client = xAPIConnector.APIClient()
        loginResponse = self.client.execute(xAPIConnector.loginCommand(userId=userId, password=password))
        xAPIConnector.logger.info(str(loginResponse)) 
        if(loginResponse['status'] == False):
            print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        
        self.thread.start()  

    def run(self):
        while True:
            print("hola")

    def connect_to_stram_api(self):

        pass

bot = Tradebot()
print("caca")
time.sleep(144000)