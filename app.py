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
            
            # Llamar a la API CORRECTA de iNaturalist
            try:
                api_url = "https://api.inaturalist.org/v1/identifications"
                headers = {'User-Agent': 'RapacesIA/1.0 (contacto@tudominio.com)'}
                
                # Debes usar el endpoint correcto para identificación de imágenes
                response = requests.post(
                    "https://api.inaturalist.org/v1/computervision/identify",
                    files={'file': open(save_path, 'rb')},
                    headers=headers
                )
                
                if response.status_code != 200:
                    flash('Error al conectar con el servicio de identificación', 'error')
                    return redirect(request.url)
                
                data = response.json()
                
                if data.get('results'):
                    best_result = data['results'][0]
                    return render_template('result.html',
                        name=best_result.get('common_name', 'Desconocido'),
                        confidence=f"{best_result.get('score', 0)*100:.1f}%"
                    )
                else:
                    flash('No se pudo identificar el ave en la imagen', 'error')
                    return redirect(request.url)
                    
            except Exception as e:
                print(f"Error con la API: {str(e)}")
                flash('Error al procesar la imagen. Intenta nuevamente.', 'error')
                return redirect(request.url)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=os.getenv('DEBUG', 'True') == 'True')