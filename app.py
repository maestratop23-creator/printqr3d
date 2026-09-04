from flask import Flask, render_template, request, send_file
import qrcode
import trimesh
import numpy as np
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/preview-qr', methods=['POST'])
def preview_qr():
    data = request.json
    url = data.get('url', 'https://google.com')
    
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    temp_dir = tempfile.gettempdir()
    path = os.path.join(temp_dir, 'qr_preview.png')
    img.save(path)
    return send_file(path, mimetype='image/png')

@app.route('/api/generate', methods=['POST'])
def generate_model():
    data = request.json
    url = data.get('url', 'https://google.com')
    shape = data.get('shape', 'plaque')
    format_type = data.get('format', '3MF')
    
    temp_dir = tempfile.gettempdir()
    ext = format_type.lower()
    output_path = os.path.join(temp_dir, f'codigo-qr.{ext}')
    
    # CAMINO 1: Si el usuario pide un PNG, generamos el QR 2D tradicional
    if ext == 'png':
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        return send_file(output_path, as_attachment=True)
        
    # CAMINO 2: Si pide 3MF o STL, construimos el modelo 3D con trimesh
    qr = qrcode.QRCode(version=1, box_size=1, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    matriz = qr.modules
    tamaño_qr = len(matriz)
    
    grosor_base = 2.0
    altura_relieve = 0.6
    
    base = trimesh.creation.box(extents=[tamaño_qr, tamaño_qr, grosor_base])
    base.apply_translation([tamaño_qr/2, tamaño_qr/2, -grosor_base/2])
    
    cubos_qr = []
    for y, fila in enumerate(matriz):
        for x, valor in enumerate(fila):
            if valor:
                cubo = trimesh.creation.box(extents=[1, 1, altura_relieve])
                cubo.apply_translation([x + 0.5, (tamaño_qr - y - 1) + 0.5, altura_relieve/2])
                cubos_qr.append(cubo)
                
    malla_qr = trimesh.util.concatenate(cubos_qr)
    escena = trimesh.Scene([base, malla_qr])
    
    escena.export(output_path)
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
