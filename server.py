#!/usr/bin/env python3
"""
AWS Developer Practice Test - Servidor HTTP Local

Este servidor proporciona:
1. Servicio web local sin caché para desarrollo/testing
2. Endpoint de apagado controlado (/shutdown)
3. Endpoint de Informacion del sistema (/server-info)
4. Endpoint para monitoreo externo (/health-check)
3. Manejo elegante de señales de terminación
4. Soporte para Chrome DevTools (.well-known)

Uso:
    python3 server.py

Características:
- Sirve archivos estáticos desde el directorio actual
- Headers anti-caché para desarrollo
- Puerto configurable (default: 8000)
- Limpieza adecuada al cerrar

Dependencias:
- Python 3.6+
- No se requieren paquetes externos
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import socketserver
import signal
import sys
import threading
import os
import platform
import json
import psutil
from datetime import datetime, timezone
import time

PORT = 8000
os_name = platform.system()      # Devuelve 'Linux', 'Darwin' (macOS), 'Windows', etc.
os_release = platform.release()  # Versión del SO (opcional)
os_details = platform.platform()
start_time = time.time()

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Inicio - Servidor Local</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      background-color: #f5f5f7;
      color: #333;
      margin: 0;
      padding: 2rem;
    }}
    .container {{
      max-width: 600px;
      margin: auto;
      background: white;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 2rem;
      text-align: center;
    }}
    h1 {{
      font-size: 2rem;
      margin-bottom: 1rem;
    }}
    nav {{
      display: flex;
      flex-direction: column;
      gap: 1rem;
      margin-top: 2rem;
    }}
    nav a {{
      display: block;
      padding: 1rem 1.5rem;
      background-color: #007AFF;
      color: white;
      text-decoration: none;
      border-radius: 6px;
      transition: background-color 0.2s ease;
    }}
    nav a:hover {{
      background-color: #005ECF;
    }}
    footer {{
      margin-top: 3rem;
      font-size: 0.9rem;
      color: #888;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>Bienvenido al Servidor Local</h1>
    <nav>
      <a href="/">📁 Archivos</a>
      <a href="/./" style="background-color: #34C759;">📂 Ver Archivos Bonitos</a>
      <a href="/server-info">🖥️ Información del Servidor</a>
      <a href="/health-check">🩺 Health Check</a>
      <a href="/shutdown" style="background-color: #FF3B30;">🛑 Cerrar Servidor</a>
    </nav>
    <br>
    <footer>
      AWS Developer Practice Test v3.0
    </footer>
  </div>
</body>
</html>
""".strip()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Información del Servidor</title>
  <style>
    body {{
      font-family: system-ui, sans-serif;
      background-color: #f5f5f7;
      color: #333;
      margin: 0;
      padding: 2rem;
    }}
    .container {{
      max-width: 800px;
      margin: auto;
      background: white;
      border-radius: 10px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      padding: 2rem;
    }}
    h1 {{
      text-align: center;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 1rem;
      color: #2c3e50;
    }}
    .icon {{
      width: 32px;
      height: 32px;
    }}
    .info {{
      margin-top: 2rem;
    }}
    .info dt {{
      font-weight: bold;
      margin-top: 1rem;
    }}
    .info dd {{
      margin-left: 1rem;
      word-break: break-word;
    }}
    footer {{
      margin-top: 3rem;
      font-size: 0.9rem;
      text-align: center;
      color: #888;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>{icon}<span>Información del Servidor</span></h1>
    <dl class="info">
      <dt>Sistema Operativo</dt><dd>{sistema_operativo}</dd>
      <dt>Versión del SO</dt><dd>{version}</dd>
      <dt>Nombre del Host</dt><dd>{nombre_maquina}</dd>
      <dt>Puerto</dt><dd>{puerto}</dd>
      <dt>Directorio Raíz</dt><dd>{directorio_raiz}</dd>
      <dt>Hora Actual (UTC)</dt><dd>{hora_actual}</dd>
      <dt>Memoria Total</dt><dd>{mem_total}</dd>
      <dt>Memoria Usada</dt><dd>{mem_usada}</dd>
      <dt>CPU Usada</dt><dd>{cpu_usado}</dd>
    </dl>
    <footer>
      Servidor HTTP Local - AWS Developer Practice Test v3.0
    </footer>
  </div>
</body>
</html>
""".strip()

FILE_ICONS = {
    'folder': '📁',
    'pdf': '📄',
    'image': '📷',
    'code': '💻',
    'text': '📝',
    'default': '📦'
}

def get_file_icon(filename):
    if filename == '..':
        return '↩️'
    elif os.path.isdir(filename):
        return FILE_ICONS['folder']
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    if ext in ('.pdf',):
        return FILE_ICONS['pdf']
    elif ext in ('.jpg', '.jpeg', '.png', '.gif'):
        return FILE_ICONS['image']
    elif ext in ('.py', '.js', '.html', '.css', '.json'):
        return FILE_ICONS['code']
    elif ext in ('.txt', '.md'):
        return FILE_ICONS['text']
    else:
        return FILE_ICONS['default']

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def generate_dir_html(path):
    files = ['..'] + sorted(os.listdir(path))  # Añadimos ".." para retroceder
    rows = []
    for file in files:
        full_path = os.path.join(path, file)
        is_dir = os.path.isdir(full_path)
        icon = get_file_icon(file)
        modified_time = os.path.getmtime(full_path)
        date_str = datetime.fromtimestamp(modified_time).strftime('%d-%b-%Y')
        if is_dir:
            link = f'<a href="{file}/">{icon} {file}/</a>'
            size_str = "-"
        else:
            size_str = format_size(os.path.getsize(full_path))
            link = f'<a href="{file}">{icon} {file}</a>'
        rows.append(f"<tr><td>{link}</td><td>{size_str}</td><td>{date_str}</td></tr>")

    table = """
        <table style="width:100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th style="text-align:left">Nombre</th>
              <th style="text-align:right">Tamaño</th>
              <th style="text-align:right">Fecha</th>
            </tr>
          </thead>
          <tbody>
        {rows}
          </tbody>
        </table>
            """.replace("{rows}", "\n".join(rows))

    return f"""
<h2>Archivos en "{os.path.basename(path)}"</h2>
{table}
"""

class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Handler HTTP que deshabilita el caché y maneja rutas especiales"""
    
    def __init__(self, *args, **kwargs):
        # Configurar el directorio base como el directorio actual
        self.directory = os.getcwd()
        super().__init__(*args, **kwargs)

    def is_html_request(self):
        accept = self.headers.get('Accept', '')
        return 'text/html' in accept or '*/*' in accept

    def get_os_icon(self, os_name):
        """Devuelve un SVG inline según el sistema operativo"""
        if os_name == "Windows":
            return '''
            <svg class="icon" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
              <path d="M21 2H7C5.9 2 5 2.9 5 4V20C5 21.1 5.9 22 7 22H21C22.1 22 23 21.1 23 20V4C23 2.9 22.1 2 21 2ZM21 20H7V14H21V20ZM21 12H7V4H21V12Z" />
            </svg>
            '''
        elif os_name == "Linux":
            return '''
            <svg class="icon" viewBox="0 0 24 24" fill="#FCC627" xmlns="http://www.w3.org/2000/svg">
              <circle cx="12" cy="12" r="8" />
            </svg>
            '''
        elif os_name == "Darwin":
            return '''
            <svg class="icon" viewBox="0 0 24 24" fill="#A2A2A2" xmlns="http://www.w3.org/2000/svg">
              <path d="M17.5 9.2c0 .8-.3 1.5-.8 2-.6.5-1.5.8-2.5.8-.2 0-.5 0-.7-.1.1.6.3 1.1.6 1.6.4.6.9 1.1 1.6 1.5.6.4 1.2.6 1.9.6.5 0 1-.1 1.5-.3.5-.2.9-.5 1.2-.9.3-.4.5-.9.5-1.5 0-.7-.4-1.3-1.2-1.8-.8-.5-1.1-1-1.1-1.6 0-.4.1-.7.4-1 .3-.3.7-.4 1.2-.4.4 0 .8.1 1.2.2.4.1.7.3 1 .6.3.3.5.6.6 1 .1.4.2.8.2 1.3Zm-2.6-3c-.6 0-1.1.2-1.5.5-.4.3-.6.8-.6 1.4 0 .6.2 1.1.6 1.4.4.3.9.5 1.5.5.6 0 1.1-.2 1.5-.5.4-.3.6-.8.6-1.4 0-.6-.2-1.1-.6-1.4-.4-.3-.9-.5-1.5-.5Z"/>
            </svg>
            '''
        else:
            return '''
            <svg class="icon" viewBox="0 0 24 24" fill="gray" xmlns="http://www.w3.org/2000/svg">
              <rect width="24" height="24" rx="4"/>
            </svg>
            '''

    def list_directory(self, path):
        try:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = generate_dir_html(path)
            full_html = f"""
                <!DOCTYPE html>
                <html>
                <head><title>Archivos</title></head>
                <body style="font-family:sans-serif; padding:2rem;">
                  <h1>📁 Listado de archivos</h1>
                  {html}
                </body>
                </html>
                """
            self.wfile.write(full_html.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Error generando listado: {e}")
            
    def end_headers(self):
        """Añade headers anti-caché a todas las respuestas"""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    
    def do_GET(self):
        """Maneja solicitudes GET, incluyendo rutas especiales"""
        # Ignorar solicitudes de Chrome DevTools
        if self.path.startswith('/.well-known/'):
            self.send_response(204)
            self.end_headers()
            return

        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HOME_TEMPLATE.encode('utf-8'))
            return
            
        # Endpoint de apagado controlado
        if self.path == '/shutdown':
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Shutting down server...")
            print("\nSolicitud de apagado recibida. Cerrando servidor...")
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return

        # Endpoint de Estado del servidor, ideal para monitorear
        if self.path == '/health-check':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            mem = psutil.virtual_memory()

            cpu_percent = psutil.cpu_percent(interval=0.1)
            health_data = {
                "status": "ok",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "os": platform.system(),
                "port": PORT,
                "up_time_seconds": int(time.time() - start_time),
                "memory_used_mb": mem.used // (1024 * 1024),
                "cpu_percent": cpu_percent
            }

            self.wfile.write(json.dumps(health_data).encode('utf-8'))
            return

        # Nuevo endpoint para info del servidor
        if self.path.startswith('/server-info'):
            # Parseamos la URL
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
    
            # Obtenemos el SO simulado si existe
            os_name = query_params.get('os', [platform.system()])[0]

            mem = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            data = {
                "sistema_operativo": os_name,
                "version": os_release,
                "nombre_maquina": platform.node(),
                "puerto": PORT,
                "directorio_raiz": os.getcwd(),
                "hora_actual": datetime.now(timezone.utc).isoformat() + " UTC",
                "mem_total": f"{mem.total // (1024 * 1024)} MB",
                "mem_usada": f"{mem.used // (1024 * 1024)} MB ({mem.percent}%)",
                "cpu_usado": f"{cpu_percent}%",
                "icon": self.get_os_icon(os_name)
            }

            if self.is_html_request():
                # Enviar respuesta HTML bonita
                html_content = HTML_TEMPLATE.format(**data)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                # Enviar respuesta JSON
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
            return
            
        # Si es una solicitud de archivo o directorio
        SimpleHTTPRequestHandler.do_GET(self)

class MyTCPServer(socketserver.TCPServer):
    """Servidor TCP con reutilización de dirección"""
    allow_reuse_address = True
    daemon_threads = True  # Permite cerrar incluso con hilos activos

def signal_handler(sig, frame):
    """Maneja señales de terminación (CTRL+C)"""
    print(f"\nSeñal {sig} recibida. Iniciando apagado...")
    shutdown_thread = threading.Thread(target=httpd.shutdown, daemon=True)
    shutdown_thread.start()
    shutdown_thread.join(timeout=2.0)  # Esperar máximo 2 segundos

if __name__ == "__main__":
    # Configurar servidor
    httpd = MyTCPServer(("", PORT), NoCacheHTTPRequestHandler)
    
    # Registrar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print(f"""\n
    █████╗ ██╗    ██╗███████╗     ██████╗ ███████╗██╗   ██╗
   ██╔══██╗██║    ██║██╔════╝    ██╔════╝ ██╔════╝██║   ██║
   ███████║██║ █╗ ██║███████╗    ██║  ███╗█████╗  ██║   ██║
   ██╔══██║██║███╗██║╚════██║    ██║   ██║██╔══╝  ╚██╗ ██╔╝
   ██║  ██║╚███╔███╔╝███████║    ╚██████╔╝███████╗ ╚████╔╝ 
   ╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝     ╚═════╝ ╚══════╝  ╚═══╝  
                                                            
   Servidor AWS Developer Practice Test (v3.0)                      
   ===========================================                      
   • Puerto: {PORT}                                         
   • Directorio: {os.getcwd()}  
   • Sistema Operativo: {os_name} ({os_release}) - {os_details}                           
   • No-Cache: Activado                                     
                                                            
   Accede: http://localhost:{PORT}                          
   Detener: CTRL+C o visitar http://localhost:{PORT}/shutdown                     
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("✅ Servidor detenido correctamente")