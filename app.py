from flask import Flask, render_template, request, send_file, Response
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

    # Añadimos acceso visible a las guías desde la navegación principal.
    html = html.replace(
        '<a href="#ideas" class="hover:text-blue-600">Ideas de uso</a>',
        '<a href="#ideas" class="hover:text-blue-600">Ideas de uso</a>\n                <a href="#guias" class="hover:text-blue-600">Guías</a>'
    )

    html = html.replace(
        'Los mejores QRs 3D generados por nuestros usuarios',
        'Ejemplos de códigos QR 3D que puedes crear'
    )

    guias = '''
    <section id="guias" class="py-16 bg-white border-t border-gray-100">
        <div class="max-w-6xl mx-auto px-4">
            <div class="text-center max-w-3xl mx-auto mb-10">
                <h2 class="text-3xl font-bold mb-3">Guías para imprimir códigos QR en 3D</h2>
                <p class="text-gray-600">Consejos prácticos para elegir el formato, evitar errores de impresión y conseguir códigos que se escaneen correctamente.</p>
            </div>
            <div class="grid md:grid-cols-3 gap-6">
                <a href="/como-imprimir-qr-3d" class="block bg-gray-50 border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
                    <h3 class="font-bold text-xl mb-2 text-gray-900">Cómo imprimir un QR 3D correctamente</h3>
                    <p class="text-gray-600 text-sm">Tamaño, contraste, relieve, orientación y comprobaciones antes de fabricar varias unidades.</p>
                    <span class="inline-block mt-4 text-blue-600 font-semibold text-sm">Leer guía →</span>
                </a>
                <a href="/3mf-vs-stl" class="block bg-gray-50 border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
                    <h3 class="font-bold text-xl mb-2 text-gray-900">3MF vs STL</h3>
                    <p class="text-gray-600 text-sm">Qué guarda cada formato y cuál conviene para un QR de uno o varios colores.</p>
                    <span class="inline-block mt-4 text-blue-600 font-semibold text-sm">Leer guía →</span>
                </a>
                <a href="/errores-qr-3d" class="block bg-gray-50 border border-gray-200 rounded-xl p-6 hover:shadow-md transition">
                    <h3 class="font-bold text-xl mb-2 text-gray-900">Errores comunes al imprimir QR 3D</h3>
                    <p class="text-gray-600 text-sm">Los fallos que hacen que un código deje de escanearse y cómo corregirlos.</p>
                    <span class="inline-block mt-4 text-blue-600 font-semibold text-sm">Leer guía →</span>
                </a>
            </div>
        </div>
    </section>
'''
    html = html.replace('   <!-- SECCIÓN GALERÍA DE COMUNIDAD -->', guias + '\n   <!-- SECCIÓN GALERÍA DE COMUNIDAD -->')

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

@app.route('/como-imprimir-qr-3d')
def como_imprimir_qr_3d():
    return render_template('como-imprimir-qr-3d.html')

@app.route('/3mf-vs-stl')
def mf_vs_stl():
    return render_template('3mf-vs-stl.html')

@app.route('/errores-qr-3d')
def errores_qr_3d():
    return render_template('errores-qr-3d.html')

@app.route('/ads.txt')
def ads_txt():
    return Response(
        'google.com, pub-5212494517858064, DIRECT, f08c47fec0942fa0\n',
        mimetype='text/plain'
    )

@app.route('/robots.txt')
def robots_txt():
    base = request.host_url.rstrip('/')
    body = f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n"
    return Response(body, mimetype='text/plain')

@app.route('/sitemap.xml')
def sitemap_xml():
    base = request.host_url.rstrip('/')
    paths = [
        '/',
        '/como-imprimir-qr-3d',
        '/3mf-vs-stl',
        '/errores-qr-3d',
        '/privacidad',
        '/cookies',
        '/aviso-legal',
        '/contacto',
    ]
    urls = ''.join(f'<url><loc>{base}{path}</loc></url>' for path in paths)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return Response(xml, mimetype='application/xml')

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
