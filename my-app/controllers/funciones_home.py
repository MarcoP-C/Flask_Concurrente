
# Para subir archivo tipo foto al servidor
from werkzeug.utils import secure_filename
import uuid  # Modulo de python para crear un string

from conexion.conexionBD import connectionBD  # Conexión a BD

import datetime
import re
import os

from flask import send_file
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from os import remove  # Modulo  para remover archivo
from os import path  # Modulo para obtener la ruta o directorio


import openpyxl  # Para generar el excel
# biblioteca o modulo send_file para forzar la descarga
from flask import send_file


def procesar_form_vehiculo(dataForm, foto_perfil):
    # Formateando Salario
    salario_sin_puntos = re.sub('[^0-9]+', '', dataForm['salario_empleado'])
    # convertir salario a INT
    salario_entero = int(salario_sin_puntos)

    result_foto_perfil = procesar_imagen_perfil(foto_perfil)
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:

                sql = "INSERT INTO tbl_empleados (nombre_empleado, apellido_empleado, sexo_empleado, telefono_empleado, email_empleado, profesion_empleado, foto_empleado, salario_empleado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

                # Creando una tupla con los valores del INSERT
                valores = (dataForm['nombre_empleado'], dataForm['apellido_empleado'], dataForm['sexo_empleado'],
                           dataForm['telefono_empleado'], dataForm['email_empleado'], dataForm['profesion_empleado'], result_foto_perfil, salario_entero)
                cursor.execute(sql, valores)

                conexion_MySQLdb.commit()
                resultado_insert = cursor.rowcount
                return resultado_insert

    except Exception as e:
        return f'Se produjo un error en procesar_form_empleado: {str(e)}'


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


# Lista de vehiculos

def sql_lista_vehiculosBD():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = (f"""
                    SELECT 
                        v.id_vehiculo,
                        v.nombre_duenio, 
                        v.sexo_duenio,
                        v.marca_auto,
                        v.modelo_auto,
                        v.factura,
                        v.tarjeta_circulacion,
                        v.email_duenio,
                        v.foto_duenio,
                        v.fecha_registro        
                    FROM tbl_vehiculos AS v
                    ORDER BY v.id_vehiculo DESC
                    """)
                cursor.execute(querySQL,)
                vehiculosBD = cursor.fetchall()
        return vehiculosBD
    except Exception as e:
        print(
            f"Errro en la función sql_lista_vehiculosBD: {e}")
        return None


# Detalles del Empleado
def sql_detalles_vehiculoBD(idVehiculo):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                        v.id_vehiculo,
                        v.nombre_duenio, 
                        v.marca_auto,
                        v.modelo_auto,
                        CASE
                            WHEN v.sexo_duenio = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_duenio,
                        v.factura, 
                        v.tarjeta_circulacion,
                        v.email_duenio,
                        v.foto_duenio,
                        DATE_FORMAT(v.fecha_registro, '%Y-%m-%d %h:%i %p') AS fecha_registro
                    FROM tbl_vehiculos AS v
                    WHERE v.id_vehiculo =%s
                    ORDER BY v.id_vehiculo DESC
                    """)
                cursor.execute(querySQL, (idVehiculo))
                vehiculosBD = cursor.fetchone()
        return vehiculosBD
    except Exception as e:
        print(  
            f"Errro en la función sql_detalles_vehiculosBD: {e}")
        return None


# Funcion Empleados Informe (Reporte)
def veiculosReporte():
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = ("""
                    SELECT 
                         v.id_vehiculo,
                        v.nombre_duenio, 
                        v.marca_auto,
                        v.modelo_auto,
                        v.factura, 
                        v.tarjeta_circulacion,
                        v.email_duenio,
                        DATE_FORMAT(v.fecha_registro, '%d de %b %Y %h:%i %p') AS fecha_registro,
                        CASE
                            WHEN v.sexo_duenio = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                        END AS sexo_duenio
                    FROM tbl_vehiculos AS v
                    ORDER BY v.id_vehiculo DESC
                    """)
                cursor.execute(querySQL,)
                vehiculosBD = cursor.fetchall()
        return vehiculosBD
    except Exception as e:
        print(
            f"Errro en la función vehiculosReporte: {e}")
        return None


def generarReportePDF():
    dataEmpleados = veiculosReporte()

    # Crear el archivo PDF
    fecha_actual = datetime.datetime.now()
    archivoPDF = f"Reporte_Vehiculos_{fecha_actual.strftime('%Y_%m_%d')}.pdf"
    carpeta_descarga = "../static/downloads-pdf"
    ruta_descarga = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), carpeta_descarga)

    try:
        os.makedirs(ruta_descarga)
        os.chmod(ruta_descarga, 0o755)
    except FileExistsError:
        pass

    ruta_archivo_pdf = os.path.join(ruta_descarga, archivoPDF)
    pdf = canvas.Canvas(ruta_archivo_pdf, pagesize=letter)

    # Configurar el tamaño de la fuente y otros estilos según sea necesario
    pdf.setFont("Helvetica", 12)

    # Establecer las posiciones iniciales de las columnas y las filas
    col_width = 200
    row_height = 20
    margin = 50
    x = margin
    y = 750

    # Agregar los registros al PDF
    for registro in dataEmpleados:
        for titulo, valor in (("Propietario", registro['nombre_duenio']),
                              ("Sexo", registro['sexo_duenio']),
                              ("Marca Vehiculo", registro['marca_auto']),
                              ("Modelo Vehiculo", registro['modelo_auto']),
                              ("Factura", registro['factura']),
                              ("Tarjeta de Circulacion", registro['tarjeta_circulacion']),
                              ("Correo Electronico", registro['email_duenio']),
                              ("Fecha de Registro", registro['fecha_registro'])):
            pdf.drawString(x, y, f"{titulo}:")
            pdf.drawString(x + col_width, y, f"{valor}")
            y -= row_height

        # Agregar espacio entre registros
        y -= row_height

    # Guardar y cerrar el PDF
    pdf.save()

    # Enviar el archivo PDF como respuesta HTTP
    return send_file(ruta_archivo_pdf, as_attachment=True)

def buscarVehiculoBD(search):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            v.id_vehiculo,
                            v.nombre_duenio, 
                            v.marca_auto,
                            v.modelo_auto,
                           CASE
                            WHEN v.sexo_duenio = 1 THEN 'Masculino'
                            ELSE 'Femenino'
                            END AS sexo_duenio
                        FROM tbl_vehiculos AS v
                        WHERE  v.nombre_duenio LIKE %s 
                        ORDER BY v.id_vehiculo DESC
                    """)
                search_pattern = f"%{search}%"  # Agregar "%" alrededor del término de búsqueda
                mycursor.execute(querySQL, (search_pattern,))
                resultado_busqueda = mycursor.fetchall()
                return resultado_busqueda

    except Exception as e:
        print(f"Ocurrió un error en def buscarVehiculoBD: {e}")
        return []



def buscarVehiculoUnico(id):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as mycursor:
                querySQL = ("""
                        SELECT 
                            v.id_vehiculo,
                            v.nombre_duenio, 
                            v.marca_auto,
                            v.modelo_auto,
                            v.sexo_duenio
                            v.factura, 
                            v.tarjeta_circulacion,
                            v.email_duenio,
                            v.foto_duenio,
                        FROM tbl_vehiculos AS v
                        WHERE v.id_vehiculo =%s LIMIT 1
                    """)
                mycursor.execute(querySQL, (id,))
                vehiculo = mycursor.fetchone()
                return vehiculo

    except Exception as e:
        print(f"Ocurrió un error en def buscarVehiculoUnico: {e}")
        return []
        


def procesar_actualizacion_form(data):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                nombre_duenio = data.form['nombre_duenio']
                sexo_duenio = data.form['sexo_duenio']
                marca_auto = data.form['marca_auto']
                modelo_auto = data.form['modelo_auto']
                factura = data.form['factura']
                tarjeta_circulacion = data.form['tarjeta_circulacion']
                email_duenio = data.form['email_duenio']
                foto_duenio = data.form['foto_duenio']

                # salario_sin_puntos = re.sub(
                #     '[^0-9]+', '', data.form['salario_empleado'])
                # salario_empleado = int(salario_sin_puntos)
                # id_empleado = data.form['id_empleado']

                if data.files['foto_empleado']:
                    file = data.files['foto_vehiculo']
                    fotoForm = procesar_imagen_perfil(file)

                    querySQL = """
                        UPDATE tbl_vehiculos
                        SET 
                            nombre_duenio = %s,
                            sexo_duenio = %s,
                            marca_auto = %s,
                            modelo_auto = %s,
                            factura = %s,
                            tarjeta_circulacion = %s,
                            email_duenio = %s,
                            foto_duenio = %s
                        WHERE id_vehiculo = %s
                    """
                    values = (nombre_duenio, sexo_duenio, marca_auto, modelo_auto,
                    factura, tarjeta_circulacion, email_duenio, foto_duenio)
                else:
                    querySQL = """
                        UPDATE tbl_vehiculos
                        SET 
                            nombre_duenio = %s,
                            sexo_duenio = %s,
                            marca_auto = %s,
                            modelo_auto = %s,
                            factura = %s,
                            tarjeta_circulacion = %s,
                            email_duenio = %s,
                            foto_duenio = %s
                        WHERE id_vehiculo = %s
                    """
                    values = (nombre_duenio, sexo_duenio, marca_auto, modelo_auto,
                    factura, tarjeta_circulacion, email_duenio, foto_duenio)

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

def eliminarVehiculo(id_vehiculo, foto_duenio):
    try:
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
                querySQL = "DELETE FROM tbl_vehiculos WHERE id_vehiculo=%s"
                cursor.execute(querySQL, (id_vehiculo,))
                conexion_MySQLdb.commit()
                resultado_eliminar = cursor.rowcount

                if resultado_eliminar:
                    # Eliminadon foto_duenio desde el directorio
                    basepath = path.dirname(__file__)
                    url_File = path.join(
                        basepath, '../static/foto_duenio', foto_duenio)

                    if path.exists(url_File):
                        remove(url_File)  # Borrar foto desde la carpeta

        return resultado_eliminar
    except Exception as e:
        print(f"Error en eliminarVehiculo : {e}")
        return []


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
    
