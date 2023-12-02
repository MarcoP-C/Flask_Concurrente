from app import app
from flask import render_template, request, flash, redirect, url_for, session,  jsonify
from mysql.connector.errors import Error


# Importando cenexión a BD
from controllers.funciones_home import *

PATH_URL = "public/vehiculos"


@app.route('/registrar-vehiculo', methods=['GET'])
def viewFormVehiculo():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/form_vehiculo.html')
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route('/form-registrar-vehiculo', methods=['POST'])
def formVehiculo():
    if 'conectado' in session:
        
            resultado = procesar_form_vehiculo(request.form)
            if resultado > 0:  # Verifica si se insertó al menos una fila en la base de datos
                return redirect(url_for('lista_vehiculos'))
            else:
                flash('El vehiculo NO fue registrado.', 'error')
                return render_template(f'{PATH_URL}/form_vehiculo.html')
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))



@app.route('/lista-de-vehiculos', methods=['GET'])
def lista_vehiculos():
    if 'conectado' in session:
        return render_template(f'{PATH_URL}/lista_vehiculos.html', vehiculos=sql_lista_vehiculosBD())
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


@app.route("/detalles-vehiculo/", methods=['GET'])

@app.route("/detalles-vehiculo/<int:idVehiculo>", methods=['GET'])
def detalleVehiculo(idVehiculo=None):
    if 'conectado' in session:
        # Verificamos si el parámetro idEmpleado es None o no está presente en la URL
        if idVehiculo is None:
            return redirect(url_for('inicio'))
        else:
            detalle_vehiculo = sql_detalles_vehiculoBD(idVehiculo) or []
            return render_template(f'{PATH_URL}/detalles_vehiculo.html', detalle_vehiculo=detalle_vehiculo)
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


# Buscadon de empleados
@app.route("/buscando-empleado", methods=['POST'])
def viewBuscarVehiculoBD():
    resultadoBusqueda = buscarVehiculoBD(request.json['busqueda'])
    if resultadoBusqueda:
        return render_template(f'{PATH_URL}/resultado_busqueda_empleado.html', dataBusqueda=resultadoBusqueda)
    else:
        return jsonify({'fin': 0})


@app.route("/editar-empleado/<int:id_vehiculo>", methods=['GET'])
def viewEditarVehiculo(id_vehiculo):
    print(f"ID del vehículo recibido: {id_vehiculo}")  # Imprime para verificar el ID recibido
    if 'conectado' in session:
        respuestaVehiculo = buscarVehiculoUnico(id_vehiculo)
        if respuestaVehiculo:
            return render_template(f'{PATH_URL}/form_empleado_update.html', respuestaVehiculo=respuestaVehiculo)
        else:
            flash('El Vehiculo no existe1.', 'error')
            return redirect(url_for('inicio'))
    else:
        flash('Primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))


#Recibir formulario para actulizar informacion de empleado
# @app.route('/actualizar-empleado', methods=['POST'])
# def actualizarEmpleado():
#     resultData = procesar_actualizacion_form(request)
#     if resultData:
#         return redirect(url_for('lista_vehiculos'))


@app.route('/actualizar-empleado/<int:id_vehiculo>', methods=['POST'])
def actualizarEmpleado(id_vehiculo):
    try:
        #Obtener los datos del formulario enviado
        nombre_duenio = request.form['nombre_duenio']
        sexo_duenio = request.form['sexo_duenio']
        marca_auto = request.form['marca_auto']
        modelo_auto = request.form['modelo_auto']
        factura = request.form['factura']
        tarjeta_circulacion = request.form['tarjeta_circulacion']
        email_duenio = request.form['email_duenio']
        foto_duenio = request.form['foto_duenio']

        #Realizar la actualización en la base de datos utilizando los datos obtenidos del formulario
        with connectionBD() as conexion_MySQLdb:
            with conexion_MySQLdb.cursor(dictionary=True) as cursor:
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
                values = (
                    nombre_duenio, sexo_duenio, marca_auto, modelo_auto,
                    factura, tarjeta_circulacion, email_duenio, foto_duenio, id_vehiculo
                )

                cursor.execute(querySQL, values)
                conexion_MySQLdb.commit()

        #Redirigir a la página de lista de vehículos después de actualizar exitosamente
        return redirect(url_for('lista_vehiculos'))
    except KeyError:
        flash('Se enviaron datos incorrectos', 'error')
        #Manejar el error, redirigir a la página o realizar otras acciones necesarias
        return redirect(url_for('error_page'))
    except Exception as e:
        flash(f'Ocurrió un error al actualizar: {str(e)}', 'error')
        #Manejar el error, redirigir a la página o realizar otras acciones necesarias
        return redirect(url_for('error_page'))


@app.route("/lista-de-usuarios", methods=['GET'])
def usuarios():
    if 'conectado' in session:
        resp_usuariosBD = lista_usuariosBD()
        return render_template('public/usuarios/lista_usuarios.html', resp_usuariosBD=resp_usuariosBD)
    else:
        return redirect(url_for('inicioCpanel'))


@app.route('/borrar-usuario/<string:id>', methods=['GET'])
def borrarUsuario(id):
    resp = eliminarUsuario(id)
    if resp:
        flash('El Usuario fue eliminado correctamente', 'success')
        return redirect(url_for('usuarios'))


# @app.route('/borrar-vehiculo/<string:id_vehiculo>/<string:foto_duenio>', methods=['GET'])
# def borrarVehiculo(id_vehiculo, foto_duenio):
#     resp = eliminarVehiculo(id_vehiculo, foto_duenio)
#     if resp > 0:
#         flash('El vehículo fue eliminado correctamente', 'success')
        
#     elif resp == 0:
#         flash('El vehículo no se pudo eliminar', 'error')
#     else:
#         flash('Ocurrió un error al intentar eliminar el vehículo', 'error')
    
#     return redirect(url_for('lista_vehiculos'))


@app.route('/borrar-vehiculo/<string:id_vehiculo>', methods=['GET'])
def borrarVehiculo(id_vehiculo):
    resp = eliminarVehiculo(id_vehiculo)
    if resp:
        flash('El Vehiculo fue eliminado correctamente', 'success')
        return redirect(url_for('lista_vehiculos'))

    

@app.route("/descargar-informe-empleados/", methods=['GET'])
def reporteBD():
    if 'conectado' in session:
        return generarReportePDF()
    else:
        flash('primero debes iniciar sesión.', 'error')
        return redirect(url_for('inicio'))
