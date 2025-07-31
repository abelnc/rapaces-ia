# Añadir al inicio (junto a otros imports)
import logging
logging.basicConfig(level=logging.INFO)

# Modificar la función call_inaturalist_api
def call_inaturalist_api(image_path):
    try:
        url = "https://api.inaturalist.org/v1/identifications"
        headers = {'User-Agent': 'RapacesIA/1.0 (tu@email.com)'}  # Identificación requerida
        files = {'file': open(image_path, 'rb')}
        
        response = requests.post(url, files=files, headers=headers, timeout=10)
        response.raise_for_status()  # Lanza error si HTTP != 200
        
        data = response.json()
        if not data.get('results'):
            logging.warning("API no devolvió resultados")
            return None
            
        best_match = data['results'][0]['taxon']
        return {
            'common_name': best_match.get('preferred_common_name', 'Desconocido'),
            'scientific_name': best_match.get('name', 'No identificado'),
            'confidence': round(best_match.get('score', 0) * 100, 2)
        }
    except requests.exceptions.RequestException as e:
        logging.error(f"Error en API: {e}")
        return None

import os
from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import requests

# Configuración inicial
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'una-clave-secreta-por-defecto')

# Configuración de archivos
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def call_inaturalist_api(image_path):
    """Función para llamar a la API de iNaturalist"""
    try:
        url = "https://api.inaturalist.org/v1/identifications"
        files = {'file': open(image_path, 'rb')}
        headers = {'Authorization': f'Bearer {os.getenv("INATURALIST_API_KEY")}'} if os.getenv("INATURALIST_API_KEY") else {}
        
        response = requests.post(url, files=files, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        if data['results']:
            best_match = data['results'][0]['taxon']
            return {
                'common_name': best_match.get('preferred_common_name', 'Desconocido'),
                'scientific_name': best_match.get('name', 'No identificado'),
                'confidence': round(best_match.get('score', 0) * 100, 2)
            }
    except Exception as e:
        print(f"API Error: {e}")
    return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verificar si se subió archivo
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo', 'error')
            return redirect(request.url)
            
        file = request.files['file']
        
        # Validar archivo
        if file.filename == '':
            flash('Archivo no válido', 'error')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_path)
            
            # Llamar a la API
            api_result = call_inaturalist_api(save_path)
            
            if api_result:
                return render_template('result.html', 
                                    name=api_result['common_name'],
                                    scientific_name=api_result['scientific_name'],
                                    confidence=api_result['confidence'])
            else:
                flash('Error al identificar la especie. Intenta con otra imagen.', 'error')
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'True') == 'True')
