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

        userId = 13020125
        password = 'colocoloCampeon123!"#'
        self.client = xAPIConnector.APIClient()
        loginResponse = self.client.execute(xAPIConnector.loginCommand(userId=userId, password=password))
        xAPIConnector.logger.info(str(loginResponse)) 
        if(loginResponse['status'] == False):
            print('Login failed. Error code: {0}'.format(loginResponse['errorCode']))
        """
        self.jugada_bitcoincash = jugada.Jugada(self.client, "BITCOINCASH", 30)
        self.jugada_bitcoin = jugada.Jugada(self.client, "BITCOIN", 33)
        self.jugada_etherium = jugada.Jugada(self.client, "ETHEREUM", 33)"""

        
        self.jugada_euro = jugada.Jugada(self.client, "EURUSD", 3300)
        self.jugada_usdjpy = jugada.Jugada(self.client, "USDJPY", 3000)
        self.jugada_cangurousd = jugada.Jugada(self.client, "AUDUSD", 3000)
        self.jugada_eurgbp = jugada.Jugada(self.client, "EURGBP", 3000)
        self.jugada_us500 = jugada.Jugada(self.client, "US500", 3000)
        self.jugada_gold = jugada.Jugada(self.client, "GOLD", 3000)
        self.jugada_eurchf = jugada.Jugada(self.client, "EURCHF", 4000)
        self.jugada_gbpusd = jugada.Jugada(self.client, "GBPUSD", 4000)
        self.jugada_usdchf = jugada.Jugada(self.client, "USDCHF", 4000)
        self.jugada_eurjpy = jugada.Jugada(self.client, "EURJPY", 4000)
        self.jugada_us30 = jugada.Jugada(self.client, "US30", 4000)

            
        #data = client.commandExecute('getProfitCalculation',  dict(closePrice = 1.20615, cmd=0, openPrice = 1.19942, symbol='EURUSD', volume=0.1))
        self.thread.start()  

    def run(self):
        while True:
            tiempo = time.localtime()
            if tiempo.tm_min % 5 == 0 and tiempo.tm_sec < 40 and tiempo.tm_sec > 19 and not self.emas_buscadas:
                balance, patrimonio, nivel_margen = indicadores.obtener_balance_patrimonio_y_nivel_margen(self.client)
                mailError.sendmail("felipe.zxkq@gmail.com", "Bot sin diff ema", "Balance: "+str(balance)+"\nPatrimonio: "+str(patrimonio)+"\nNivel de margen: "+str(nivel_margen))
                self.jugada_euro.obtener_velas_y_emas()
                self.jugada_usdjpy.obtener_velas_y_emas()
                self.jugada_cangurousd.obtener_velas_y_emas()
                
                self.jugada_eurgbp.obtener_velas_y_emas()
                self.jugada_us500.obtener_velas_y_emas()
                self.jugada_gold.obtener_velas_y_emas()
                self.jugada_eurchf.obtener_velas_y_emas()
                self.jugada_gbpusd.obtener_velas_y_emas()
                self.jugada_usdchf.obtener_velas_y_emas()
                self.jugada_eurjpy.obtener_velas_y_emas()
                self.jugada_us30.obtener_velas_y_emas()

                """
                self.jugada_etherium.obtener_velas_y_emas()
                self.jugada_bitcoin.obtener_velas_y_emas()
                self.jugada_bitcoincash.obtener_velas_y_emas()"""
                self.emas_buscadas = True  

            else:
                self.jugada_euro.jugar()
                self.jugada_usdjpy.jugar()
                self.jugada_cangurousd.jugar()
                
                self.jugada_eurgbp.jugar()
                self.jugada_us500.jugar()
                self.jugada_gold.jugar()
                self.jugada_eurchf.jugar()
                self.jugada_gbpusd.jugar()
                self.jugada_usdchf.jugar()
                self.jugada_eurjpy.jugar()
                self.jugada_us30.jugar()

                self.emas_buscadas = False
                """
                self.jugada_etherium.jugar()
                self.jugada_bitcoin.jugar()
                self.jugada_bitcoincash.jugar()"""
            time.sleep(0.01)
        

    def connect_to_stram_api(self):

        pass

bot = Tradebot()
print("caca")
time.sleep(144000)