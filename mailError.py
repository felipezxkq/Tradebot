import sys, os
import smtplib


# cuando ocurre una exception que impide el funcionamiento el programa, esta función envía un mail a los administradores con
# un mensaje customizado de error, uno de la exception, el nombre del programa y la línea exacta donde ocurrió
def enviar_error(destinatario, problem, excepcion):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

    mens_excepcion = str(exc_type) + "\n"  + str(fname) + " linea: " + str(exc_tb.tb_lineno) + "\nException: " + str(excepcion)
    #mens_excepcion = "hola"

    sendmail(destinatario, problem, mens_excepcion)


def sendmail(para, titulo, mensaje_exception):
    TO = para
    SUBJECT = titulo
    TEXT = mensaje_exception

    # Gmail Sign In
    gmail_sender = 'cartpy.soporte@gmail.com'
    gmail_passwd = 'cartpy2019'

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_sender, gmail_passwd)

        BODY = '\r\n'.join(['To: %s' % TO,
                            'From: %s' % gmail_sender,
                            'Subject: %s' % SUBJECT,
                            '', TEXT])

    
        server.sendmail(gmail_sender, [TO], BODY)
        print ('Email enviado')
    except Exception as e:
        print ('Error al enviar email')
        print(e)
    server.quit()