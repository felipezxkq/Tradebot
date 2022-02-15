import mysql 
import cuentas


def connexion():
    
    try:
        cnx = mysql.connector.connect( **cuentas.datosDeConexionMySQL)

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("algo esta mal con el nombre de usuario o contraseña")
        elif erro.errno == errorcode.ER_BAD_DB_ERROR:
            print("la Base de Datos no existe")
        else:
            print(err)
    else:
        return cnx
    

def desconectar(cnx):
    cnx.close()