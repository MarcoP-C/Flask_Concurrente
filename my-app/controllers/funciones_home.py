# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import threading
import datetime
import re
import os

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio



import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file

# Creamos un objeto Lock para sincronizar el acceso a la conexión a la base de datos
lock = threading.Lock()

def procesar_form_vehiculo(dataForm):
    # Formateando Salario
    #salario_sin_puntos = re.sub('[^0-9]+', '', dataForm['salario_empleado'])
    # Convertir salario a INT
    #salario_entero = int(salario_sin_puntos)

    #result_foto_perfil = procesar_imagen_perfil(foto_perfil)

    resultado_insert = -1  # Valor predeterminado en caso de error

    def ejecutar_procesamiento():
        nonlocal resultado_insert
        try:
            with connectionBD() as conexion_MySQLdb:
                with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                    sql = "INSERT INTO tbl_vehiculos (nombre_duenio, sexo_duenio, marca_auto, modelo_auto, factura, tarjeta_circulacion, email_duenio, foto_duenio) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                    valores = (dataForm['nombre_duenio'], dataForm['sexo_duenio'], dataForm['marca_auto'],
                               dataForm['modelo_auto'], dataForm['factura'], dataForm['tarjeta_circulacion'],dataForm['email_duenio'], dataForm['foto_duenio'])
                    
                    with lock:
                        cursor.execute(sql, valores)
                        conexion_MySQLdb.commit()
                        resultado_insert = cursor.rowcount
        except Exception as e:
            print(f'Se produjo un error en procesar_form_empleado: {str(e)}')

    # Crear un hilo para ejecutar el procesamiento
    thread = threading.Thread(target=ejecutar_procesamiento)
    thread.start()
    thread.join()  # Esperar a que el hilo termine su ejecución

    return resultado_insert


def procesar_imagen_perfil(foto):
    try:
        # Nombre original del archivo
        filename = secure_filename(foto.filename)
        extension = os.path.splitext(filename)[1]

        # Creando un string de 50 caracteres
        nuevoNameFile = (uuid.uuid4().hex + uuid.uuid4().hex)[:100]
        nombreFile = nuevoNameFile + extension

        # Construir la ruta completa de subida del archivo
        basepath = os.path.abspath(os.path.dirname(__file__))
        upload_dir = os.path.join(basepath, f'../static/fotos_empleados/')

        # Validar si existe la ruta y crearla si no existe
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
            # Dando permiso a la carpeta
            os.chmod(upload_dir, 0o755)

        # Construir la ruta completa de subida del archivo
        upload_path = os.path.join(upload_dir, nombreFile)
        foto.save(upload_path)

        return nombreFile

    except Exception as e:
        print("Error al procesar archivo:", e)
        return []


# Lista de Empleados
def sql_lista_vehiculosBD():
    try:
        empleadosBD = None

        def ejecutar_consulta():
            nonlocal empleadosBD
            try:
                with connectionBD() as conexion_MySQLdb:
                    with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                        querySQL = (f"""
                            SELECT 
                                e.id_vehiculo,
                                e.nombre_duenio, 
                                CASE
                                    WHEN e.sexo_duenio = 1 THEN 'Masculino'
                                    ELSE 'Femenino'
                                END AS sexo_duenio,
                                e.marca_auto,
                                e.modelo_auto,
                                e.factura
                                
                            FROM tbl_vehiculos AS e
                            ORDER BY e.id_vehiculo DESC
                            """)
                        cursor.execute(querySQL)
                        empleadosBD = cursor.fetchall()
            except Exception as e:
                print(f"Error en la función sql_lista_empleadosBD: {e}")

        thread = threading.Thread(target=ejecutar_consulta)
        thread.start()
        thread.join()  # Esperar a que el hilo termine su ejecución

        return empleadosBD
    except Exception as e:
        print(f"Error general en sql_lista_empleadosBD: {e}")
        return None


# Detalles del Empleado
def sql_detalles_vehiculosBD(idVehiculo):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        e.id_vehiculo,
                        e.nombre_duenio, 
                        CASE
                            WHEN e.sexo_duenio = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_duenio,
                        e.marca_auto,
                        e.modelo_auto,
                        
                        e.factura, 
                        e.tarjeta_circulacion,
                        e.email_duenio,
                        e.foto_duenio,
                        DATE_FORMAT(e.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro
                    FROM tbl_vehiculos AS e
                    WHERE id_vehiculo =%s
                    ORDER BY e.id_vehiculo DESC
                    """)
                cursor.execute(querySQL, (idVehiculo,))
                empleadosBD = cursor.fetchone()
        return empleadosBD
    except Exception as e:
        print(
            f"Errro en la función sql_detalles_empleadosBD: {e}")
        return None


# Funcion Empleados Informe (Reporte)
def empleadosReporte():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        e.id_empleado,
                        e.nombre_empleado, 
                        e.apellido_empleado,
                        e.salario_empleado,
                        e.email_empleado,
                        e.telefono_empleado,
                        e.profesion_empleado,
                        DATE_FORMAT(e.fecha_registro, '%d de %b %Y %h:%i %p') AS fecha_registro,
                        CASE
                            WHEN e.sexo_empleado = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_empleado
                    FROM tbl_empleados AS e
                    ORDER BY e.id_empleado DESC
                    """)
                cursor.execute(querySQL,)
                empleadosBD = cursor.fetchall()
        return empleadosBD
    except Exception as e:
        print(
            f"Errro en la función empleadosReporte: {e}")
        return None


def generarReporteExcel():
    dataEmpleados = empleadosReporte()
    wb = openpyxl.Workbook()
    hoja = wb.active

    # Agregar la fila de encabezado con los títulos
    cabeceraExcel = ("Nombre", "Apellido", "Sexo",
                     "Telefono", "Email", "Profesión", "Salario", "Fecha de Ingreso")

    hoja.append(cabeceraExcel)

    # Formato para números en moneda colombiana y sin decimales
    formato_moneda_colombiana = '#,##0'

    # Agregar los registros a la hoja
    for registro in dataEmpleados:
        nombre_empleado = registro['nombre_empleado']
        apellido_empleado = registro['apellido_empleado']
        sexo_empleado = registro['sexo_empleado']
        telefono_empleado = registro['telefono_empleado']
        email_empleado = registro['email_empleado']
        profesion_empleado = registro['profesion_empleado']
        salario_empleado = registro['salario_empleado']
        fecha_registro = registro['fecha_registro']

        # Agregar los valores a la hoja
        hoja.append((nombre_empleado, apellido_empleado, sexo_empleado, telefono_empleado, email_empleado, profesion_empleado,
                     salario_empleado, fecha_registro))

        # Itera a través de las filas y aplica el formato a la columna G
        for fila_num in range(2, hoja.max_row + 1):
            columna = 7  # Columna G
            celda = hoja.cell(row=fila_num, column=columna)
            celda.number_format = formato_moneda_colombiana

    fecha_actual = datetime.datetime.now()
    archivoExcel = f"Reporte_empleados_{fecha_actual.strftime('%Y_%m_%d')}.xlsx"
    carpeta_descarga = "../static/downloads-excel"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    if not os.path.exists(ruta_descarga):
        os.makedirs(ruta_descarga)
        # Dando permisos a la carpeta
        os.chmod(ruta_descarga, 0o755)

    ruta_archivo = os.path.join(ruta_descarga, archivoExcel)
    wb.save(ruta_archivo)

    # Enviar el archivo como respuesta HTTP
    return send_file(ruta_archivo, as_attachment=True)


def buscarEmpleadoBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            e.id_vehiculo,
                            e.nombre_duenio, 
                            CASE
                                WHEN e.sexo_duenio = 1 THEN 'Masculino'
                                ELSE 'Femenino'
                            END AS sexo_duenio,
                            e.marca_auto,
                            e.modelo_auto
                            
                        FROM tbl_vehiculos AS e
                        WHERE e.nombre_duenio LIKE %s 
                        ORDER BY e.id_vehiculo DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoBD: {e}")
        return []


def buscarEmpleadoUnico(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            e.id_empleado,
                            e.nombre_empleado, 
                            e.apellido_empleado,
                            e.sexo_empleado,
                            e.telefono_empleado,
                            e.email_empleado,
                            e.profesion_empleado,
                            e.salario_empleado,
                            e.foto_empleado
                        FROM tbl_empleados AS e
                        WHERE e.id_empleado =%s LIMIT 1
                    """)
                mycursor.execute(querySQL, (id,))
                empleado = mycursor.fetchone()
                return empleado

    except Exception as e:
        print(f"Ocurrió un error en def buscarEmpleadoUnico: {e}")
        return []


def procesar_actualizacion_form(data):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                nombre_empleado = data.form['nombre_empleado']
                apellido_empleado = data.form['apellido_empleado']
                sexo_empleado = data.form['sexo_empleado']
                telefono_empleado = data.form['telefono_empleado']
                email_empleado = data.form['email_empleado']
                profesion_empleado = data.form['profesion_empleado']

                salario_sin_puntos = re.sub(
                    '[^0-9]+', '', data.form['salario_empleado'])
                salario_empleado = int(salario_sin_puntos)
                id_empleado = data.form['id_empleado']

                if data.files['foto_empleado']:
                    file = data.files['foto_empleado']
                    fotoForm = procesar_imagen_perfil(file)

                    querySQL = """
                        UPDATE tbl_empleados
                        SET 
                            nombre_empleado = %s,
                            apellido_empleado = %s,
                            sexo_empleado = %s,
                            telefono_empleado = %s,
                            email_empleado = %s,
                            profesion_empleado = %s,
                            salario_empleado = %s,
                            foto_empleado = %s
                        WHERE id_empleado = %s
                    """
                    values = (nombre_empleado, apellido_empleado, sexo_empleado,
                              telefono_empleado, email_empleado, profesion_empleado,
                              salario_empleado, fotoForm, id_empleado)
                else:
                    querySQL = """
                        UPDATE tbl_empleados
                        SET 
                            nombre_empleado = %s,
                            apellido_empleado = %s,
                            sexo_empleado = %s,
                            telefono_empleado = %s,
                            email_empleado = %s,
                            profesion_empleado = %s,
                            salario_empleado = %s
                        WHERE id_empleado = %s
                    """
                    values = (nombre_empleado, apellido_empleado, sexo_empleado,
                              telefono_empleado, email_empleado, profesion_empleado,
                              salario_empleado, id_empleado)

                cursor.execute(querySQL, values)
                conexion_MySQLdb.commit()

        return cursor.rowcount or []
    except Exception as e:
        print(f"Ocurrió un error en procesar_actualizacion_form: {e}")
        return None


# Lista de Usuarios creados
def lista_usuariosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "SELECT id, name_surname, email_user, created_user FROM users"
                cursor.execute(querySQL,)
                usuariosBD = cursor.fetchall()
        return usuariosBD
    except Exception as e:
        print(f"Error en lista_usuariosBD : {e}")
        return []


# Eliminar uEmpleado
# def eliminarVehiculo(id_vehiculo, foto_duenio):
#     try:
#         with connectionBD() as conexion_MySQLdb:
#             with conexion_MySQLdb.cursor(dictionary=True) as cursor:
#                 querySQL = "DELETE FROM tbl_vehiculos WHERE id_vehiculo=%s"
#                 cursor.execute(querySQL, (id_vehiculo,))
#                 conexion_MySQLdb.commit()
#                 resultado_eliminar = cursor.rowcount

#                 if resultado_eliminar:
#                     # Eliminadon foto_empleado desde el directorio
#                     basepath = path.dirname(__file__)
#                     url_File = path.join(
#                         basepath, '../static/fotos_empleados', foto_duenio)

#                     if path.exists(url_File):
#                         remove(url_File)  # Borrar foto desde la carpeta

#         return resultado_eliminar
#     except Exception as e:
#         print(f"Error en eliminarEmpleado : {e}")
#         return []

def eliminarVehiculo(id_vehiculo):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_vehiculos WHERE id_vehiculo=%s"
                cursor.execute(querySQL, (id_vehiculo,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

        if resultado_eliminar > 0:
            return resultado_eliminar
        else:
            return -1  # Devolver un valor que indique que no se eliminó ningún registro
    except Exception as e:
        print(f"Error en eliminarVehiculo: {e}")
        raise  # Relanzar la excepción para que la vista de Flask pueda manejarla



    

# Eliminar usuario
def eliminarUsuario(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM users WHERE id=%s"
                cursor.execute(querySQL, (id,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarUsuario : {e}")
        return []












