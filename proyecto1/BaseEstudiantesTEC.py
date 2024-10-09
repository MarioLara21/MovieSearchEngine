import mariadb 
# Basado en https://mariadb.com/resources/blog/how-to-connect-python-programs-to-mariadb/ 
 
# Conectarse a MariaDB 
def connectMariaDB(): 
    try: 
        conn = mariadb.connect( 
            user= "root",
            password= "1234", 
            host= "127.0.0.1", 
            port= 3307
        )
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
def createTabla(conn): 
    try: 
        cursor = conn.cursor() 
        db = "estudiantesTEC"
        tabla = "estudiantes" 
        
        # Primero seleccionamos la base de datos
        cursor.execute(f"USE {db}")

        # Luego creamos la tabla
        cursor.execute(                               
            f"""CREATE TABLE IF NOT EXISTS {tabla}  
            (id INT AUTO_INCREMENT PRIMARY KEY,  
            nombre VARCHAR(100), 
            apellido VARCHAR(100), 
            carnet INT, 
            carrera VARCHAR(100), 
            edad INT, 
            correo VARCHAR(100))""" 
        )  
        conn.commit()       # Confirmar cambios 
        print("Tabla creada") 
        cursor.close()      # Cerrar cursor 

    except mariadb.Error as e: 
        return print(f"Error creating table: {e}")

def createTabla2(conn): 
    try: 
        cursor = conn.cursor() 
        db = "estudiantesTEC"
        tabla = "carro" 
        
        # Primero seleccionamos la base de datos
        cursor.execute(f"USE {db}")

        # Luego creamos la tabla
        cursor.execute(                               
            f"""CREATE TABLE IF NOT EXISTS {tabla}  
            (id INT AUTO_INCREMENT PRIMARY KEY,  
            descripcion VARCHAR(250), 
            id_estudiante INT, 
            FOREIGN KEY (id_estudiante) REFERENCES estudiantes(id))""" 
        )  
        conn.commit()       # Confirmar cambios 
        print("Tabla creada2") 
        cursor.close()      # Cerrar cursor 

    except mariadb.Error as e: 
        return print(f"Error creating table: {e}")
# Llenar Tabla
def llenarTabla(conn):
    try:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO estudiantes (nombre, apellido, carnet, carrera, edad, correo) 
            VALUES ('Juan', 'Perez', 2020123456, 'Ingenieria en Computacion', 32, 'juperez@estudiantec.cr')""")
        cursor.execute(
            """INSERT INTO estudiantes (nombre, apellido, carnet, carrera, edad, correo) 
            VALUES ('Pablo', 'Chacón', 2021123456, 'Ingenieria en Computacion', 21, 'pachacon@estudiantec.cr')""")
        
        conn.commit()
        cursor.execute(
        """INSERT INTO carro (descripcion, id_estudiante) 
        VALUES ('Toyota Corolla Cross BWC166, Blanco Perlado', (SELECT id FROM estudiantes WHERE nombre = 'Juan'))"""
        )

        cursor.execute(
        """INSERT INTO carro (descripcion, id_estudiante) 
        VALUES ('Honda CRV HUJ-987, Dorado', (SELECT id FROM estudiantes WHERE nombre = 'Pablo'))"""
        )
        print("Tabla llenada")
        cursor.close()

    except mariadb.Error as e:
        return print(f"Error filling table: {e}")
    
# Cerrar conexión
def cerrarConexion(conn):
    try:
        conn.close()
    except mariadb.Error as e:
        return print(f"Error closing MariaDB connection: {e}")
 
conn = connectMariaDB()
createDatabase(conn)
createTabla(conn)
createTabla2(conn)
llenarTabla(conn)
cerrarConexion(conn)