# Importando Libreria mysql.connector para conectar Python con MySQL
import mysql.connector

def connectionBD():
    try:
        # Crear la conexión
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="123456",  # Reemplaza "tu_contraseña" con la contraseña real
            database="crud_python",
            port="3306",
            collation='utf8mb4_general_ci',
            raise_on_warnings=True
        )

        # Comprobar si la conexión está establecida
        if connection.is_connected():
            print("Conexión exitosa a la BD")

            # Retornar solo la conexión
            return connection

    except mysql.connector.Error as error:
        print(f"No se pudo conectar: {error}")
        # Retornar None en caso de error
        return None

# Ejemplo de uso
conexion = connectionBD()

# Verificar si la conexión fue exitosa antes de crear el cursor
if conexion:
    # Crear un cursor
    cursor = conexion.cursor(dictionary=True)

    # Ahora puedes usar la conexión y el cursor según tus necesidades
    # ...

    # No olvides cerrar la conexión y el cursor cuando hayas terminado
    cursor.close()
    conexion.close()
else:
    print("Hubo un error al conectar a la base de datos.")

