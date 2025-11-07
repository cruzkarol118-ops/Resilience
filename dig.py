from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from data.recomendaciones import RECOMENDACIONES
import json
import os
# ---- Base de datos: Importación ----
import mysql.connector
# ---- Base de datos Local: Configuración ----
'''DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bienestar_universitario'
}'''
# ---- Base de datos: Configuración ----
DB_CONFIG = {
    'host': 'sql5.freesqldatabase.com',
    'user': 'sql5806480',
    'password': 'N69s1CIP3B',
    'database': 'sql5806480'
}
# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Error al conectar a MySQL: {err}")
        return None

app = Flask(__name__)
app.secret_key = '3c9e1f76a4b3b4f28a1b6456c9d7a49c'


JSON_PATH = os.path.join(os.path.dirname(__file__), 'data', 'usuarios.json')

JSON_DIR = os.path.join(os.path.dirname(__file__), 'data')
FORMULARIOS_JSON = os.path.join(JSON_DIR, 'formularios.json')
RESPUESTAS_JSON = os.path.join(JSON_DIR, 'respuestas.json')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/index1')
def index1():
    return render_template("index1.html")

@app.route('/index2')
def index2():
    return render_template("index2.html")

@app.route('/Masculino')
def Masculino():
    return render_template("Masculino.html", recomendaciones=RECOMENDACIONES)

@app.route('/recomendacion/<categoria>')
def mostrar_recomendacion(categoria):
    if categoria in RECOMENDACIONES:
        return render_template(
            RECOMENDACIONES[categoria]['template'],
            detalle=RECOMENDACIONES[categoria]  # Pasamos los datos completos
        )
    return redirect(url_for('Masculino'))

@app.route('/Indexxx')
def Indexxx():
    return render_template("Indexxx.html")

@app.route('/bipolaridad')
def bipolaridad():
    return render_template("bipolaridad.html")

@app.route('/depresion')
def depresion():
    return render_template("depresion.html")

@app.route('/hiperactividad')
def hiperactividad():
    return render_template("hiperactividad.html")

@app.route('/adiccion')
def adiccion():
    return render_template("adiccion.html")

@app.route('/insomnio')
def insomnio():
    return render_template("insomnio.html")

@app.route('/Sicologa')
def Sicologa():
    return render_template("Sicologa.html")

'''**************POST METHODS**********************'''
@app.route('/validar_login', methods=['POST'])
def validar_login():
    username = request.form.get('username').strip()
    password = request.form.get('password')
    conn = get_db_connection()
    
    # ------------------- Lógica de Base de Datos -------------------
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            
            # (MODIFICADO) Añadimos "Cedula" al SELECT
            sql = "SELECT ID_Usuario, Username, Nombres, Apellidos, Email, Cedula, Rol FROM Usuarios WHERE Username = %s AND Password = %s"
            cursor.execute(sql, (username, password))
            usuario_db = cursor.fetchone()
            cursor.close()

            if usuario_db:
                # Login exitoso en DB. Guardar datos completos en la sesión.
                session['usuario'] = {
                    'id_usuario': usuario_db['ID_Usuario'], # ID único para el sistema
                    'username': usuario_db['Username'],
                    'email': usuario_db['Email'],
                    'nombres': usuario_db['Nombres'],
                    'apellidos': usuario_db['Apellidos'],
                    'cedula': usuario_db['Cedula'], # <-- AÑADIDO
                    'rol': usuario_db['Rol']
                }
                return redirect(url_for('Masculino'))
            
        except Exception as e:
            # Si hay un error con la DB (ej. conexión o SQL), imprimimos y continuamos a la lógica JSON
            print(f"Advertencia: Fallo en Login con DB. Cayendo a JSON. Error: {str(e)}")
        finally:
            if conn and conn.is_connected():
                conn.close()
    #--------------Base de datos (Fin)

    # (Lógica de JSON... se mantiene igual)
    try:
        username = request.form.get('username').strip().lower()
        password = request.form.get('password')
        
        with open('data/usuarios.json', 'r') as f:
            usuarios = json.load(f)['usuarios']
            usuario = next((u for u in usuarios if u['username'].lower() == username), None)
            
            if usuario and usuario['password'] == password:
                # Guarda los datos importantes en la sesión, incluyendo el rol (si existe en JSON)
                session['usuario'] = {
                    'username': usuario['username'],
                    'email': usuario['email'],
                    'nombres': usuario['nombres'],
                    'apellidos': usuario.get('apellidos', ''),
                    'cedula': usuario.get('cedula', ''), # <-- AÑADIDO (para consistencia con JSON)
                    'rol': usuario.get('rol')
                }
                return redirect(url_for('Masculino'))
                
        return render_template('index1.html', error="Usuario o contraseña incorrectos")
        
    except Exception as e:
        print(f"Error en login: {str(e)}")
        return render_template('index1.html', error="Error al iniciar sesión")

@app.route('/logout')
def logout():
    session.pop('usuario', None)  # Eliminar los datos de sesión
    return redirect(url_for('index1'))

# Registrar
@app.route('/registrar', methods=['POST'])
def registrar():
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return render_template('index2.html')

    try:
        nuevo_usuario = {
            "username": request.form.get('username').strip(),
            "password": request.form.get('password'),
            "email": request.form.get('email').lower().strip(),
            "nombres": request.form.get('nombres').strip(),
            "apellidos": request.form.get('apellidos', '').strip(),
            "cedula": request.form.get('cedula').strip(),  # <-- AÑADIDO
            "rol": 'Estudiante'
        }
        
        # Validaciones básicas de campos requeridos
        if not all([nuevo_usuario['username'], nuevo_usuario['password'], nuevo_usuario['email'], nuevo_usuario['nombres'], nuevo_usuario['cedula']]): # <-- AÑADIDO CEDULA
            flash("Complete todos los campos obligatorios.", 'danger')
            return render_template('index2.html')

        # Validación extra para cédula (asegurar que sean solo números)
        if not nuevo_usuario['cedula'].isdigit():
            flash("La cédula debe contener solo números.", 'danger')
            return render_template('index2.html')

        cursor = conn.cursor()
        
        # --- 1. REGISTRO EN BASE DE DATOS ---
        
        # 1.1 Verificar unicidad en la DB (AÑADIDO CEDULA)
        cursor.execute("SELECT ID_Usuario FROM Usuarios WHERE Username = %s OR Email = %s OR Cedula = %s", 
                       (nuevo_usuario['username'], nuevo_usuario['email'], nuevo_usuario['cedula']))
        if cursor.fetchone():
            flash("El usuario, el email o la cédula ya están registrados.", 'danger')
            return render_template('index2.html')

        # 1.2 Insertar el nuevo usuario en la tabla Usuarios (AÑADIDO CEDULA)
        sql_user = "INSERT INTO Usuarios (Username, Password, Email, Cedula, Nombres, Apellidos, Rol) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        data_db = (
            nuevo_usuario['username'], 
            nuevo_usuario['password'], 
            nuevo_usuario['email'], 
            nuevo_usuario['cedula'],  # <-- AÑADIDO
            nuevo_usuario['nombres'], 
            nuevo_usuario['apellidos'],
            nuevo_usuario['rol']
        )
        cursor.execute(sql_user, data_db)
        id_usuario_generado = cursor.lastrowid
        
        # 1.3 Crear Perfil Estudiante Inicial (MODIFICADO)
        # Se elimina Documento_Codigo de la inserción.
        sql_estudiante = "INSERT INTO Estudiantes (ID_Usuario, Programa_Academico, Semestre, Telefono_Contacto) VALUES (%s, '', 0, '')"
        cursor.execute(sql_estudiante, (id_usuario_generado,))

        conn.commit()
        # --- FIN REGISTRO EN BASE DE DATOS ---

        # --- 2. REGISTRO EN ARCHIVO JSON (MANTENIENDO LA FUNCIONALIDAD ORIGINAL) ---
        # (El JSON se mantiene, pero si quieres puedes añadir la cédula aquí también)
        try:
            with open('data/usuarios.json', 'r+') as f:
                data = json.load(f)
                
                if any(u['username'] == nuevo_usuario['username'] for u in data['usuarios']):
                    flash("El usuario ya existe en el sistema.", 'warning')
                elif any(u['email'] == nuevo_usuario['email'] for u in data['usuarios']):
                    flash("El email ya está registrado en el sistema.", 'warning')
                else:
                    data['usuarios'].append(nuevo_usuario) # <-- El dict ya tiene la cédula
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
        except Exception as json_error:
            print(f"Error al guardar en JSON: {str(json_error)}")
        # --- FIN REGISTRO EN JSON ---

        flash('Registro exitoso. ¡Inicie sesión!', 'success')
        return redirect(url_for('index1'))
        
    except Exception as e:
        conn.rollback()
        print(f"Error en registro: {str(e)}")
        flash('Ocurrió un error. Intente nuevamente', 'danger')
        return render_template('index2.html')
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Admin Roles
@app.route('/admin/roles')
def admin_roles():
    if 'usuario' not in session or session['usuario'].get('rol') != 'Admin':
        flash('Acceso no autorizado (Solo para Administradores).', 'danger')
        return redirect(url_for('agenda'))
    
    # 1. Obtener el término de búsqueda y el rol objetivo (default 'Estudiante')
    search_query = request.args.get('search_query', '').strip()
    target_rol = request.args.get('rol', 'Estudiante') 
    
    # Validación del rol objetivo
    if target_rol not in ['Estudiante', 'Psicologo']:
        target_rol = 'Estudiante'

    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    usuarios = []
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 2. Query base (Filtra por el rol objetivo: 'Estudiante' o 'Psicologo')
        # (MODIFICADO) Añadimos "Cedula" al SELECT
        sql = """
            SELECT ID_Usuario, Username, Nombres, Apellidos, Email, Cedula, Rol 
            FROM Usuarios 
            WHERE Rol = %s 
        """
        params = [target_rol] 
        
        # 3. Si hay término de búsqueda, añadir filtro (AÑADIDO Cedula)
        if search_query:
            sql += """
                AND (
                    Username LIKE %s 
                    OR Nombres LIKE %s 
                    OR Apellidos LIKE %s
                    OR Cedula LIKE %s
                )
            """
            like_query = f"%{search_query}%"
            params.extend([like_query, like_query, like_query, like_query])
        
        # 4. Añadir ordenamiento A-Z
        sql += " ORDER BY Nombres ASC, Apellidos ASC"
        
        cursor.execute(sql, tuple(params))
        usuarios = cursor.fetchall()
        cursor.close()
        
    except Exception as e:
        print(f"Error al cargar usuarios: {str(e)}")
        flash(f'Error al cargar usuarios: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    # 5. Pasamos el target_rol a la plantilla para la lógica de botones y títulos
    return render_template('admin_roles.html', 
                           usuarios=usuarios, 
                           current_search=search_query,
                           target_rol=target_rol)

    # 5. Pasamos el target_rol a la plantilla para la lógica de botones y títulos
    return render_template('admin_roles.html', 
                           usuarios=usuarios, 
                           current_search=search_query,
                           target_rol=target_rol)


@app.route('/admin/promote/<int:id_usuario>', methods=['POST'])
def admin_promote_psicologo(id_usuario):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Admin':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('agenda'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('admin_roles'))

    try:
        cursor = conn.cursor()
        
        # 1. Obtener datos del usuario (Necesitamos Nombre/Apellido para el display del Psicólogo)
        cursor.execute("SELECT Nombres, Apellidos FROM Usuarios WHERE ID_Usuario = %s AND Rol = 'Estudiante'", (id_usuario,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('Usuario no encontrado o ya es Psicólogo/Admin.', 'warning')
            return redirect(url_for('admin_roles'))
            
        nombres, apellidos = user_data
        
        # 2. Promover a Psicólogo
        sql_update_rol = "UPDATE Usuarios SET Rol = 'Psicologo' WHERE ID_Usuario = %s"
        cursor.execute(sql_update_rol, (id_usuario,))
        
        # 3. Crear Perfil de Psicólogo
        nombre_display = f"{nombres} {apellidos}".strip()
        sql_insert_psicologo = """
            INSERT INTO Psicologos (ID_Usuario, Nombre_Completo_Display, Correo_Institucional) 
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE Nombre_Completo_Display = VALUES(Nombre_Completo_Display);
        """
        # (Añadí ON DUPLICATE KEY por si el perfil ya existía por alguna razón)
        cursor.execute(sql_insert_psicologo, (id_usuario, nombre_display, f'psicologo-{id_usuario}@uni.edu'))

        # 4. ELIMINAMOS LA LÍNEA QUE BORRABA AL ESTUDIANTE
        # Ya no intentamos: DELETE FROM Estudiantes...
        
        conn.commit()
        
        flash(f'Usuario {nombre_display} promovido a Psicólogo exitosamente. Su historial de estudiante ha sido conservado.', 'success')
        return redirect(url_for('admin_roles'))

    except Exception as e:
        conn.rollback()
        print(f"Error al promover rol: {str(e)}")
        flash(f'Ocurrió un error al asignar el rol: {str(e)}', 'danger')
        return redirect(url_for('admin_roles'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

@app.route('/admin/degrade/<int:id_usuario>', methods=['POST'])
def admin_degrade_estudiante(id_usuario):
    """
    Degrada un usuario de 'Psicologo' a 'Estudiante'.
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Admin':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('agenda'))
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('admin_roles', rol='Psicologo'))

    try:
        cursor = conn.cursor()

        # 1. Obtener datos del usuario y verificar que sea Psicólogo
        cursor.execute("SELECT Nombres, Apellidos FROM Usuarios WHERE ID_Usuario = %s AND Rol = 'Psicologo'", (id_usuario,))
        user_data = cursor.fetchone()
        
        if not user_data:
            flash('Usuario no encontrado o no tiene el rol de Psicólogo.', 'warning')
            return redirect(url_for('admin_roles', rol='Psicologo'))
            
        nombres, apellidos = user_data
        
        # 2. Cambiar Rol a Estudiante
        sql_update_rol = "UPDATE Usuarios SET Rol = 'Estudiante' WHERE ID_Usuario = %s"
        cursor.execute(sql_update_rol, (id_usuario,))
        
        # 3. ELIMINAMOS LA LÍNEA QUE BORRABA AL PSICÓLOGO
        # Ya no intentamos: DELETE FROM Psicologos...
        
        # 4. Crear Perfil de Estudiante Inicial (o asegurarse de que exista)
        sql_insert_estudiante = """
            INSERT INTO Estudiantes (ID_Usuario, Documento_Codigo, Programa_Academico, Semestre, Telefono_Contacto) 
            VALUES (%s, '', '', 0, '')
            ON DUPLICATE KEY UPDATE ID_Usuario = VALUES(ID_Usuario);
        """
        # (Añadí ON DUPLICATE KEY por si ya tenía un perfil de estudiante 'congelado' de antes)
        cursor.execute(sql_insert_estudiante, (id_usuario,))
        
        conn.commit()
        
        flash(f'Usuario {nombres} {apellidos} degradado a Estudiante exitosamente. Su historial de psicólogo ha sido conservado.', 'success')
        return redirect(url_for('admin_roles', rol='Psicologo')) 

    except Exception as e:
        conn.rollback()
        print(f"Error al degradar rol: {str(e)}")
        flash(f'Ocurrió un error al degradar el rol: {str(e)}', 'danger')
        return redirect(url_for('admin_roles', rol='Psicologo'))
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

#Admin Historial de Usuarios
@app.route('/admin/historial_estudiantes')
def admin_historial_estudiantes():
    """
    Muestra la lista de estudiantes con citas REALIZADAS,
    agrupados por período académico (deducido por fecha).
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Admin':
        flash('Acceso no autorizado (Solo para Administradores).', 'danger')
        return redirect(url_for('agenda'))
    
    search_query = request.args.get('search_query', '').strip()

    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    usuarios_agrupados = {}
    try:
        cursor = conn.cursor(dictionary=True)
        
        # SQL para derivar periodo: CONCAT(YEAR(C.Fecha_Cita), '-', IF(MONTH(C.Fecha_Cita) <= 6, 1, 2))
        # Seleccionamos usuarios distintos que tengan al menos una cita realizada
        sql = """
            SELECT 
                U.ID_Usuario, U.Username, U.Nombres, U.Apellidos,
                CONCAT(YEAR(C.Fecha_Cita), '-', IF(MONTH(C.Fecha_Cita) <= 6, 1, 2)) AS Periodo_Academico,
                COUNT(C.ID_Cita) as Total_Citas_Realizadas
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Usuarios U ON E.ID_Usuario = U.ID_Usuario
            WHERE C.Estado_Cita = 'REALIZADA'
        """
        params = []
        
        if search_query:
            sql += """
                AND (
                    U.Username LIKE %s 
                    OR U.Nombres LIKE %s 
                    OR U.Apellidos LIKE %s
                    OR U.ID_Usuario = %s
                )
            """
            like_query = f"%{search_query}%"
            # Manejar si la búsqueda es un ID numérico
            id_query = search_query if search_query.isdigit() else "0"
            params.extend([like_query, like_query, like_query, id_query])

        sql += """
            GROUP BY U.ID_Usuario, U.Username, U.Nombres, U.Apellidos, Periodo_Academico
            ORDER BY Periodo_Academico DESC, U.Nombres ASC
        """
        
        cursor.execute(sql, tuple(params))
        usuarios_raw = cursor.fetchall()
        cursor.close()
        
        # Agrupar resultados en Python para la plantilla
        for usuario in usuarios_raw:
            periodo = usuario['Periodo_Academico']
            if periodo not in usuarios_agrupados:
                usuarios_agrupados[periodo] = []
            usuarios_agrupados[periodo].append(usuario)
            
    except Exception as e:
        print(f"Error al cargar historial de estudiantes: {str(e)}")
        flash(f'Error al cargar historial: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('admin_historial_estudiantes.html', 
                           usuarios_agrupados=usuarios_agrupados, 
                           current_search=search_query)


@app.route('/admin/historial_detalle/<int:id_usuario>')
def admin_ver_historial_detalle(id_usuario):
    """
    Muestra el historial completo de un estudiante específico,
    incluyendo calificaciones y comentarios.
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Admin':
        flash('Acceso no autorizado (Solo para Administradores).', 'danger')
        return redirect(url_for('agenda'))
        
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('admin_historial_estudiantes'))

    citas = []
    estudiante_info = None
    
    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Obtener información del estudiante
        cursor.execute("SELECT Nombres, Apellidos FROM Usuarios WHERE ID_Usuario = %s", (id_usuario,))
        estudiante_info = cursor.fetchone()
        
        if not estudiante_info:
            flash('Estudiante no encontrado.', 'danger')
            return redirect(url_for('admin_historial_estudiantes'))

        # 2. Obtener historial de citas (TODOS los estados) con la encuesta
        sql_citas = """
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, 
                C.Nota_Ubicacion,
                P.Nombre_Completo_Display AS Nombre_Psicologo,
                EC.Calificacion, EC.Comentario
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Usuarios U ON E.ID_Usuario = U.ID_Usuario
            JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
            LEFT JOIN Encuestas EC ON C.ID_Cita = EC.ID_Cita
            WHERE 
                U.ID_Usuario = %s 
            ORDER BY 
                C.Fecha_Cita DESC, C.Hora_Cita DESC
        """
        cursor.execute(sql_citas, (id_usuario,))
        citas = cursor.fetchall()
        cursor.close()

        # 3. Formatear fechas y horas
        for c in citas:
            try:
                t_obj = datetime.strptime(c['Hora_Cita'], '%H:%M').time()
                c['Hora_Formateada'] = t_obj.strftime('%I:%M %p')
                c['Fecha_Formateada'] = c['Fecha_Cita'].strftime('%d / %m / %Y')
            except (ValueError, TypeError):
                c['Hora_Formateada'] = c['Hora_Cita']
                c['Fecha_Formateada'] = str(c['Fecha_Cita'])
        
    except Exception as e:
        print(f"Error al cargar detalle de historial: {str(e)}")
        flash(f'Ocurrió un error al cargar el historial: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('admin_historial_detalle.html', 
                           citas=citas, 
                           estudiante=estudiante_info)


'''********************** Formularios ***********************'''
# Cargar formularios
def cargar_formularios():
    with open(FORMULARIOS_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return {form['id']: form for form in data['formularios']}

# Guardar respuestas
def guardar_respuesta(respuesta):
    os.makedirs(os.path.dirname(RESPUESTAS_JSON), exist_ok=True)
    
    respuestas = []
    if os.path.exists(RESPUESTAS_JSON):
        try:
            with open(RESPUESTAS_JSON, 'r', encoding='utf-8') as f:
                respuestas = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            respuestas = []

    # Buscar si ya hay respuesta para ese usuario y tema
    index_existente = -1
    for i, r in enumerate(respuestas):
        if r.get('usuario', {}).get('username') == respuesta['usuario']['username'] and r.get('tema') == respuesta['tema']:
            index_existente = i
            break
    
    if index_existente >= 0:
        respuestas[index_existente] = respuesta  # Actualizar la respuesta existente
    else:
        respuestas.append(respuesta)  # Agregar nueva

    with open(RESPUESTAS_JSON, 'w', encoding='utf-8') as f:
        json.dump(respuestas, f, indent=2, ensure_ascii=False)


# Ruta para mostrar formularios
@app.route('/test/<tema>')
def test_diagnostico(tema):
    formularios = cargar_formularios()
    if tema in formularios:
        return render_template('formulario.html', formulario=formularios[tema])
    flash('Formulario no encontrado', 'danger')
    return redirect(url_for('Masculino'))

# Ruta para procesar respuestas
@app.route('/procesar_test/<tema>', methods=['POST'])
def procesar_test(tema):
    formularios = cargar_formularios()
    if tema not in formularios:
        flash('Formulario no válido', 'danger')
        return redirect(url_for('Masculino'))

    if 'usuario' not in session:
        flash('Debes iniciar sesión para completar el test', 'warning')
        return redirect(url_for('login'))

    try:
        # Obtener TODOS los datos del usuario de la sesión
        usuario_data = {
            'username': session['usuario'].get('username', ''),
            'email': session['usuario'].get('email', ''),
            'nombres': session['usuario'].get('nombres', ''),
            'apellidos': session['usuario'].get('apellidos', '')
        }

        # Procesar respuestas
        respuestas = {}
        for key, value in request.form.items():
            if key.startswith('pregunta_'):
                pregunta_id = key.split('_')[1]
                respuestas[pregunta_id] = value

        # Crear registro de respuesta completo
        respuesta = {
            'fecha': datetime.now().isoformat(),
            'tema': tema,
            'usuario': usuario_data,  #Todos los datos del usuario en un objeto
            'respuestas': respuestas
        }

        guardar_respuesta(respuesta)
        flash('Test enviado correctamente', 'success')
        return redirect(url_for('Masculino'))

    except Exception as e:
        flash(f'Error al procesar el test: {str(e)}', 'danger')
        #return redirect(url_for('test_diagnostico', tema=tema))
        return redirect(url_for('Masculino'))
    
@app.route('/mis_resultados')
def mis_resultados():
    formularios = cargar_formularios()
    if 'usuario' not in session:
        flash('Debes iniciar sesión para ver tus resultados', 'warning')
        return redirect(url_for('login'))

    try:
        with open(RESPUESTAS_JSON, 'r', encoding='utf-8') as f:
            todas_respuestas = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        todas_respuestas = []

    usuario_respuestas = {}
    for r in todas_respuestas:
        usuario = r.get('usuario')
        if usuario and usuario.get('username') == session['usuario']['username']:
            usuario_respuestas[r['tema']] = r

    resultados = []
    for tema, respuesta in usuario_respuestas.items():
        formulario = formularios.get(respuesta['tema'])
        analisis = analizar_respuestas(respuesta['tema'], respuesta['respuestas'], formulario)
        resultados.append({
            'tema': tema,
            'fecha': respuesta['fecha'],
            'analisis': analisis
        })

    return render_template('resultados.html', resultados=resultados)

def analizar_respuestas(tema, respuestas_usuario, formulario):
    analisis = {
        'puntaje_total': 0,
        'nivel': '',
        'recomendacion': '',
        'detalles': []
    }

    if not formulario:
        analisis['nivel'] = 'Formulario no encontrado'
        analisis['recomendacion'] = ''
        return analisis

    puntaje = 0

    preguntas = formulario.get('preguntas', [])

    # Se asume que en cada pregunta hay un campo 'peso' que puede ser dict con valores por respuesta
    for pregunta in preguntas:
        pid = str(pregunta['id'])
        if pid in respuestas_usuario:
            respuesta_usuario = respuestas_usuario[pid].strip().lower()

            peso = 0
            if pregunta.get('tipo') == 'texto_libre':
                # Para preguntas de texto libre, asignamos un peso de -1
                peso = -1
            elif 'opciones' in pregunta:
                for opcion in pregunta['opciones']:
                    if opcion['texto'].lower() == respuesta_usuario.lower():
                        peso = opcion.get('peso', 0)
                        break

            # Solo se suma al puntaje si no es una pregunta de texto libre (peso diferente de -1)
            if peso != -1:
                puntaje += peso

            analisis['detalles'].append({
                'pregunta': pregunta.get('pregunta', 'Pregunta sin texto'),
                'respuesta': respuesta_usuario,
                'peso': peso
            })

    analisis['puntaje_total'] = puntaje

    if tema == 'ansiedad_adolescentes':
        if puntaje >= 20:
            analisis['nivel'] = "Ansiedad alta"
            analisis['recomendacion'] = "Recomendamos terapia."
        elif puntaje >= 10:
            analisis['nivel'] = "Ansiedad moderada"
            analisis['recomendacion'] = "Considera técnicas de relajación."
        else:
            analisis['nivel'] = "Ansiedad baja"
            analisis['recomendacion'] = "Mantén buenos hábitos."

    elif tema == 'depresion_adolescentes':
        if puntaje >= 20:
            analisis['nivel'] = "Depresión severa"
            analisis['recomendacion'] = "Busca ayuda profesional."
        elif puntaje >= 10:
            analisis['nivel'] = "Depresión moderada"
            analisis['recomendacion'] = "Considera terapia."
        else:
            analisis['nivel'] = "Depresión leve"
            analisis['recomendacion'] = "Sigue con hábitos saludables."
    
    elif tema == 'bipolaridad':
        if puntaje >= 10:
            analisis['nivel'] = "Bipolaridad Severa"
            analisis['recomendacion'] = "Es fundamental buscar ayuda profesional especializada de inmediato. Un diagnóstico y plan de tratamiento son cruciales."
        elif puntaje >= 5:
            analisis['nivel'] = "Bipolaridad Moderada"
            analisis['recomendacion'] = "Considera hablar con un especialista en salud mental. Un seguimiento temprano puede ser muy beneficioso."
        else:
            analisis['nivel'] = "Bipolaridad Leve"
            analisis['recomendacion'] = "Mantén un registro de tus estados de ánimo y busca información fiable. Consulta a un profesional si los síntomas persisten o empeoran."
    
    elif tema == 'hiperactividad':
        if puntaje >= 10:
            analisis['nivel'] = "Hiperactividad Severa"
            analisis['recomendacion'] = "Una evaluación y manejo profesional son recomendados para desarrollar estrategias de afrontamiento efectivas y considerar opciones de tratamiento."
        elif puntaje >= 5:
            analisis['nivel'] = "Hiperactividad Moderada"
            analisis['recomendacion'] = "Considera técnicas para mejorar la concentración y el control de impulsos. Un especialista puede ofrecerte apoyo y orientación."
        else:
            analisis['nivel'] = "Hiperactividad Leve"
            analisis['recomendacion'] = "Explora estrategias para canalizar la energía. Si los síntomas afectan tu vida diaria, busca asesoramiento."

    elif tema == 'adicciones':
        if puntaje >= 10:
            analisis['nivel'] = "Adicción Severa"
            analisis['recomendacion'] = "Busca ayuda profesional de inmediato. La recuperación es posible con el apoyo adecuado."
        elif puntaje >= 5:
            analisis['nivel'] = "Adicción Moderada"
            analisis['recomendacion'] = "Considera hablar con un terapeuta o un grupo de apoyo. Reconocer el problema es el primer paso."
        else:
            analisis['nivel'] = "Riesgo de Adicción Leve"
            analisis['recomendacion'] = "Evalúa tus hábitos y busca información sobre los riesgos. Mantén un estilo de vida saludable."

    elif tema == 'insomnio':
        if puntaje >= 10:
            analisis['nivel'] = "Insomnio Severo"
            analisis['recomendacion'] = "Consulta a un médico especialista en sueño. Es vital para tu salud general."
        elif puntaje >= 5:
            analisis['nivel'] = "Insomnio Moderado"
            analisis['recomendacion'] = "Practica la higiene del sueño: horarios regulares, ambiente oscuro y tranquilo. Si persiste, busca asesoramiento."
        else:
            analisis['nivel'] = "Insomnio Leve"
            analisis['recomendacion'] = "Mejora tus hábitos de sueño y evita estimulantes antes de acostarte. La relajación puede ayudar."
    
    else:
        analisis['nivel'] = f"Puntaje total: {puntaje}"
        analisis['recomendacion'] = "No hay una recomendación específica definida para este tema."

    return analisis

#----Base de datos----
# Endpoint para la nueva vista de Agenda
@app.route('/agenda')
def agenda():
    if 'usuario' not in session:
        # Si no hay sesión, redirige al login
        flash('Debes iniciar sesión para acceder a la agenda.', 'warning')
        return redirect(url_for('index1')) 

    # Obtenemos el rol del usuario logueado
    rol = session['usuario'].get('rol')
    
    # Renderizamos la plantilla pasando el rol
    return render_template('agenda.html', rol_usuario=rol)

#----Agenda Endpoints ----
@app.route('/est_agendar', methods=['GET', 'POST'])
def est_agendar():
    """
    Maneja la vista de Agendamiento.
    Si hay cita activa, muestra los detalles de la cita (no editables).
    Si no hay cita, muestra el formulario de solicitud.
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    id_usuario_actual = session['usuario']['id_usuario']
    
    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Buscar Cita Activa para determinar la vista a mostrar
        
        # **** LÍNEA CRÍTICA AÑADIDA/VERIFICADA ****
        active_cita = None 
        # **** (Asegúrate de que esta línea exista) ****
        
        cursor.execute("""
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, C.Nota_Ubicacion,
                P.Nombre_Completo_Display AS Nombre_Psicologo
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
            WHERE 
                E.ID_Usuario = %s 
                AND (C.Estado_Cita = 'SOLICITADA' OR C.Estado_Cita = 'CONFIRMADA')
        """, (id_usuario_actual,))
        cita_activa_data = cursor.fetchone()
        
        # 2. Lógica POST (Solo ocurre si no hay cita activa)
        if request.method == 'POST':
            if cita_activa_data:
                flash('Ya tienes una cita activa. No puedes agendar otra.', 'warning')
                return redirect(url_for('agenda'))
            
            # --- Lógica de Inserción de Nueva Cita ---
            id_psicologo_sel = request.form.get('psicologo')
            fecha_cita = request.form.get('fecha_cita')
            id_horario_sel = request.form.get('id_horario_seleccionado')
            if not id_horario_sel:
                flash('Error: No seleccionaste un bloque de horario válido.', 'danger')
                raise Exception("No se seleccionó ID de horario.") 
            # documento = request.form.get('documento') # <-- ELIMINADO
            programa = request.form.get('programa')
            semestre = request.form.get('semestre')
            telefono = request.form.get('telefono')
            
            cursor.execute("SELECT ID_Estudiante FROM Estudiantes WHERE ID_Usuario = %s", (id_usuario_actual,))
            perfil_estudiante = cursor.fetchone()
            id_estudiante_db = None
            
            if perfil_estudiante:
                id_estudiante_db = perfil_estudiante['ID_Estudiante']
                # Query MODIFICADO: se quita Documento_Codigo
                sql_update_est = "UPDATE Estudiantes SET Programa_Academico = %s, Semestre = %s, Telefono_Contacto = %s WHERE ID_Estudiante = %s"
                cursor.execute(sql_update_est, (programa, semestre, telefono, id_estudiante_db))
            else:
                # Query MODIFICADO: se quita Documento_Codigo
                sql_insert_est = "INSERT INTO Estudiantes (ID_Usuario, Programa_Academico, Semestre, Telefono_Contacto) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql_insert_est, (id_usuario_actual, programa, semestre, telefono))
                id_estudiante_db = cursor.lastrowid
                
            cursor.execute("SELECT Hora_Inicio FROM Horarios_Disponibles WHERE ID_Horario = %s", (id_horario_sel,))
            bloque_seleccionado = cursor.fetchone()
            if not bloque_seleccionado:
                 raise Exception("El bloque de horario seleccionado no es válido.")
            hora_cita_db = bloque_seleccionado['Hora_Inicio']
            
            sql_insert_cita = "INSERT INTO Citas (ID_Estudiante, ID_Psicologo, Fecha_Cita, Hora_Cita, Estado_Cita) VALUES (%s, %s, %s, %s, 'SOLICITADA')"
            cursor.execute(sql_insert_cita, (id_estudiante_db, id_psicologo_sel, fecha_cita, hora_cita_db))
            
            conn.commit()
            
            flash('Cita solicitada correctamente. Espere confirmación.', 'success')
            return redirect(url_for('agenda'))

        # 3. LÓGICA GET (Renderización de la vista)
        estudiante_data = None
        lista_psicologos = []

        if cita_activa_data:
            try:
                # Formateo de hora para la vista no editable
                hora_obj = datetime.strptime(cita_activa_data['Hora_Cita'], '%H:%M').time()
                cita_activa_data['Hora_Cita_Formateada'] = hora_obj.strftime('%I:%M %p')
            except (ValueError, TypeError):
                cita_activa_data['Hora_Cita_Formateada'] = cita_activa_data['Hora_Cita'] 
            active_cita = cita_activa_data
        else:
            # Si NO hay cita activa, cargamos los datos para el formulario de solicitud
            cursor.execute("SELECT * FROM Estudiantes WHERE ID_Usuario = %s", (id_usuario_actual,))
            estudiante_data = cursor.fetchone()
            cursor.execute("SELECT p.ID_Psicologo, p.Nombre_Completo_Display FROM Psicologos p")
            lista_psicologos = cursor.fetchall()

        cursor.close()
        
        return render_template('est_agendar.html', 
                               active_cita=active_cita,
                               psicologos=lista_psicologos, 
                               estudiante=estudiante_data)

    except Exception as e:
        conn.rollback() 
        print(f"Error en est_agendar: {str(e)}")
        flash(f'Ocurrió un error al procesar la solicitud: {str(e)}', 'danger')
        return redirect(url_for('agenda'))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/est_ver_o_editar')
def est_ver_o_editar():
    """Maneja la lógica del botón 'Ver Cita Activa': Redirige a edición o muestra alerta."""
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))
        
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    id_usuario_actual = session['usuario']['id_usuario']
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT C.ID_Cita
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            WHERE 
                E.ID_Usuario = %s 
                AND (C.Estado_Cita = 'SOLICITADA' OR C.Estado_Cita = 'CONFIRMADA')
        """, (id_usuario_actual,))
        cita_activa = cursor.fetchone()
        cursor.close()

        if cita_activa:
            return redirect(url_for('est_editar_cita', id_cita=cita_activa['ID_Cita']))
        else:
            flash('Actualmente no tienes ninguna cita activa para ver o editar.', 'warning')
            return redirect(url_for('agenda'))

    except Exception as e:
        print(f"Error en est_ver_o_editar: {str(e)}")
        flash(f'Ocurrió un error al buscar la cita activa: {str(e)}', 'danger')
        return redirect(url_for('agenda'))
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/est_editar_cita/<int:id_cita>', methods=['GET', 'POST'])
def est_editar_cita(id_cita):
    """Maneja la vista y la lógica POST para EDITAR una cita activa."""
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))
        
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))
        
    id_usuario_actual = session['usuario']['id_usuario']

    try:
        cursor = conn.cursor(dictionary=True)

        # 1. Obtener la cita y verificar propiedad/estado
        cursor.execute("""
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, C.Nota_Ubicacion, C.ID_Psicologo,
                P.Nombre_Completo_Display AS Nombre_Psicologo,
                E.Programa_Academico, E.Semestre, E.Telefono_Contacto, E.ID_Estudiante 
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
            WHERE 
                C.ID_Cita = %s
                AND E.ID_Usuario = %s 
                AND (C.Estado_Cita = 'SOLICITADA' OR C.Estado_Cita = 'CONFIRMADA')
        """, (id_cita, id_usuario_actual))
        # Se quitó E.Documento_Codigo del SELECT
        cita_activa = cursor.fetchone()

        if not cita_activa:
            flash('La cita que intentas editar no existe, no te pertenece o ya fue cancelada/finalizada.', 'danger')
            return redirect(url_for('est_agendar'))

        # 2. Lógica POST (Guardar Cambios)
        if request.method == 'POST':
            # documento = request.form.get('documento') # <-- ELIMINADO
            programa = request.form.get('programa')
            semestre = request.form.get('semestre')
            telefono = request.form.get('telefono')
            id_psicologo_sel = request.form.get('psicologo')
            fecha_cita = request.form.get('fecha_cita')
            id_horario_sel = request.form.get('id_horario_seleccionado')

            # a) Actualizar datos del Estudiante (MODIFICADO)
            sql_update_est = "UPDATE Estudiantes SET Programa_Academico = %s, Semestre = %s, Telefono_Contacto = %s WHERE ID_Estudiante = %s"
            cursor.execute(sql_update_est, (programa, semestre, telefono, cita_activa['ID_Estudiante']))

            # b) Actualizar datos de la Cita (...)
            hora_cita_db = cita_activa['Hora_Cita'] 
            cita_modificada = False

            if id_horario_sel:
                cursor.execute("SELECT Hora_Inicio FROM Horarios_Disponibles WHERE ID_Horario = %s", (id_horario_sel,))
                bloque_seleccionado = cursor.fetchone()
                if not bloque_seleccionado:
                    raise Exception("El nuevo bloque de horario seleccionado no es válido.")
                hora_cita_db = bloque_seleccionado['Hora_Inicio']
                cita_modificada = True
            
            if str(cita_activa['ID_Psicologo']) != id_psicologo_sel or str(cita_activa['Fecha_Cita'].strftime('%Y-%m-%d')) != fecha_cita or cita_modificada:
                sql_update_cita = "UPDATE Citas SET ID_Psicologo = %s, Fecha_Cita = %s, Hora_Cita = %s WHERE ID_Cita = %s"
                cursor.execute(sql_update_cita, (id_psicologo_sel, fecha_cita, hora_cita_db, id_cita))
                
            conn.commit()
            
            flash('Cita actualizada correctamente.', 'success')
            return redirect(url_for('agenda'))

        # 3. Lógica GET (...)
        try:
            hora_obj = datetime.strptime(cita_activa['Hora_Cita'], '%H:%M').time()
            cita_activa['Hora_Cita_Formateada'] = hora_obj.strftime('%I:%M %p')
        except (ValueError, TypeError):
            cita_activa['Hora_Cita_Formateada'] = cita_activa['Hora_Cita'] 
            
        cursor.execute("SELECT p.ID_Psicologo, p.Nombre_Completo_Display FROM Psicologos p")
        lista_psicologos = cursor.fetchall()

        cursor.close()

        return render_template('est_editar_cita.html', 
                               cita_activa=cita_activa,
                               psicologos=lista_psicologos)

    except Exception as e:
        conn.rollback() 
        print(f"Error en est_editar_cita: {str(e)}")
        flash(f'Ocurrió un error al editar la cita: {str(e)}', 'danger')
        return redirect(url_for('agenda'))
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/cancelar_cita/<int:id_cita>', methods=['POST'])
def cancelar_cita(id_cita):
    """Cancela una cita activa y redirige a la agenda (funcionalidad del botón en edición)."""
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))
        
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))
        
    id_usuario_actual = session['usuario']['id_usuario']

    try:
        cursor = conn.cursor(dictionary=True)
        
        sql_check = """
            SELECT C.ID_Cita
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            WHERE C.ID_Cita = %s AND E.ID_Usuario = %s 
            AND (C.Estado_Cita = 'SOLICITADA' OR C.Estado_Cita = 'CONFIRMADA')
        """
        cursor.execute(sql_check, (id_cita, id_usuario_actual))
        if not cursor.fetchone():
            flash('Error: La cita no se pudo cancelar (no existe, no te pertenece o ya fue cancelada).', 'danger')
            return redirect(url_for('agenda'))

        sql_cancel = "UPDATE Citas SET Estado_Cita = 'CANCELADA' WHERE ID_Cita = %s"
        cursor.execute(sql_cancel, (id_cita,))
        conn.commit()
        
        flash('La cita ha sido cancelada correctamente.', 'success')
        
        # --- LÍNEA AÑADIDA ---
        # Establecemos una bandera en la sesión para indicar
        # que el formulario de agendar debe resetearse.
        session['_form_reset'] = True
        # --- FIN LÍNEA AÑADIDA ---
        
        return redirect(url_for('agenda'))

    except Exception as e:
        conn.rollback() 
        print(f"Error en cancelar_cita: {str(e)}")
        flash(f'Ocurrió un error al intentar cancelar la cita: {str(e)}', 'danger')
        return redirect(url_for('agenda'))
    finally:
        if conn and conn.is_connected():
            conn.close()

# API ENDPOINT PARA OBTENER HORARIOS (LLAMADO POR JAVASCRIPT)
@app.route('/api/horarios/<int:id_psicologo>/<string:fecha>')
def api_get_horarios(id_psicologo, fecha):
    if 'usuario' not in session:
        return jsonify({"error": "No autorizado"}), 401

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Error de conexión"}), 500
    
    try:
        # 1. Calcular Día de la Semana (Esto sigue igual)
        dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d')
            dia_semana_str = dias_semana[fecha_obj.weekday()]
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido"}), 400

        cursor = conn.cursor(dictionary=True)

        # 2. Obtener Plantilla (Ahora lee VARCHAR '15:00')
        sql_horarios = """
            SELECT ID_Horario, Hora_Inicio, Hora_Fin 
            FROM Horarios_Disponibles 
            WHERE ID_Psicologo = %s AND Dia_Semana = %s
        """
        cursor.execute(sql_horarios, (id_psicologo, dia_semana_str))
        bloques_disponibles = cursor.fetchall()

        # 3. Obtener Citas Ocupadas (Ahora lee VARCHAR '15:00' de la tabla Citas)
        sql_citas = """
            SELECT Hora_Cita 
            FROM Citas 
            WHERE ID_Psicologo = %s AND Fecha_Cita = %s AND (Estado_Cita = 'CONFIRMADA' OR Estado_Cita = 'SOLICITADA')
        """
        cursor.execute(sql_citas, (id_psicologo, fecha))
        citas_ocupadas = cursor.fetchall()
        
        # 'horas_ocupadas' es un set de strings: {'15:00'}
        horas_ocupadas = {c['Hora_Cita'] for c in citas_ocupadas}

        # 4. Filtrar (Comparamos texto con texto, sin errores de 'TIME')
        bloques_libres = []
        for bloque in bloques_disponibles:
            # bloque['Hora_Inicio'] es el string '15:00'
            if bloque['Hora_Inicio'] not in horas_ocupadas:
                
                # Formatear '15:00' a '03:00 PM' para el usuario
                t_inicio_obj = datetime.strptime(bloque['Hora_Inicio'], '%H:%M').time()
                t_fin_obj = datetime.strptime(bloque['Hora_Fin'], '%H:%M').time()
                
                bloques_libres.append({
                    "id": bloque['ID_Horario'],
                    "texto": f"{t_inicio_obj.strftime('%I:%M %p')} - {t_fin_obj.strftime('%I:%M %p')}"
                })

        cursor.close()
        return jsonify(bloques_libres) # Devuelve la lista

    except Exception as e:
        print(f"Error fatal en api_get_horarios: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn and conn.is_connected():
            conn.close()

@app.route('/estudiante/historial')
def est_historial():
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_estudiante = get_id_estudiante_by_usuario(id_usuario_actual)
    
    if not id_estudiante:
        flash('Error: Perfil de estudiante no encontrado.', 'danger')
        return redirect(url_for('agenda'))
        
    citas = []
    citas_calificadas = set()
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    try:
        cursor = conn.cursor(dictionary=True)
        
        # (NUEVO) 1. Obtener las citas que YA fueron calificadas
        sql_calificadas = "SELECT ID_Cita FROM Encuestas WHERE ID_Estudiante = %s"
        cursor.execute(sql_calificadas, (id_estudiante,))
        for row in cursor.fetchall():
            citas_calificadas.add(row['ID_Cita'])

        # 2. Obtener TODAS las citas del estudiante (igual que antes)
        sql_citas = """
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, 
                C.Nota_Ubicacion, C.Fecha_Solicitud,
                P.Nombre_Completo_Display AS Nombre_Psicologo
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
            WHERE 
                E.ID_Usuario = %s 
                AND (C.Estado_Cita = 'REALIZADA' OR C.Estado_Cita = 'CANCELADA')
            ORDER BY 
                C.Fecha_Cita DESC, C.Hora_Cita DESC
        """
        cursor.execute(sql_citas, (id_usuario_actual,))
        citas = cursor.fetchall()
        cursor.close()

        # 3. Formatear y añadir la bandera 'calificada'
        for c in citas:
            c['calificada'] = (c['ID_Cita'] in citas_calificadas)
            try:
                t_obj = datetime.strptime(c['Hora_Cita'], '%H:%M').time()
                c['Hora_Formateada'] = t_obj.strftime('%I:%M %p')
                c['Fecha_Formateada'] = c['Fecha_Cita'].strftime('%d / %m / %Y')
            except (ValueError, TypeError):
                c['Hora_Formateada'] = c['Hora_Cita']
                c['Fecha_Formateada'] = str(c['Fecha_Cita'])
        
    except Exception as e:
        print(f"Error al cargar historial del estudiante: {str(e)}")
        flash(f'Ocurrió un error al cargar tu historial: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('est_historial.html', citas=citas)

@app.route('/estudiante/calificar/<int:id_cita>', methods=['GET', 'POST'])
def est_calificar_cita(id_cita):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))
        
    id_usuario_actual = session['usuario']['id_usuario']
    id_estudiante = get_id_estudiante_by_usuario(id_usuario_actual)
    
    conn = get_db_connection()
    if conn is None: 
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('est_historial'))

    try:
        cursor = conn.cursor(dictionary=True)
        
        # 1. Verificar propiedad y estado de la cita
        sql_check = """
            SELECT C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, P.Nombre_Completo_Display
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
            WHERE C.ID_Cita = %s AND E.ID_Usuario = %s AND C.Estado_Cita = 'REALIZADA'
        """
        cursor.execute(sql_check, (id_cita, id_usuario_actual))
        cita_data = cursor.fetchone()
        
        if not cita_data:
            flash('Error: Cita no encontrada, no te pertenece o aún no ha sido marcada como realizada.', 'danger')
            return redirect(url_for('est_historial'))

        # 2. Verificar si ya fue calificada (por si acaso)
        cursor.execute("SELECT ID_Encuesta FROM Encuestas WHERE ID_Cita = %s", (id_cita,))
        if cursor.fetchone():
            flash('Esta cita ya ha sido calificada.', 'warning')
            return redirect(url_for('est_historial'))
            
        # 3. Lógica POST (Guardar la encuesta)
        if request.method == 'POST':
            calificacion = request.form.get('calificacion')
            comentario = request.form.get('comentario', '').strip()
            
            if not calificacion:
                flash('Debes seleccionar una calificación (1 a 5).', 'danger')
                return redirect(url_for('est_calificar_cita', id_cita=id_cita))
                
            sql_insert = """
                INSERT INTO Encuestas (ID_Cita, ID_Estudiante, Calificacion, Comentario)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql_insert, (id_cita, id_estudiante, calificacion, comentario))
            conn.commit()
            
            flash('¡Gracias! Tu calificación ha sido enviada.', 'success')
            return redirect(url_for('est_historial'))

        # 4. Lógica GET (Mostrar el formulario)
        # Formatear datos para la vista
        t_obj = datetime.strptime(cita_data['Hora_Cita'], '%H:%M').time()
        cita_data['Hora_Formateada'] = t_obj.strftime('%I:%M %p')
        cita_data['Fecha_Formateada'] = cita_data['Fecha_Cita'].strftime('%d / %m / %Y')
        
        return render_template('est_calificar_cita.html', cita=cita_data)

    except Exception as e:
        conn.rollback()
        print(f"Error en est_calificar_cita: {str(e)}")
        flash(f'Ocurrió un error al procesar la calificación: {str(e)}', 'danger')
        return redirect(url_for('est_historial'))
    finally:
        if conn and conn.is_connected():
            conn.close()

# Checkpoint
def get_id_estudiante_by_usuario(id_usuario):
    """Función auxiliar para obtener el ID_Estudiante dado un ID_Usuario."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT ID_Estudiante FROM Estudiantes WHERE ID_Usuario = %s", (id_usuario,))
            result = cursor.fetchone()
            cursor.close()
            return result['ID_Estudiante'] if result else None
        except Exception as e:
            print(f"Error al obtener ID_Estudiante: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()
    return None

"""-----------------  Pendiente para borrar  -----------------
@app.route('/est_ver')
def est_ver():
    return redirect(url_for('agenda'))  # Redirige a la agenda principal

@app.route('/psic_registrar')
def psic_registrar():
    return redirect(url_for('agenda'))  # Redirige a la agenda principal

@app.route('/psic_ver')
def psic_ver():
    return redirect(url_for('agenda'))  # Redirige a la agenda principal
"""

# ---- NUEVAS RUTAS PARA EL PSICÓLOGO ----

def get_id_psicologo_by_usuario(id_usuario):
    """Función auxiliar para obtener el ID_Psicologo dado un ID_Usuario."""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Verifica en Psicologos
            cursor.execute("SELECT ID_Psicologo FROM Psicologos WHERE ID_Usuario = %s", (id_usuario,))
            result = cursor.fetchone()
            cursor.close()
            return result['ID_Psicologo'] if result else None
        except Exception as e:
            print(f"Error al obtener ID_Psicologo: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()
    return None

# --- Rutas de Agenda/Estudiante (Mantener Existentes) ---
# ... (est_agendar, est_ver_o_editar, est_editar_cita, cancelar_cita, api_get_horarios, etc.)


# ---- NUEVAS RUTAS PARA EL PSICÓLOGO ----

@app.route('/psicologo/registrar_horario', methods=['GET', 'POST'])
def psic_registrar_horario():
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_psicologo = get_id_psicologo_by_usuario(id_usuario_actual)

    if not id_psicologo:
        flash('Perfil de psicólogo no encontrado.', 'danger')
        return redirect(url_for('agenda'))

    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash('Error de conexión a la base de datos.', 'danger')
            return redirect(url_for('agenda'))
        
        try:
            dia_semana = request.form.get('dia_semana')
            hora_inicio = request.form.get('hora_inicio')
            hora_fin = request.form.get('hora_fin')
            periodo = request.form.get('periodo_academico') or '2025-1' 

            if not all([dia_semana, hora_inicio, hora_fin]):
                flash('Complete todos los campos obligatorios del horario.', 'danger')
                return redirect(url_for('psic_registrar_horario'))

            cursor = conn.cursor()

            # Validación 1: Verificar que la Hora_Fin sea posterior a la Hora_Inicio
            # La comparación de strings 'HH:MM' funciona correctamente.
            if hora_inicio >= hora_fin:
                flash('Error: La hora de fin debe ser posterior a la hora de inicio.', 'danger')
                return redirect(url_for('psic_registrar_horario'))

            # Validación 2: Chequeo de solapamiento (Overlap)
            # El solapamiento ocurre si: (new_end > existing_start) AND (new_start < existing_end)
            sql_overlap = """
                SELECT ID_Horario 
                FROM Horarios_Disponibles 
                WHERE 
                    ID_Psicologo = %s AND Dia_Semana = %s 
                    AND (
                        %s > Hora_Inicio AND %s < Hora_Fin
                    )
            """
            # Parámetros: (ID_Psicologo, Dia_Semana, hora_fin (new end), hora_inicio (new start))
            cursor.execute(sql_overlap, (id_psicologo, dia_semana, hora_fin, hora_inicio))
            
            if cursor.fetchone():
                flash('Error: El nuevo horario se solapa o duplica con un horario ya registrado para ese día.', 'danger')
                return redirect(url_for('psic_registrar_horario'))

            # Si no hay solapamiento, proceder con la inserción
            sql = "INSERT INTO Horarios_Disponibles (ID_Psicologo, Dia_Semana, Hora_Inicio, Hora_Fin, Periodo_Academico) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (id_psicologo, dia_semana, hora_inicio, hora_fin, periodo))
            conn.commit()
            flash('Horario registrado exitosamente.', 'success')
            return redirect(url_for('psic_ver_horario'))

        except Exception as e:
            conn.rollback()
            print(f"Error al registrar horario: {str(e)}")
            flash(f'Ocurrió un error al registrar el horario: {str(e)}', 'danger')
        finally:
            if conn and conn.is_connected():
                conn.close()

    # GET request logic
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    # Simulamos el periodo actual de la DB
    periodo_academico_default = '2025-1' 
    
    return render_template('psic_horario_registro.html', 
                           dias=dias, 
                           periodo_default=periodo_academico_default)


@app.route('/psicologo/ver_horario')
def psic_ver_horario():
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_psicologo = get_id_psicologo_by_usuario(id_usuario_actual)
    horarios = []
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    try:
        cursor = conn.cursor(dictionary=True)
        # Ordenamos para mostrar Lunes a Domingo, luego por hora
        sql = "SELECT ID_Horario, Dia_Semana, Hora_Inicio, Hora_Fin, Periodo_Academico FROM Horarios_Disponibles WHERE ID_Psicologo = %s ORDER BY FIELD(Dia_Semana, 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'), Hora_Inicio"
        cursor.execute(sql, (id_psicologo,))
        horarios = cursor.fetchall()
        cursor.close()

        # Formateo de horas para la vista
        for h in horarios:
            try:
                t_inicio_obj = datetime.strptime(h['Hora_Inicio'], '%H:%M').time()
                t_fin_obj = datetime.strptime(h['Hora_Fin'], '%H:%M').time()
                h['Hora_Inicio_Formateada'] = t_inicio_obj.strftime('%I:%M %p')
                h['Hora_Fin_Formateada'] = t_fin_obj.strftime('%I:%M %p')
            except ValueError:
                # Caso de emergencia si la hora no tiene formato HH:MM
                h['Hora_Inicio_Formateada'] = h['Hora_Inicio']
                h['Hora_Fin_Formateada'] = h['Hora_Fin']
        
    except Exception as e:
        print(f"Error al cargar horarios: {str(e)}")
        flash(f'Ocurrió un error al cargar tus horarios: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('psic_horario_gestion.html', horarios=horarios)

@app.route('/psicologo/editar_cita_detalle/<int:id_cita>', methods=['GET', 'POST'])
def psic_editar_cita_detalle(id_cita):
    """
    Maneja la página dedicada para que el psicólogo edite
    detalles de la cita (por ahora, solo la ubicación).
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_psicologo = get_id_psicologo_by_usuario(session['usuario']['id_usuario'])
    conn = get_db_connection()
    if conn is None: 
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('psic_gestionar_citas'))

    try:
        # Verificar propiedad
        cita_data = psic_verificar_propiedad_cita(id_cita, id_psicologo, conn)
        if not cita_data:
            flash('Acción no permitida. Cita no encontrada.', 'danger')
            conn.close()
            return redirect(url_for('psic_gestionar_citas'))

        # Lógica POST (Guardar la nueva ubicación)
        if request.method == 'POST':
            nota_ubicacion = request.form.get('nota_ubicacion', '').strip()
            
            if not nota_ubicacion:
                flash('Error: La ubicación no puede estar vacía.', 'danger')
                return redirect(url_for('psic_editar_cita_detalle', id_cita=id_cita))

            cursor = conn.cursor()
            sql = """
                UPDATE Citas SET Nota_Ubicacion = %s 
                WHERE ID_Cita = %s AND (Estado_Cita = 'CONFIRMADA' OR Estado_Cita = 'REALIZADA')
            """
            cursor.execute(sql, (nota_ubicacion, id_cita))
            conn.commit()
            
            flash('Ubicación actualizada correctamente.', 'success')
            return redirect(url_for('psic_gestionar_citas'))

        # Lógica GET (Mostrar el formulario de edición)
        # Necesitamos más datos de la cita para mostrar en la página
        cursor = conn.cursor(dictionary=True)
        sql_get_full = """
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, C.Nota_Ubicacion,
                U.Nombres AS Estudiante_Nombres, U.Apellidos AS Estudiante_Apellidos
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Usuarios U ON E.ID_Usuario = U.ID_Usuario
            WHERE C.ID_Cita = %s AND C.ID_Psicologo = %s
        """
        cursor.execute(sql_get_full, (id_cita, id_psicologo))
        cita_completa = cursor.fetchone()
        
        # Formateo
        t_obj = datetime.strptime(cita_completa['Hora_Cita'], '%H:%M').time()
        cita_completa['Hora_Formateada'] = t_obj.strftime('%I:%M %p')
        cita_completa['Fecha_Formateada'] = cita_completa['Fecha_Cita'].strftime('%d / %m / %Y')
        
        return render_template('psic_editar_cita_detalle.html', cita=cita_completa)

    except Exception as e:
        conn.rollback()
        flash(f'Error al procesar la edición: {str(e)}', 'danger')
        return redirect(url_for('psic_gestionar_citas'))
    finally:
        if conn and conn.is_connected(): conn.close()

@app.route('/psicologo/editar_horario/<int:id_horario>', methods=['GET', 'POST'])
def psic_editar_horario(id_horario):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_psicologo = get_id_psicologo_by_usuario(id_usuario_actual)
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('psic_ver_horario'))

    try:
        cursor = conn.cursor(dictionary=True)
        # Obtener el horario y verificar propiedad
        sql_select = "SELECT ID_Horario, Dia_Semana, Hora_Inicio, Hora_Fin, Periodo_Academico FROM Horarios_Disponibles WHERE ID_Horario = %s AND ID_Psicologo = %s"
        cursor.execute(sql_select, (id_horario, id_psicologo))
        horario_data = cursor.fetchone()

        if not horario_data:
            flash('Bloque de horario no encontrado o no te pertenece.', 'danger')
            return redirect(url_for('psic_ver_horario'))

        if request.method == 'POST':
            dia_semana = request.form.get('dia_semana')
            hora_inicio = request.form.get('hora_inicio')
            hora_fin = request.form.get('hora_fin')
            periodo = request.form.get('periodo_academico')

            if not all([dia_semana, hora_inicio, hora_fin, periodo]):
                flash('Complete todos los campos obligatorios.', 'danger')
            else:
                sql_update = "UPDATE Horarios_Disponibles SET Dia_Semana = %s, Hora_Inicio = %s, Hora_Fin = %s, Periodo_Academico = %s WHERE ID_Horario = %s"
                cursor.execute(sql_update, (dia_semana, hora_inicio, hora_fin, periodo, id_horario))
                conn.commit()
                flash('Horario actualizado correctamente.', 'success')
                return redirect(url_for('psic_ver_horario'))

        return render_template('psic_horario_editar.html', 
                               horario=horario_data, 
                               dias=dias)

    except Exception as e:
        conn.rollback()
        print(f"Error al editar horario: {str(e)}")
        flash(f'Ocurrió un error al editar el horario: {str(e)}', 'danger')
        return redirect(url_for('psic_ver_horario'))
    finally:
        if conn and conn.is_connected():
            conn.close()


@app.route('/psicologo/eliminar_horario/<int:id_horario>', methods=['POST'])
def psic_eliminar_horario(id_horario):
    # Lógica de verificación y eliminación (Mantenida del paso anterior, solo verificada)
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_psicologo = get_id_psicologo_by_usuario(id_usuario_actual)
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('psic_ver_horario'))

    try:
        cursor = conn.cursor()
        
        # 1. Verificar si el horario pertenece al psicólogo logueado (Seguridad)
        cursor.execute("SELECT ID_Psicologo FROM Horarios_Disponibles WHERE ID_Horario = %s", (id_horario,))
        horario_data = cursor.fetchone()
        
        if horario_data is None or horario_data[0] != id_psicologo:
            flash('Error: Horario no encontrado o no te pertenece.', 'danger')
            return redirect(url_for('psic_ver_horario'))
            
        # 2. Eliminar el horario
        sql_delete = "DELETE FROM Horarios_Disponibles WHERE ID_Horario = %s"
        cursor.execute(sql_delete, (id_horario,))
        conn.commit()
        
        flash('Bloque de horario eliminado correctamente.', 'success')
        
    except Exception as e:
        conn.rollback()
        print(f"Error al eliminar horario: {str(e)}")
        flash(f'Ocurrió un error al eliminar el horario: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return redirect(url_for('psic_ver_horario'))

#--- Rutas para Gestión de Citas del Psicólogo ---

@app.route('/psicologo/gestionar_citas')
def psic_gestionar_citas():
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_usuario_actual = session['usuario']['id_usuario']
    id_psicologo = get_id_psicologo_by_usuario(id_usuario_actual)
    citas = []
    
    conn = get_db_connection()
    if conn is None:
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('agenda'))

    try:
        cursor = conn.cursor(dictionary=True)
        # (ARREGLO: Añadido C.Nota_Ubicacion al SELECT)
        sql = """
            SELECT 
                C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, C.Fecha_Solicitud,
                C.Nota_Ubicacion, 
                U.Nombres AS Estudiante_Nombres, 
                U.Apellidos AS Estudiante_Apellidos,
                E.Telefono_Contacto
            FROM Citas C
            JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
            JOIN Usuarios U ON E.ID_Usuario = U.ID_Usuario
            WHERE C.ID_Psicologo = %s
            ORDER BY 
                FIELD(C.Estado_Cita, 'SOLICITADA', 'CONFIRMADA', 'REALIZADA', 'CANCELADA'), 
                C.Fecha_Cita, C.Hora_Cita
        """
        cursor.execute(sql, (id_psicologo,))
        citas = cursor.fetchall()
        cursor.close()

        # Formateo de horas y fechas para la vista
        for c in citas:
            try:
                t_obj = datetime.strptime(c['Hora_Cita'], '%H:%M').time()
                c['Hora_Formateada'] = t_obj.strftime('%I:%M %p')
                c['Fecha_Formateada'] = c['Fecha_Cita'].strftime('%d / %m / %Y')
            except (ValueError, TypeError):
                c['Hora_Formateada'] = c['Hora_Cita']
                c['Fecha_Formateada'] = str(c['Fecha_Cita'])
        
    except Exception as e:
        print(f"Error al cargar citas del psicólogo: {str(e)}")
        flash(f'Ocurrió un error al cargar las citas: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected():
            conn.close()

    return render_template('psic_gestionar_citas.html', citas=citas)

def psic_verificar_propiedad_cita(id_cita, id_psicologo, conn):
    """Función auxiliar para verificar si una cita pertenece al psicólogo."""
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ID_Cita FROM Citas WHERE ID_Cita = %s AND ID_Psicologo = %s", (id_cita, id_psicologo))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error en verificación de propiedad: {e}")
        return None

@app.route('/psicologo/confirmar_cita/<int:id_cita>', methods=['POST'])
def psic_confirmar_cita(id_cita):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_psicologo = get_id_psicologo_by_usuario(session['usuario']['id_usuario'])
    
    # (NUEVO) Obtener la nota de ubicación desde el formulario
    nota_ubicacion = request.form.get('nota_ubicacion', '').strip()

    conn = get_db_connection()
    if conn is None: 
        flash('Error de conexión a la base de datos.', 'danger')
        return redirect(url_for('psic_gestionar_citas'))

    try:
        # (NUEVO) Validación: Asegurarse de que la ubicación no esté vacía
        if not nota_ubicacion:
            flash('Error: Debes especificar una ubicación para confirmar la cita.', 'danger')
            return redirect(url_for('psic_gestionar_citas'))

        if not psic_verificar_propiedad_cita(id_cita, id_psicologo, conn):
            flash('Acción no permitida. Cita no encontrada.', 'danger')
            return redirect(url_for('psic_gestionar_citas'))

        cursor = conn.cursor()
        
        # (ACTUALIZADO) La consulta SQL ahora actualiza el Estado Y la Nota_Ubicacion
        sql = """
            UPDATE Citas 
            SET Estado_Cita = 'CONFIRMADA', Nota_Ubicacion = %s 
            WHERE ID_Cita = %s AND Estado_Cita = 'SOLICITADA'
        """
        cursor.execute(sql, (nota_ubicacion, id_cita))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash('Cita confirmada exitosamente.', 'success')
        else:
            flash('La cita no se pudo confirmar (quizás ya estaba confirmada o cancelada).', 'warning')

    except Exception as e:
        conn.rollback()
        flash(f'Error al confirmar la cita: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected(): conn.close()
        
    return redirect(url_for('psic_gestionar_citas'))

@app.route('/psicologo/cancelar_cita/<int:id_cita>', methods=['POST'])
def psic_cancelar_cita(id_cita):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_psicologo = get_id_psicologo_by_usuario(session['usuario']['id_usuario'])
    conn = get_db_connection()
    if conn is None: return redirect(url_for('psic_gestionar_citas'))

    try:
        if not psic_verificar_propiedad_cita(id_cita, id_psicologo, conn):
            flash('Acción no permitida. Cita no encontrada.', 'danger')
            return redirect(url_for('psic_gestionar_citas'))

        cursor = conn.cursor()
        sql = "UPDATE Citas SET Estado_Cita = 'CANCELADA' WHERE ID_Cita = %s AND (Estado_Cita = 'SOLICITADA' OR Estado_Cita = 'CONFIRMADA')"
        cursor.execute(sql, (id_cita,))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash('Cita cancelada exitosamente.', 'success')
        else:
            flash('La cita no se pudo cancelar.', 'warning')

    except Exception as e:
        conn.rollback()
        flash(f'Error al cancelar la cita: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected(): conn.close()
        
    return redirect(url_for('psic_gestionar_citas'))

@app.route('/psicologo/realizar_cita/<int:id_cita>', methods=['POST'])
def psic_realizar_cita(id_cita):
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_psicologo = get_id_psicologo_by_usuario(session['usuario']['id_usuario'])
    conn = get_db_connection()
    if conn is None: return redirect(url_for('psic_gestionar_citas'))

    try:
        if not psic_verificar_propiedad_cita(id_cita, id_psicologo, conn):
            flash('Acción no permitida. Cita no encontrada.', 'danger')
            return redirect(url_for('psic_gestionar_citas'))

        cursor = conn.cursor()
        # Solo se puede marcar como REALIZADA si estaba CONFIRMADA
        sql = "UPDATE Citas SET Estado_Cita = 'REALIZADA' WHERE ID_Cita = %s AND Estado_Cita = 'CONFIRMADA'"
        cursor.execute(sql, (id_cita,))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash('Cita marcada como REALIZADA exitosamente.', 'success')
        else:
            flash('La cita no se pudo marcar como realizada (debe estar confirmada).', 'warning')

    except Exception as e:
        conn.rollback()
        flash(f'Error al marcar la cita: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected(): conn.close()
        
    return redirect(url_for('psic_gestionar_citas'))


@app.route('/psicologo/revertir_cita/<int:id_cita>', methods=['POST'])
def psic_revertir_cita(id_cita):
    """
    Permite al psicólogo devolver una cita 'CONFIRMADA' a 'SOLICITADA' 
    en caso de error al confirmar.
    """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Psicologo':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('index1'))

    id_psicologo = get_id_psicologo_by_usuario(session['usuario']['id_usuario'])
    conn = get_db_connection()
    if conn is None: return redirect(url_for('psic_gestionar_citas'))

    try:
        if not psic_verificar_propiedad_cita(id_cita, id_psicologo, conn):
            flash('Acción no permitida. Cita no encontrada.', 'danger')
            return redirect(url_for('psic_gestionar_citas'))

        cursor = conn.cursor()
        
        # (MODIFICADO) Establece la ubicación a NULL (vacío)
        sql = """
            UPDATE Citas 
            SET Estado_Cita = 'SOLICITADA', Nota_Ubicacion = NULL 
            WHERE ID_Cita = %s AND Estado_Cita = 'CONFIRMADA'
        """
        cursor.execute(sql, (id_cita,))
        conn.commit()
        
        if cursor.rowcount > 0:
            flash('Cita devuelta al estado SOLICITADA.', 'success')
        else:
            flash('La cita no se pudo revertir (debe estar confirmada).', 'warning')

    except Exception as e:
        conn.rollback()
        flash(f'Error al revertir la cita: {str(e)}', 'danger')
    finally:
        if conn and conn.is_connected(): conn.close()
        
    return redirect(url_for('psic_gestionar_citas'))

# ---- RUTAS DEL CHATBOT ----
# (Asegúrate de eliminar las funciones antiguas 'process_chatbot_message' y 'get_psicologos_info' si existen)

def process_chatbot_message(message, usuario):
    """
    Procesa el mensaje del usuario y genera una respuesta inteligente
    basada en el ROL del usuario.
    """
    rol = usuario.get('rol')
    nombres = usuario.get('nombres', 'Usuario')
    message_lower = message.lower()

    # --- Palabras clave ---
    saludos = ['hola', 'hi', 'hey', 'buenos días', 'buenas tardes', 'buenas noches']
    ayuda_keywords = ['ayuda', 'qué puedes', 'info', 'comandos', 'funciones']
    
    # Palabras clave Estudiante
    cancelar_keywords = ['cancelar', 'cancelar cita', 'ya no quiero', 'no puedo ir', 'eliminar cita']
    mis_citas_keywords = ['mis citas', 'citas activas', 'ver cita', 'cita pendiente', 'mi cita']
    agendar_keywords = ['agendar', 'nueva cita', 'reservar', 'pedir cita']
    historial_keywords = ['historial', 'citas pasadas', 'citas anteriores', 'mis citas anteriores']
    calificar_keywords = ['calificar', 'calificar cita', 'pendiente calificar', 'encuesta', 'opinar']

    # --- Lógica de Saludos (Universal) ---
    if any(saludo in message_lower for saludo in saludos):
        if rol == 'Estudiante':
            return {
                'success': True,
                'response': f'¡Hola {nombres}! 👋 Soy tu asistente. ¿Cómo puedo ayudarte hoy?',
                'actions': [
                    {'type': 'redirect', 'text': '📅 Agendar Cita', 'url': '/est_agendar'},
                    {'type': 'fetch_active_citas', 'text': '👁️ Ver mi Cita Activa'},
                    {'type': 'fetch_historial', 'text': '📚 Ver Historial de Citas'},
                    {'type': 'prompt_cancel', 'text': '🚫 Cancelar mi Cita Activa'}
                ]
            }
        elif rol == 'Psicologo':
            return {
                'success': True,
                'response': f'¡Hola Dr(a). {nombres}! 👋 Soy el asistente de RESILIENCE.',
                'actions': [
                    {'type': 'redirect', 'text': '🗓️ Gestionar mis Citas', 'url': '/psicologo/gestionar_citas'},
                    {'type': 'redirect', 'text': '➕ Registrar Disponibilidad', 'url': '/psicologo/registrar_horario'},
                    {'type': 'redirect', 'text': '✏️ Ver/Editar mi Horario', 'url': '/psicologo/ver_horario'}
                ]
            }
        elif rol == 'Admin':
             return {
                'success': True,
                'response': f'¡Hola {nombres}! (Admin) 👋. ¿Qué deseas gestionar?',
                'actions': [
                    {'type': 'redirect', 'text': '🧑‍⚕️ Gestionar Roles (Psicólogos)', 'url': '/admin/roles'}
                ]
            }
        else:
             return {'success': True, 'response': f'¡Hola {nombres}! 👋'}

    # --- Lógica por ROL ---

    # --- ROL ESTUDIANTE ---
    if rol == 'Estudiante':
        if any(keyword in message_lower for keyword in cancelar_keywords):
            # 1. Intención: Cancelar Cita
            return {
                'success': True,
                'response': 'Veo que quieres cancelar tu cita activa. ¿Estás seguro? Esta acción no se puede deshacer.',
                'actions': [
                    {'type': 'exec_cancel', 'text': 'Sí, estoy seguro, cancelar'},
                    {'type': 'abort_cancel', 'text': 'No, conservar mi cita'}
                ]
            }
        
        if any(keyword in message_lower for keyword in mis_citas_keywords):
            # 2. Intención: Ver Citas Activas
            return {
                'success': True,
                'response': 'Entendido. Voy a buscar tu cita activa (Solicitada o Confirmada)...',
                'actions': [{'type': 'fetch_active_citas'}] 
            }

        if any(keyword in message_lower for keyword in agendar_keywords):
            # 3. Intención: Agendar (Redirigir)
            return {
                'success': True,
                'response': '¡Claro! Para agendar una nueva cita, haz clic aquí:',
                'actions': [
                    {'type': 'redirect', 'text': '📅 Ir a Agendar Cita', 'url': '/est_agendar'}
                ]
            }
            
        if any(keyword in message_lower for keyword in historial_keywords):
            # 4. Intención: Ver Historial
            return {
                'success': True,
                'response': 'Consultando tu historial de citas (Realizadas y Canceladas)...',
                'actions': [{'type': 'fetch_historial'}]
            }

        if any(keyword in message_lower for keyword in calificar_keywords):
            # 5. Intención: Calificar
            return {
                'success': True,
                'response': 'Consultando si tienes citas pendientes por calificar...',
                'actions': [{'type': 'fetch_pendientes'}]
            }

        if any(keyword in message_lower for keyword in ayuda_keywords):
            # 6. Intención: Ayuda (Estudiante)
            return {
                'success': True,
                'response': 'Como estudiante, puedo ayudarte con esto:',
                'actions': [
                    {'type': 'redirect', 'text': '📅 Agendar Cita', 'url': '/est_agendar'},
                    {'type': 'fetch_active_citas', 'text': '👁️ Ver mi Cita Activa'},
                    {'type': 'fetch_historial', 'text': '📚 Ver Historial de Citas'},
                    {'type': 'fetch_pendientes', 'text': '⭐ Calificar Citas'},
                    {'type': 'prompt_cancel', 'text': '🚫 Cancelar mi Cita Activa'}
                ]
            }
        
        # Default Estudiante
        return {
            'success': True,
            'response': 'No entendí muy bien. ¿Qué necesitas? (Intenta con "ayuda" para ver opciones).',
            'actions': [{'type': 'ayuda', 'text': 'Ver comandos de Ayuda'}]
        }

    # --- ROL PSICOLOGO ---
    elif rol == 'Psicologo':
        if 'citas' in message_lower or 'pacientes' in message_lower:
            return {
                'success': True,
                'response': 'Para ver y administrar tus citas (confirmar, cancelar, etc.), ve al panel de gestión:',
                'actions': [{'type': 'redirect', 'text': '🗓️ Gestionar mis Citas', 'url': '/psicologo/gestionar_citas'}]
            }
        if 'horario' in message_lower or 'disponibilidad' in message_lower:
             return {
                'success': True,
                'response': 'Puedes gestionar tu disponibilidad desde estos enlaces:',
                'actions': [
                    {'type': 'redirect', 'text': '➕ Registrar Disponibilidad', 'url': '/psicologo/registrar_horario'},
                    {'type': 'redirect', 'text': '✏️ Ver/Editar mi Horario', 'url': '/psicologo/ver_horario'}
                ]
            }
        # Default Psicologo
        return {
            'success': True,
            'response': f'Hola Dr(a). {nombres}. Como psicólogo, puedes gestionar tus citas y horarios desde la Agenda.',
            'actions': [
                {'type': 'redirect', 'text': '🗓️ Gestionar mis Citas', 'url': '/psicologo/gestionar_citas'},
                {'type': 'redirect', 'text': '➕ Registrar Disponibilidad', 'url': '/psicologo/registrar_horario'}
            ]
        }

    # --- ROL ADMIN ---
    elif rol == 'Admin':
        # Default Admin
        return {
            'success': True,
            'response': f'Hola {nombres} (Admin). Tu función principal es la asignación de roles de psicólogo.',
            'actions': [
                {'type': 'redirect', 'text': '🧑‍⚕️ Gestionar Roles (Psicólogos)', 'url': '/admin/roles'}
            ]
        }
    
    # --- Sin Rol / Error ---
    return {'success': True, 'response': 'No estoy seguro de cómo ayudarte. ¿Podrías ser más específico?'}


@app.route('/chatbot/query', methods=['POST'])
def chatbot_query():
    if 'usuario' not in session:
        return jsonify({'success': False, 'response': 'Debes iniciar sesión para usar el chatbot.'})
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        # Procesar el mensaje y determinar la intención
        # (MODIFICADO) Pasa la sesión completa del usuario
        response_data = process_chatbot_message(user_message, session['usuario'])
        
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error en chatbot: {str(e)}")
        return jsonify({'success': False, 'response': 'Error procesando tu mensaje.'})

@app.route('/chatbot/mis_citas')
def chatbot_mis_citas():
    """ (MANTENIDA) Obtiene la cita ACTIVA (Solicitada o Confirmada) del estudiante. """
    if 'usuario' not in session:
        return jsonify({'success': False, 'citas': []})
    
    id_usuario_actual = session['usuario']['id_usuario']
    citas = []
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT 
                    C.ID_Cita, C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, C.Nota_Ubicacion,
                    P.Nombre_Completo_Display AS Nombre_Psicologo
                FROM Citas C
                JOIN Estudiantes E ON C.ID_Estudiante = E.ID_Estudiante
                JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
                WHERE E.ID_Usuario = %s AND C.Estado_Cita IN ('SOLICITADA', 'CONFIRMADA')
                ORDER BY C.Fecha_Cita, C.Hora_Cita
            """
            cursor.execute(sql, (id_usuario_actual,))
            citas_db = cursor.fetchall()
            cursor.close()
            
            # Formatear las citas
            for cita in citas_db:
                try:
                    t_obj = datetime.strptime(cita['Hora_Cita'], '%H:%M').time()
                    hora_formateada = t_obj.strftime('%I:%M %p')
                except:
                    hora_formateada = cita['Hora_Cita']
                
                citas.append({
                    'fecha': cita['Fecha_Cita'].strftime('%d/%m/%Y'),
                    'hora': hora_formateada,
                    'psicologo': cita['Nombre_Psicologo'],
                    'estado': cita['Estado_Cita'],
                    'ubicacion': cita['Nota_Ubicacion']
                })
                
        except Exception as e:
            print(f"Error al obtener citas para chatbot: {str(e)}")
        finally:
            if conn.is_connected():
                conn.close()
    
    return jsonify({'success': True, 'citas': citas})

@app.route('/chatbot/mi_historial')
def chatbot_mi_historial():
    """ (NUEVO) Obtiene el historial de citas (pasadas) del estudiante. """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        return jsonify({'success': False, 'citas': []})

    id_usuario_actual = session['usuario']['id_usuario']
    id_estudiante = get_id_estudiante_by_usuario(id_usuario_actual)
    if not id_estudiante:
        return jsonify({'success': False, 'citas': []})
        
    citas = []
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT C.Fecha_Cita, C.Hora_Cita, C.Estado_Cita, P.Nombre_Completo_Display AS Nombre_Psicologo
                FROM Citas C
                JOIN Psicologos P ON C.ID_Psicologo = P.ID_Psicologo
                WHERE C.ID_Estudiante = %s 
                AND C.Estado_Cita IN ('REALIZADA', 'CANCELADA')
                ORDER BY C.Fecha_Cita DESC
                LIMIT 5
            """
            cursor.execute(sql, (id_estudiante,))
            citas_db = cursor.fetchall()
            cursor.close()
            
            for cita in citas_db:
                t_obj = datetime.strptime(cita['Hora_Cita'], '%H:%M').time()
                citas.append({
                    'fecha': cita['Fecha_Cita'].strftime('%d/%m/%Y'),
                    'hora': t_obj.strftime('%I:%M %p'),
                    'psicologo': cita['Nombre_Psicologo'],
                    'estado': cita['Estado_Cita']
                })
        except Exception as e:
            print(f"Error en chatbot_mi_historial: {str(e)}")
        finally:
            if conn.is_connected(): conn.close()
    
    return jsonify({'success': True, 'citas': citas})

@app.route('/chatbot/citas_pendientes_calificar')
def chatbot_citas_pendientes_calificar():
    """ (NUEVO) Revisa cuántas citas 'REALIZADAS' no tienen 'ENCUESTA'. """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        return jsonify({'success': False, 'count': 0})

    id_usuario_actual = session['usuario']['id_usuario']
    id_estudiante = get_id_estudiante_by_usuario(id_usuario_actual)
    if not id_estudiante:
        return jsonify({'success': False, 'count': 0})
        
    count = 0
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # Contamos las citas REALIZADAS que NO ESTÁN en la tabla de Encuestas
            sql = """
                SELECT COUNT(C.ID_Cita) AS pendientes
                FROM Citas C
                LEFT JOIN Encuestas E ON C.ID_Cita = E.ID_Cita
                WHERE C.ID_Estudiante = %s
                AND C.Estado_Cita = 'REALIZADA'
                AND E.ID_Encuesta IS NULL
            """
            cursor.execute(sql, (id_estudiante,))
            resultado = cursor.fetchone()
            if resultado:
                count = resultado['pendientes']
            cursor.close()
        except Exception as e:
            print(f"Error en chatbot_citas_pendientes_calificar: {str(e)}")
        finally:
            if conn.is_connected(): conn.close()
            
    return jsonify({'success': True, 'count': count})

@app.route('/chatbot/cancelar_mi_cita', methods=['POST'])
def chatbot_cancelar_mi_cita():
    """ (NUEVO) Cancela la cita activa (SOLICITADA o CONFIRMADA) del estudiante. """
    if 'usuario' not in session or session['usuario'].get('rol') != 'Estudiante':
        return jsonify({'success': False, 'message': 'No autorizado.'})

    id_usuario_actual = session['usuario']['id_usuario']
    id_estudiante = get_id_estudiante_by_usuario(id_usuario_actual)
    if not id_estudiante:
        return jsonify({'success': False, 'message': 'Perfil de estudiante no encontrado.'})

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            # 1. Encontrar la cita activa
            sql_find = """
                SELECT ID_Cita FROM Citas 
                WHERE ID_Estudiante = %s AND Estado_Cita IN ('SOLICITADA', 'CONFIRMADA')
            """
            cursor.execute(sql_find, (id_estudiante,))
            cita_activa = cursor.fetchone()
            
            if not cita_activa:
                return jsonify({'success': False, 'message': 'No se encontró una cita activa para cancelar.'})

            # 2. Cancelar la cita
            id_cita_a_cancelar = cita_activa['ID_Cita']
            sql_cancel = "UPDATE Citas SET Estado_Cita = 'CANCELADA' WHERE ID_Cita = %s"
            cursor.execute(sql_cancel, (id_cita_a_cancelar,))
            conn.commit()
            
            return jsonify({'success': True, 'message': '¡Tu cita ha sido cancelada exitosamente!'})

        except Exception as e:
            conn.rollback()
            print(f"Error en chatbot_cancelar_mi_cita: {str(e)}")
            return jsonify({'success': False, 'message': f'Error de servidor: {str(e)}'})
        finally:
            if conn.is_connected(): conn.close()
            
    return jsonify({'success': False, 'message': 'Error de conexión a la base de datos.'})

@app.route('/debug_static')
def debug_static():
    base = os.path.join(os.path.dirname(__file__), 'static')
    output = {}
    for root, dirs, files in os.walk(base):
        rel = os.path.relpath(root, base)
        output[rel] = files
    # Indicar si index1.css existe
    output['_index1_exists'] = os.path.exists(os.path.join(base, 'index1.css'))
    return jsonify(output)

if __name__ == '__main__':
    app.run(debug=True)
