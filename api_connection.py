import socket
import ssl
import json
import time


class Api_connection():

    def __init__(self, userid: int, password: str):
        self.userid = userid
        self.password = password
        self.host = 'xapia.x-station.eu'
        self.port = 5124
        self.s = socket.socket()
        self.s.connect((self.host, self.port))
        self.s = ssl.wrap_socket(self.s)
        self.stream_session_id = "asd"
        self.stream_api = "a"
        self.login()
        self.connect_streaming_api(self.stream_session_id)
        

    def login(self):
        parameters = {
            "command" : "login",
            "arguments" : {
                "userId": self.userid,
                "password": self.password
            }
        }
        response = self.send_command(parameters = parameters)
        print(response)
        self.stream_session_id = response['streamSessionId']
        print("Session ID: ", self.stream_session_id)
        print('Print login: ', response)

    def connect_streaming_api(self, stream_session_id):
        host = 'xapia.x-station.eu'
        port = 5125
        s = socket.socket()
        s.connect((host, port))
        self.stream_api = ssl.wrap_socket(s)
        parameters = {
            "command" : "getNews",
            "streamSessionId" : stream_session_id
        }
        print(stream_session_id)
        packet = json.dumps(parameters, indent=4)
        self.stream_api.send(packet.encode("UTF-8"))
        response = self.recv_basic()
        #self.stream_api.recv(8192)
        response = json.loads(response)
        print("Streaming response: ", response)


    def recv_basic(self):
        while True:
            print("estoy intentandolo")
            data = ''
            time.sleep(4)
            data = self.stream_api.recv(8192)
            print(data)
            #if data: break
        return data

    def close_connection(self):
        logout = {
            "command" : "logout"
        }
        response = self.send_command(parameters = logout)
        print("Logout: ", response)

    def send_command(self, parameters):
        packet = json.dumps(parameters, indent=4)
        self.s.send(packet.encode("UTF-8"))
        response = self.s.recv(8192)
        response = json.loads(response)
        return response

    def open_position(self, symbol: str, volume: float = 0.1, tp: float = 0.0, sl: float = 0.0):
        presio = self.get_price(symbol)

        # Transaction
        tradetransinfo = {
                "cmd": 0,
                "customComment": "Some text",
                "offset": 0,
                "order": 0,
                "price": presio,
                "sl": sl,
                "symbol": symbol,
                "tp": tp,
                "type": 0,
                "volume": volume
            }
        parameters = {
            "command" : "tradeTransaction",
            "arguments" : {
                "tradeTransInfo" : tradetransinfo
            }
        }

        print("Tradetransaction: ", tradetransinfo)
        print("Parámetros: ", parameters)
        packet = json.dumps(parameters, indent=4)
        self.s.send(packet.encode("UTF-8"))

        response = self.s.recv(8192)
        print('Trade: {}'.format(response))

    def get_price(self, symbol):
        parameters = {
        "command" : "getSymbol",
            "arguments" : {
                "symbol": symbol

            }
        }
        
        response = self.send_command(parameters = parameters)
        print(response)
        presio = response['returnData']['ask']
        print('Datos de ' + symbol + ': ', presio)
        return presio


    def get_candles(self, symbol: str):
        parameters = {
            "command" : "getTickPrices",
            "streamSessionId" : self.stream_session_id,
            "symbol" : symbol
        }
        print(parameters)
        packet = json.dumps(parameters, indent=4)
        self.stream_api.send(packet.encode("UTF-8"))
        while True:
            response = self.stream_api.recv(8192)
            response = json.loads(response)
            print("Candles response: ", response)






