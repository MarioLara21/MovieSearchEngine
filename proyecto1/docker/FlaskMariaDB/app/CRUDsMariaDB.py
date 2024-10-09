import mariadb 
import os 
from flask import Flask, request, jsonify 
from prometheus_client import start_http_server, Counter 
import unittest 
import logging 
 
app = Flask(__name__) 
REQUEST_COUNT = Counter('flask_http_requests', 'Number of HTTP requests received') 
 
# Basado en https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/ 
 
# Conectarse a MariaDB 
def connectMariaDB(): 
    try: 
        conn = mariadb.connect( 
            user= os.environ.get("MDB_USERNAME"), 
            password= os.environ.get("MDB_PASSWORD"), 
            host= os.environ.get("MDB_HOST"), 
            database= os.environ.get("MDB_DATABASE") 
        ) 
        c= os.environ.get("MDB_DATABASE") 
        print(c) 
        print ("Conexión exitosa a MariaDB") 
        return conn 
    except mariadb.Error as e: 
        print(f"Error connecting to MariaDB Platform: {e}") 
        return None 
     
# Crear Base de Datos 
def createDatabase(conn): 
    try: 
        cursor = conn.cursor() 
        db = "estudiantesTEC" 
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db}") # Crear Base de Datos 
        conn.commit()       # Confirmar cambios 
        print ("Base de Datos creada") 
        cursor.close()      # Cerrar cursor 
 
    except mariadb.Error as e: 
        return print(f"Error creating database: {e}") 
 
# Crear Tabla 
def createTable(conn): 
    try: 
        cursor = conn.cursor() 
        tabla = "estudiantes" 
        cursor.execute( # Crear Tabla 
            f"""CREATE TABLE IF NOT EXISTS {tabla}  
            (id INT AUTO_INCREMENT PRIMARY KEY,  
            nombre VARCHAR(100), 
            apellido VARCHAR(100), 
            carnet INT, 
            carrera VARCHAR(100)), 
            edad INT, 
            correo VARCHAR(100)""" 
        )  
        conn.commit()       # Confirmar cambios 
        print ("Tabla creada") 
        cursor.close()      # Cerrar cursor 
 
    except mariadb.Error as e: 
        return print(f"Error creating table: {e}") 
 
# Acceder a columnas de la tabla 
def getColumnas(tabla, cursor): 
    try: 
        cursor.execute(f"DESCRIBE {tabla}") # Acceder a columnas 
        columnas = cursor.fetchall() 
        return columnas 
    except mariadb.Error as e: 
        return print(f"Error getting columns: {e}") 
 
 
# _____ Convertir JSON a SQL query _____ 
 
# Insert 
# Basado en: https://stackoverflow.com/questions/9336270/using-a-python-dict-for-a-sql-insert-statement 
def jsonToInsert(json, columnas): 
    tabla = "estudiantes" 
    conn = connectMariaDB()     # Conectarse a MariaDB 
    cursor = conn.cursor() 
    placeholders = ', '.join(['%s'] * len(json)) 
    sql = f"INSERT INTO {tabla} ({columnas}) VALUES ({placeholders})" 
    cursor.execute(sql, tuple(json.values())) 
    cursor.close()      # Cerrar cursor 
    conn.close()        # Cerrar conexión 
    return print("JSON insertado") 
 
# Update 
def jsonToUpdate(json, idTabla): 
    tabla = "estudiantes" 
    conn = connectMariaDB()     # Conectarse a MariaDB 
    cursor = conn.cursor() 
    set = ', '.join(f'{key} = %s' for key in json) 
    sql = f"UPDATE {tabla} SET {set} WHERE id = %s LIMIT 1" 
    updateValores = list(json.values()) 
    updateValores.append(idTabla) 
    cursor.execute(sql, updateValores) 
    conn.commit()       # Confirmar cambios 
    cursor.close()      # Cerrar cursor 
    conn.close()        # Cerrar conexión 
 
class TestDictToSQLFunctions(unittest.TestCase): 
    def test_dict_to_sql_insert(self): 
        json = { 
            "Id": 1, 
            "Name": "Test", 
            "Type1": "TypeA", 
            "Type2": "TypeB" 
        } 
        result = jsonToInsert(json) 
 
        expected_query = "INSERT INTO estudiantes (`Id`, `nombre`, `apellido`, `canet`, `carrera`, `edad`, `correo`) VALUES (%s, %s, %s, %s, %s, %s, %s)" 
        expected_values = [1, "Test", "TypeA", "TypeB"] 
 
        self.assertEqual(result["insertQuery"], expected_query) 
        self.assertEqual(result["values"], expected_values)     
 
 
# Basado en: https://pythonbasics.org/flask-http-methods/ 
# write 
@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/postEstudiantesTEC", methods=['POST'] )  
def postData(): 
    try: 
        REQUEST_COUNT.inc() 
        datos = request.form.to_dict()   # Analizar el json 
        conn = connectMariaDB()    # Conectarse a MariaDB 
        cursor = conn.cursor() 
        tabla = "estudiantes" 
 
        columnas = getColumnas(tabla, cursor) 
        jsonToInsert(datos, columnas)  # Convertir a SQL query 
        conn.commit()       # Confirmar cambios 
        conn.close()        # Cerrar conexión 
        return print ("Datos insertados") 
     
    except Exception as e: 
        return print(f"Error: {e}") 
 
 # delete 
@app.route("/deleteEstudiantesTEC/<id>", methods=['DELETE'] ) 
def deleteData(id): 
    try: 
        REQUEST_COUNT.inc() 
        conn = connectMariaDB()   # Conectarse a MariaDB 
        cursor = conn.cursor() 
        tabla = "estudiantes" 
 
        # Crear delete query 
        deleteQuery = f"DELETE FROM {tabla} WHERE id = (SELECT Id FROM {tabla} WHERE id = {id} LIMIT 1);" 
        cursor.execute(deleteQuery) # Ejecutar delete query 
        conn.commit()       # Confirmar cambios 
        cursor.close()      # Cerrar cursor 
        conn.close()        # Cerrar conexión 
        return print ("Datos eliminados") 
     
    except Exception as e: 
        return print(f"Error: {e}") 
     
# update 
@app.route("/putEstudiantesTEC/<id>", methods=['PUT']) 
def putData(id): 
    try: 
        REQUEST_COUNT.inc() 
        data = request.form.to_dict()   # Analizar el json 
        conn = connectMariaDB()     # Conectarse a MariaDB 
 
        jsonToUpdate(data, id)  # Convertir a SQL query 
 
        conn.commit()       # Confirmar cambios 
        conn.close()        # Cerrar conexión 
        return print ("Datos actualizados") 
     
    except Exception as e: 
        return print(f"Error: {e}") 
 
 
# read 
@app.route("/getAllEstudiantesTEC", methods=['GET'] ) 
def getAllData(): 
    try: 
        REQUEST_COUNT.inc() 
        conn = connectMariaDB()     # Conectarse a MariaDB 
        cursor = conn.cursor() 
        tabla = "estudiantes" 
        columnas = getColumnas(tabla, cursor) 
        selectQuery = f"SELECT {', '.join(columnas)} FROM {tabla}"  # Crear select query 
 
        cursor.execute(selectQuery) 
        result = cursor.fetchall() 
        cursor.close() 
        conn.commit()       # Confirmar cambios 
        conn.close()        # Cerrar conexión 
        print ("Datos obtenidos") 
        return result 
 
    except Exception as e: 
        return print(f"Error: {e}") 
 
@app.route("/getEstudiantesTEC/<id>", methods=['GET'] ) 
def getData(id): 
    try: 
        REQUEST_COUNT.inc() 
        conn = connectMariaDB()     # Conectarse a MariaDB 
        cursor = conn.cursor() 
        tabla = "estudiantes" 
        columnas = getColumnas(tabla, cursor) 
        selectQuery = f"SELECT {', '.join(columnas)} FROM {tabla} WHERE id = {id}"     # Crear select query 
 
        cursor.execute(selectQuery)  
        result = cursor.fetchone() 
        cursor.close() 
        conn.commit()       # Confirmar cambios 
        conn.close()        # Cerrar conexión 
 
        if result: 
            print ("Datos obtenidos") 
            return result 
        else: 
            return print ("No se encontraron datos") 
 
    except Exception as e: 
        return print(f"Error: {e}") 

 
if __name__ == '__main__':  
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') 
    logger = logging.getLogger(__name__) 
     
     
    conn = connectMariaDB()     # Conectarse a MariaDB 
    createDatabase(conn)        # Crear Base de Datos 
    createTable(conn)           # Crear Tabla 
    conn.close()                # Cerrar conexión 
    print("hola")
    start_http_server(8000)     # Correr flask 
    app.run() 
   # unittest.main()  