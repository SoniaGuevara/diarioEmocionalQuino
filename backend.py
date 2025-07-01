# -*- coding: utf-8 -*-
import pandas as pd
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

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

# Nombre del archivo donde guardaremos todas las respuestas.
NOMBRE_ARCHIVO_EXCEL = 'diario_emocional_escolar.xlsx'

def guardar_en_excel(nuevos_datos):
    """
    Esta función recibe los datos recogidos del usuario y los guarda
    en un archivo de Excel. Si el archivo ya existe, añade los datos
    nuevos al final, sin borrar los anteriores.
    """
    try:
        # Creamos un DataFrame con los nuevos datos.
        df_nuevos = pd.DataFrame([nuevos_datos])

        if os.path.exists(NOMBRE_ARCHIVO_EXCEL):
            # Leemos el archivo existente
            df_existente = pd.read_excel(NOMBRE_ARCHIVO_EXCEL)
            # Unimos el dataframe existente con el nuevo
            df_final = pd.concat([df_existente, df_nuevos], ignore_index=True)
        else:
            # Si el archivo no existe, el nuevo dataframe es el final
            df_final = df_nuevos

        # Reordenamos las columnas para que siempre tengan el mismo orden
        columnas_ordenadas = ['Curso', 'Materia', 'Sentimiento', 'Causa', 'Explicacion Adicional']
        df_final = df_final[columnas_ordenadas]

        # Guardamos el dataframe final en el archivo Excel
        df_final.to_excel(NOMBRE_ARCHIVO_EXCEL, index=False)
        print(f"✅ Registro guardado correctamente en {NOMBRE_ARCHIVO_EXCEL}") # Log para confirmar
        return True

    except Exception as e:
        print(f"❌ Ha ocurrido un error al guardar en Excel: {e}")
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

    # Guardamos en el archivo Excel
    if guardar_en_excel(datos_recogidos):
        return jsonify({"success": True, "message": "¡Registro guardado con éxito!"})
    else:
        return jsonify({"success": False, "message": "Error al guardar el registro."}), 500

# --- INICIAR EL SERVIDOR ---
if __name__ == '__main__':
    # --- CAMBIO IMPORTANTE ---
    # Desactivamos el "reloader" automático (use_reloader=False) para evitar 
    # que el servidor se reinicie cada vez que guardamos el archivo Excel.
    #
    # NOTA: Si haces cambios en este archivo (backend.py), tendrás que detener 
    # el servidor (Ctrl+C) y volver a iniciarlo manualmente para ver los cambios.
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
