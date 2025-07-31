from flask import Flask, render_template, request
from tensorflow.keras.models import load_model
from PIL import Image
import numpy as np

app = Flask(__name__)
model = load_model('model/rapaces.h5')  # Asegúrate de subir tu modelo luego

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            img = Image.open(file).resize((150, 150))
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            prediction = model.predict(img_array)
            predicted_class = np.argmax(prediction)
            confidence = round(100 * np.max(prediction), 2)
            
            return render_template('result.html', 
                                species="Águila imperial",  # Ejemplo (cambiar luego)
                                confidence=confidence)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
