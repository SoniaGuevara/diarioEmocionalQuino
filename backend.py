# -*- coding: utf-8 -*-
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import gspread # Importamos la librería para interactuar con Google Sheets
from oauth2client.service_account import ServiceAccountCredentials # Importamos para las credenciales

# --- INICIALIZACIÓN DE LA APLICACIÓN FLASK ---
app = Flask(__name__)
# Habilitamos CORS para permitir que el frontend se comunique con este backend
CORS(app)

# --- LISTAS DE OPCIONES PARA LOS MENÚS DESPLEGABLES ---
# Estas son las opciones que se enviarán al frontend.
CURSOS_DISPONIBLES = ["1ro A", "1ro B", "2do A", "2do B", "3ro A", "4to A", "5to A", "6to A"]
MATERIAS_DISPONIBLES = [
    "Matemática", "Lengua y Literatura", "Historia", "Geografía",
    "Biología", "Física", "Química", "Educación Física", "Inglés", "Otra"
]
EMOCIONES_DISPONIBLES = [
    "Feliz", "Triste", "Enojado/a", "Ansioso/a",
    "Sorprendido/a", "Con miedo", "Con calma", "Agradecido/a"
]
CAUSAS_POSIBLES = [
    "Una tarea o examen", "Una situación con compañeros", "Una situación con un profesor",
    "Algo que pasó en casa", "No estoy seguro/a", "Otro motivo"
]

# --- CONFIGURACIÓN DE GOOGLE SHEETS ---
# Define el nombre de tu archivo de credenciales JSON
RUTA_CREDENCIALES = 'credentials.json'
# Define el nombre de tu hoja de cálculo en Google Sheets
NOMBRE_HOJA_CALCULO = 'Diario Emocional - Registros'

def guardar_en_google_sheets(nuevos_datos):
    """
    Esta función recibe los datos recogidos del usuario y los guarda
    en la Hoja de Google especificada.
    """
    try:
        # Define los alcances de la API (permisos que necesita la cuenta de servicio)
        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        # Carga las credenciales desde el archivo JSON
        # La ruta del archivo de credenciales debe ser correcta
        creds = ServiceAccountCredentials.from_json_keyfile_name(RUTA_CREDENCIALES, scope)
        
        # Autoriza el cliente de gspread
        client = gspread.authorize(creds)

        # Abre la hoja de cálculo por su nombre
        # Asegúrate de que el nombre de la hoja de cálculo coincida exactamente
        sheet = client.open(NOMBRE_HOJA_CALCULO).sheet1 # .sheet1 selecciona la primera hoja dentro del documento

        # Prepara los datos como una lista en el orden de tus columnas
        # Es crucial que el orden aquí coincida con los encabezados en tu Google Sheet
        fila_a_insertar = [
            nuevos_datos.get('Curso'),
            nuevos_datos.get('Materia'),
            nuevos_datos.get('Sentimiento'),
            nuevos_datos.get('Causa'),
            nuevos_datos.get('Explicacion Adicional')
        ]

        # Añade la nueva fila al final de la hoja
        sheet.append_row(fila_a_insertar)
        
        print(f"✅ Registro guardado correctamente en Google Sheets: {NOMBRE_HOJA_CALCULO}")
        return True

    except Exception as e:
        print(f"❌ Ha ocurrido un error al guardar en Google Sheets: {e}")
        # Puedes añadir más detalles del error si es necesario para depuración
        # Por ejemplo: print(traceback.format_exc())
        return False

# --- RUTAS DE LA API ---

@app.route('/api/options', methods=['GET'])
def get_options():
    """
    Endpoint para que el frontend pueda obtener las listas de opciones
    para rellenar los menús desplegables.
    """
    options = {
        "cursos": CURSOS_DISPONIBLES,
        "materias": MATERIAS_DISPONIBLES,
        "emociones": EMOCIONES_DISPONIBLES,
        "causas": CAUSAS_POSIBLES
    }
    return jsonify(options)

@app.route('/api/submit', methods=['POST'])
def submit_entry():
    """
    Endpoint para recibir los datos del formulario del frontend
    y guardarlos.
    """
    # Obtenemos los datos enviados desde el frontend en formato JSON
    data = request.get_json()
    print("➡️  Datos recibidos en /api/submit:", data) # Log para ver qué llega

    # Validamos que los datos necesarios estén presentes
    if not data or 'curso' not in data or 'sentimiento' not in data:
        return jsonify({"success": False, "message": "Faltan datos."}), 400

    # Creamos el diccionario para guardar
    datos_recogidos = {
        'Curso': data.get('curso'),
        'Materia': data.get('materia'),
        'Sentimiento': data.get('sentimiento'),
        'Causa': data.get('causa'),
        'Explicacion Adicional': data.get('explicacion', '')
    }

    # Guardamos en la Hoja de Google
    if guardar_en_google_sheets(datos_recogidos):
        return jsonify({"success": True, "message": "¡Registro guardado con éxito en Google Sheets!"})
    else:
        return jsonify({"success": False, "message": "Error al guardar el registro en Google Sheets."}), 500

# --- INICIAR EL SERVIDOR ---
if __name__ == '__main__':
    # --- CAMBIO IMPORTANTE ---
    # Desactivamos el "reloader" automático (use_reloader=False) para evitar 
    # que el servidor se reinicie cada vez que guardamos el archivo Excel.
    #
    # NOTA: Si haces cambios en este archivo (backend.py), tendrás que detener 
    # el servidor (Ctrl+C) y volver a iniciarlo manualmente para ver los cambios.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)

