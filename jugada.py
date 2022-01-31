import xAPIConnector
import pandas as pd
import strategy
import indicadores, mailError
import time


class Jugada(object):
    
    def __init__(self, client, symbol, volumen_minimo):
        self.symbol = symbol
        self.client = client
        self.volumen_minimo = volumen_minimo
        self.vol_signal = False
        self.emas_buscadas = False
        self.posicion_abierta = False
        self.stop_loss = 0
        self.ultimo_precio = 0
        self.numerito_de_cerrar = 0
        self.tipo_posicion = 0   # 0 para compra y 1 para venta
        ultimo_5, ultimo_20, ultimo_200, ultimo_precio, ultimo_vol = indicadores.obtener_emas(self.client, self.symbol)
        self.supera_techo_o_piso = False
        self.titulo_correo = ""

 
        print("Ultimo precio: ", ultimo_precio)
        emas_dict = dict(ema_5= ultimo_5, ema_20= ultimo_20)
        self.emas_anteriores = dict(sorted(emas_dict.items(), key=lambda item: item[1]))
        print("Emas anteriores: ", self.emas_anteriores)
        self.margen_symbol = strategy.obtener_margen_symbol(symbol, self.client)

        self.mercado_actual = strategy.tipo_de_mercado(ultimo_200, ultimo_precio)
        self.obtener_velas_y_emas()

    def jugar(self):
        if not self.posicion_abierta:
            diferencia_sl, ultimo_precio, ultimo_200, self.emas_actuales = indicadores.obtener_emas_cambiantes_por_seg(self.client, self.symbol, self.ultimas_velas)
            if ultimo_200 < ultimo_precio:  # Mercado alcista
                self.mercado_alcista = True
            else:
                self.mercado_alcista = False
            
            self.vol_signal = False
            if self.ultimo_vol > self.volumen_minimo:
                self.vol_signal = True

            
            self.mercado_actual = self.movimiento_emas(ultimo_precio, ultimo_200, self.mercado_actual, diferencia_sl)

        elif self.posicion_abierta:
            precio_compra, precio_venta = indicadores.precios_symbol(self.symbol, self.client)
            self.mover_numerito_segun_spread_ganancia(precio_compra, precio_venta)
            if self.tipo_posicion == 0:
                if self.supera_techo_o_piso and precio_venta < self.numerito_de_cerrar:
                    self.cerrar_posicion(precio_venta, motivo_cierre="Techo o piso")
                if not self.supera_techo_o_piso and precio_venta > self.techo and self.techo > self.precio_apertura:
                    self.supera_techo_o_piso = True
                    self.numerito_de_cerrar = self.techo
                    mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "Se supera techo, numerito queda en: "+str(self.numerito_de_cerrar))
                if precio_venta <= self.stop_loss:
                    self.cerrar_posicion(precio_venta, motivo_cierre="SL alcanzado")
                    return
                if self.precio_apertura <= precio_venta and precio_venta <= self.numerito_de_cerrar:
                    self.cerrar_posicion(precio_venta, motivo_cierre="Numerito alcanzado post spread")
                
            else:
                if self.supera_techo_o_piso and precio_compra > self.numerito_de_cerrar:
                    self.cerrar_posicion(precio_compra, motivo_cierre="Techo o piso")
                if not self.supera_techo_o_piso and precio_compra < self.piso and self.piso < self.precio_apertura:
                    self.supera_techo_o_piso = True
                    self.numerito_de_cerrar = self.piso
                    mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "Se supera techo, numerito queda en: "+str(self.numerito_de_cerrar))
                if precio_compra >= self.stop_loss:
                    self.cerrar_posicion(precio_compra, motivo_cierre="SL alcanzado")
                    return
                if self.precio_apertura >= precio_compra and precio_compra >= self.numerito_de_cerrar:  # Usa numerito para cerrar solo si es que hay ganancia
                    self.cerrar_posicion(precio_compra, motivo_cierre="Numerito alcanzado post spread")

        else:
            pass

    def obtener_velas_y_emas(self):
        self.ultimo_vol, self.ultimas_velas, ultima_vela = indicadores.obtener_velas_anteriores(self.client, self.symbol)

        # Obtiene los pisos y techos de las velas de las últimas 12 horas (pensando en cambiarlo a solo las últimas 6 horas)
        self.piso = min(self.ultimas_velas[-144:])
        self.techo = max(self.ultimas_velas[-144:])

        ultimo_5, ultimo_20, ultimo_200, ultimo_precio, ultimo_vol = indicadores.obtener_emas(self.client, self.symbol)
        emas_dict = dict(ema_5= ultimo_5, ema_20= ultimo_20)
        self.emas_anteriores = dict(sorted(emas_dict.items(), key=lambda item: item[1]))
        
        if self.posicion_abierta:
            if self.tipo_posicion == 0:
                if ultima_vela['open'] < ultima_vela['open'] + ultima_vela['close']:# Si es que la vela es verde
                    mecha, orden = indicadores.convertir_al_mismo_orden_de_magnitud(self.ultimo_precio, ultima_vela['open'] + ultima_vela['low'])
                    if mecha > self.numerito_de_cerrar:
                        self.numerito_de_cerrar = mecha

                elif ultima_vela['open'] + ultima_vela['close'] < ultima_vela['open']:  # Si la vela es roja
                    cierre_vela, orden = indicadores.convertir_al_mismo_orden_de_magnitud(self.ultimo_precio, ultima_vela['open'] + ultima_vela['close'])
                    if cierre_vela < self.numerito_de_cerrar:
                        self.cerrar_posicion(motivo_cierre="Numerito")
                print("El numerito quedó: ", self.numerito_de_cerrar)
                mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "El numerito quedo: "+str(self.numerito_de_cerrar)+"\nLa vela es: "+str(ultima_vela)+"\n Techo:"+str(self.techo))
            elif self.tipo_posicion == 1:
                if ultima_vela['open'] > ultima_vela['open'] + ultima_vela['close']:# Si es que la vela es roja
                    mecha, orden = indicadores.convertir_al_mismo_orden_de_magnitud(self.ultimo_precio, ultima_vela['open'] + ultima_vela['high'])
                    if mecha < self.numerito_de_cerrar:
                        self.numerito_de_cerrar = mecha

                elif ultima_vela['open'] + ultima_vela['close'] > ultima_vela['open']:  # Si la vela es verde
                    cierre_vela, orden = indicadores.convertir_al_mismo_orden_de_magnitud(self.ultimo_precio, ultima_vela['open'] + ultima_vela['close'])
                    if cierre_vela > self.numerito_de_cerrar:
                        self.cerrar_posicion(motivo_cierre="Numerito")
                print("El numerito quedó: ", self.numerito_de_cerrar)
                mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "El numerito quedo: "+str(self.numerito_de_cerrar) + "\nLa vela es: "+str(ultima_vela)+"\n Piso:"+str(self.piso))

            

    def movimiento_emas(self, ultimo_precio, ultimo_200, mercado_anterior, diferencia_sl):
        self.emas_anteriores_l = list(self.emas_anteriores.keys())
        self.emas_actuales_l = list(self.emas_actuales.keys())
        mercado_actual = indicadores.tipo_de_mercado(ultimo_200, ultimo_precio)  # True = Alcista, False = Bajista
        print("Ultimo 200 y ultimo precio: "+str(ultimo_200)+"    "+str(ultimo_precio))
        print("Mercado actual: ", mercado_actual)

        precio_compra, precio_venta = indicadores.precios_symbol(self.symbol, self.client)
        if mercado_anterior != mercado_actual and self.posicion_abierta:
            self.cerrar_posicion(precio_venta, motivo_cierre="Cambio de mercado")
        margen_libre = indicadores.obtener_margen_libre(self.client)
        #vol = indicadores.cuanto_comprar(margen_libre, indicadores.obtener_margen_symbol(self.symbol, self.client))

        cumple_condiciones_cruce = indicadores.cumple_condiciones_cruce_ema(mercado_actual, self.emas_anteriores, self.emas_actuales, ultimo_200)
        if mercado_actual and cumple_condiciones_cruce:
            if self.emas_anteriores_l[0] == "ema_5" and self.emas_actuales_l[1] == "ema_5" and self.vol_signal:
                self.stop_loss = indicadores.encontrar_sl(precio_venta, diferencia_sl, True, abs(precio_venta-precio_compra))
                self.ultimo_precio = precio_venta
                
                self.client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd=0, offset=0, order=0, price=precio_compra, sl=0, symbol=self.symbol, tp=0.0, type=0, volume=0.01)))
                if indicadores.verifica_transaccion(self.symbol, self.client):
                    self.posicion_abierta = True
                    self.precio_apertura = precio_compra
                    self.tipo_posicion = 0
                    self.numerito_de_cerrar = self.stop_loss
                    tiempo = time.localtime()
                    self.titulo_correo = "2Abre compra de "+self.symbol + " a las: " + str(tiempo.tm_hour)+ " : "+str(tiempo.tm_min)+" : " +str(tiempo.tm_sec)
                mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "EMAs anteriores"+str(self.emas_anteriores) + "\nEMAs actuales: " + str(self.emas_actuales)
                + "\nSL: " +str(self.ultimo_precio-diferencia_sl) + "\n Ultimo 200: "+str(ultimo_200)+ " Precio apertura: "+str(self.precio_apertura))
        
        elif not mercado_actual and cumple_condiciones_cruce:
            if self.emas_actuales_l[0] == "ema_5" and self.emas_anteriores_l[1] == "ema_5" and self.vol_signal:
                self.stop_loss = indicadores.encontrar_sl(precio_compra, diferencia_sl, False, abs(precio_venta-precio_compra))
                self.ultimo_precio = precio_compra
                self.client.commandExecute('tradeTransaction',  dict(tradeTransInfo = dict(cmd=1, offset=0, order=0, price=precio_venta, sl=0, symbol=self.symbol, tp=0.0, type=0, volume=0.01)))
                print("Cambiaron de lugar, shortear")  # Orden de venta
                if indicadores.verifica_transaccion(self.symbol, self.client):
                    self.posicion_abierta = True
                    self.precio_apertura = precio_venta
                    self.tipo_posicion = 1
                    self.numerito_de_cerrar = self.stop_loss
                    tiempo = time.localtime()
                    self.titulo_correo = "2Abre venta de "+self.symbol + " a las: " + str(tiempo.tm_hour)+ " : "+str(tiempo.tm_min)+" : " +str(tiempo.tm_sec)
                mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "EMAS anteriores: " + str(self.emas_anteriores) + "\nEMAas actuales: " + str(self.emas_actuales)
                + "\nSL: " +str(self.stop_loss) + "\nTransaccion fue abierta correctamente: "+str(self.posicion_abierta) + "\n Ultimo 200: "+str(ultimo_200)
                + " Precio apertura: "+str(self.precio_apertura))

        return mercado_actual

    def cerrar_posicion(self, precio_cierre= None, motivo_cierre= None):
        indicadores.cerrar_transacciones(self.symbol, self.client)
        self.posicion_abierta = False
        self.supera_techo_o_piso = False
        mailError.sendmail("felipe.zxkq@gmail.com", self.titulo_correo, "Se ha cerrado posicion en: "+str(precio_cierre)+"\nMotivo de cierre: "+str(motivo_cierre))

    def mover_numerito_segun_spread_ganancia(self, precio_compra, precio_venta):
        spread = abs(precio_compra-precio_venta)
        if self.tipo_posicion == 0:
            if precio_venta >= self.precio_apertura + 2*spread:
                nuevo_numerito = precio_venta - spread
                if nuevo_numerito > self.numerito_de_cerrar:
                    self.numerito_de_cerrar = nuevo_numerito
        else:
            if precio_compra <= self.precio_apertura - 2*spread:
                nuevo_numerito = precio_compra + spread
                if nuevo_numerito < self.numerito_de_cerrar:
                    self.numerito_de_cerrar = nuevo_numerito


        