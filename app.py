from flask import Flask, render_template, request, flash
import requests
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def identify_species(image_path):
    """Envía la imagen a iNaturalist y devuelve el resultado."""
    try:
        url = "https://api.inaturalist.org/v1/identifications"
        files = {'file': open(image_path, 'rb')}
        response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            # Extrae la especie más probable (ejemplo simplificado)
            top_result = data['results'][0]['taxon']
            return {
                'name': top_result['preferred_common_name'],
                'scientific_name': top_result['name'],
                'confidence': top_result['score'] * 100  # Convertir a porcentaje
            }
        else:
            return None
    except Exception as e:
        print("Error calling iNaturalist API:", e)
        return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se seleccionó ningún archivo')
            return render_template('index.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('Archivo no válido')
            return render_template('index.html')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            temp_path = os.path.join('static', 'uploads', filename)
            file.save(temp_path)
            
            result = identify_species(temp_path)
            if result:
                return render_template('result.html', 
                                    name=result['name'],
                                    scientific_name=result['scientific_name'],
                                    confidence=result['confidence'])
            else:
                flash('Error al identificar la especie')
    
    return render_template('index.html')

if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    app.run(debug=True)
