from flask import Flask, render_template, request, send_file
import qrcode
import trimesh
import numpy as np
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    html = render_template('index.html')

    # Durante la preparación para AdSense quitamos los bloques de anuncio de demostración.
    html = html.replace('''    <!-- Ad: Notificación en esquina -->
    <div class="fixed bottom-4 right-4 w-64 h-24 ad-placeholder z-50 shadow-lg text-sm rounded">
        ANUNCIO (NOTIFICACIÓN)
    </div>
''', '')

    html = html.replace('''    <!-- Ad: Banner Horizontal -->
    <div class="max-w-6xl mx-auto px-4 my-8">
        <div class="w-full h-24 ad-placeholder rounded-lg">
            ANUNCIO (BANNER HORIZONTAL)
        </div>
    </div>
''', '')

    html = html.replace('''    <!-- Ad: Banner Mitad de Contenido -->
    <div class="max-w-4xl mx-auto px-4 my-8">
        <div class="w-full h-40 ad-placeholder rounded-lg">
            ANUNCIO (BANNER MITAD CONTENIDO)
        </div>
    </div>
''', '')

    html = html.replace(
        'Los mejores QRs 3D generados por nuestros usuarios',
        'Ejemplos de códigos QR 3D que puedes crear'
    )

    html = html.replace('''    <footer class="bg-gray-900 text-gray-400 py-8 text-center">
        <p>&copy; 2026 PrintQR3D. Todos los derechos reservados.</p>
    </footer>''', '''    <footer class="bg-gray-900 text-gray-300 py-8">
        <div class="max-w-6xl mx-auto px-4 text-center space-y-3">
            <p>&copy; 2026 PrintQR3D. Todos los derechos reservados.</p>
            <nav class="flex flex-wrap justify-center gap-x-5 gap-y-2 text-sm">
                <a href="/privacidad" class="hover:text-white">Privacidad</a>
                <a href="/cookies" class="hover:text-white">Cookies</a>
                <a href="/aviso-legal" class="hover:text-white">Aviso legal</a>
                <a href="/contacto" class="hover:text-white">Contacto</a>
            </nav>
        </div>
    </footer>''')

    html = html.replace('''            <div class="w-full h-48 ad-placeholder mb-4 rounded">
                ANUNCIO (POP-UP DESCARGA)
            </div>''', '''            <div class="w-full bg-blue-50 border border-blue-100 p-4 mb-4 rounded text-sm text-center text-gray-700">
                Gracias por utilizar PrintQR3D. Comprueba siempre que el código se escanea correctamente antes de imprimirlo.
            </div>''')

    return html

@app.route('/privacidad')
def privacidad():
    return render_template('privacidad.html')

@app.route('/cookies')
def cookies():
    return render_template('cookies.html')

@app.route('/aviso-legal')
def aviso_legal():
    return render_template('aviso-legal.html')

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

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

    if ext == 'png':
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(output_path)
        return send_file(output_path, as_attachment=True)

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
