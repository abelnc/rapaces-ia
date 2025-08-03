import { useState } from 'react';

export default function ImageUploader({ onImageSelect }) {
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    
    if (!file) return;
    
    // Validar que es una imagen
    if (!file.type.match('image.*')) {
      setError('Por favor, selecciona un archivo de imagen válido');
      return;
    }
    
    // Validar tamaño (ejemplo: máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('La imagen es demasiado grande (máximo 5MB)');
      return;
    }
    
    setError(null);
    
    // Crear vista previa
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
      if (onImageSelect) {
        onImageSelect(reader.result);
      }
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="uploader-container">
      <input
        type="file"
        id="image-upload"
        accept="image/*"
        onChange={handleImageChange}
        style={{ display: 'none' }}
      />
      
      <label htmlFor="image-upload" className="upload-button">
        Seleccionar de Galería
      </label>
      
      {error && <div className="error-message">{error}</div>}
      
      {preview && (
        <div className="image-preview">
          <img src={preview} alt="Vista previa" />
        </div>
      )}
    </div>
  );
}
