#!/usr/bin/env python3
"""
AWS Developer Practice Test - Servidor HTTP Local Mejorado
Version 3.0
Desarrollo por: Natxo Varona

Este servidor proporciona:
1. Servicio web local sin caché para desarrollo/testing
2. Endpoint de apagado controlado (/shutdown)
3. Endpoint de Informacion del sistema (/server-info)
4. Endpoint para monitoreo externo (/health-check)
5. Endpoint sistema de archivos en modo alternativo y bonito (/files)
6. Endpoint sistema de archivos en modo simple (/simple-files)
7. Manejo elegante de señales de terminación
8. Soporte para Chrome DevTools (.well-known)
9. Interfaz mejorada y listado de archivos bonito

Uso:
    python3 server.py

Características:
- Sirve archivos estáticos desde el directorio actual
- Headers anti-caché para desarrollo
- Puerto configurable (default: 8000)
- Limpieza adecuada al cerrar
- Interfaz moderna y responsive

Dependencias:
- Python 3.6+
- psutil (pip install psutil)
"""

from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs, unquote
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
import mimetypes

PORT = 8000
os_name = platform.system()
os_release = platform.release()
os_details = platform.platform()
start_time = time.time()

# Plantilla CSS moderna para todas las páginas
MODERN_CSS = """
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 2rem;
    color: #333;
  }
  
  .container {
    max-width: 900px;
    margin: 0 auto;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    animation: slideIn 0.6s ease-out;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
  }
  
  .header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    animation: float 6s ease-in-out infinite;
  }
  
  @keyframes float {
    0%, 100% { transform: translate(-50%, -50%) rotate(0deg); }
    50% { transform: translate(-50%, -50%) rotate(180deg); }
  }
  
  .header h1 {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 1;
  }
  
  .header p {
    font-size: 1.1rem;
    opacity: 0.9;
    position: relative;
    z-index: 1;
  }
  
  .content {
    padding: 2rem;
  }
  
  .nav-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  
  .nav-item {
    display: flex;
    align-items: center;
    padding: 1.5rem;
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    border-radius: 15px;
    text-decoration: none;
    color: #334155;
    transition: all 0.3s ease;
    border: 2px solid transparent;
    position: relative;
    overflow: hidden;
  }
  
  .nav-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent);
    transition: left 0.5s;
  }
  
  .nav-item:hover::before {
    left: 100%;
  }
  
  .nav-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
    border-color: #4f46e5;
  }
  
  .nav-item.primary {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
  }
  
  .nav-item.success {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
  }
  
  .nav-item.danger {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
  }
  
  .nav-item.info {
    background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%);
    color: white;
  }
  
  .nav-icon {
    font-size: 2rem;
    margin-right: 1rem;
    min-width: 3rem;
  }
  
  .nav-text {
    flex: 1;
  }
  
  .nav-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.25rem;
  }
  
  .nav-desc {
    font-size: 0.9rem;
    opacity: 0.8;
  }
  
  .footer {
    text-align: center;
    padding: 1.5rem;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
    color: #64748b;
    font-size: 0.9rem;
  }
  
  /* Estilos específicos para listado de archivos */
  .file-browser {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  }
  
  .file-header {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    padding: 1rem 1.5rem;
    font-weight: 600;
  }
  
  .file-table {
    width: 100%;
    border-collapse: collapse;
  }
  
  .file-table th {
    background: #f8fafc;
    padding: 1rem 1.5rem;
    text-align: left;
    font-weight: 600;
    color: #475569;
    border-bottom: 2px solid #e2e8f0;
  }
  
  .file-table td {
    padding: 1rem 1.5rem;
    border-bottom: 1px solid #f1f5f9;
    vertical-align: middle;
  }
  
  .file-table tr:hover {
    background: #f8fafc;
  }
  
  .file-link {
    display: flex;
    align-items: center;
    text-decoration: none;
    color: #334155;
    transition: color 0.2s ease;
  }
  
  .file-link:hover {
    color: #4f46e5;
  }
  
  .file-icon {
    font-size: 1.2rem;
    margin-right: 0.75rem;
    min-width: 1.5rem;
  }
  
  .file-name {
    font-weight: 500;
  }
  
  .file-size {
    text-align: right;
    color: #64748b;
    font-family: 'Monaco', 'Menlo', monospace;
    font-size: 0.9rem;
  }
  
  .file-date {
    text-align: right;
    color: #64748b;
    font-size: 0.9rem;
  }
  
  .breadcrumb {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0.75rem 1rem;
    background: #f8fafc;
    border-radius: 10px;
    font-size: 0.9rem;
    color: #64748b;
  }
  
  .breadcrumb a {
    color: #4f46e5;
    text-decoration: none;
    transition: color 0.2s ease;
  }
  
  .breadcrumb a:hover {
    color: #7c3aed;
  }
  
  /* Responsive */
  @media (max-width: 768px) {
    .nav-grid {
      grid-template-columns: 1fr;
    }
    
    .header h1 {
      font-size: 2rem;
    }
    
    .nav-item {
      padding: 1.25rem;
    }
    
    .file-table th,
    .file-table td {
      padding: 0.75rem 1rem;
    }
    
    .file-size,
    .file-date {
      display: none;
    }
  }
</style>
"""

HOME_TEMPLATE = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>AWS Developer Practice Test - Servidor Local</title>
  {MODERN_CSS}
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🚀 AWS Developer Practice Test</h1>
      <p>Servidor de desarrollo local v3.0</p>
    </div>
    
    <div class="content">
      <div class="nav-grid">
        <a href="/files" class="nav-item primary">
          <div class="nav-icon">📁</div>
          <div class="nav-text">
            <div class="nav-title">Explorador de Archivos</div>
            <div class="nav-desc">Navega por los archivos del proyecto</div>
          </div>
        </a>
        
        <a href="/server-info" class="nav-item info">
          <div class="nav-icon">🖥️</div>
          <div class="nav-text">
            <div class="nav-title">Información del Servidor</div>
            <div class="nav-desc">Detalles del sistema y recursos</div>
          </div>
        </a>
        
        <a href="/health-check" class="nav-item success">
          <div class="nav-icon">🩺</div>
          <div class="nav-text">
            <div class="nav-title">Health Check</div>
            <div class="nav-desc">Estado y métricas del servidor</div>
          </div>
        </a>
        
        <a href="/simple-files" class="nav-item">
          <div class="nav-icon">📋</div>
          <div class="nav-text">
            <div class="nav-title">Archivos Básicos</div>
            <div class="nav-desc">Vista simple de archivos</div>
          </div>
        </a>
        
        <a href="/shutdown" class="nav-item danger" onclick="return confirm('¿Estás seguro de que quieres cerrar el servidor?')">
          <div class="nav-icon">🛑</div>
          <div class="nav-text">
            <div class="nav-title">Cerrar Servidor</div>
            <div class="nav-desc">Apagar el servidor de forma segura</div>
          </div>
        </a>
      </div>
    </div>
    
    <div class="footer">
      <p>Servidor HTTP Local para desarrollo • Puerto {PORT} • {os_name} {os_release}</p>
    </div>
  </div>
</body>
</html>
""".strip()

SERVER_INFO_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Información del Servidor - AWS Developer Practice Test</title>
  {MODERN_CSS}
  <style>
    .info-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }}
    
    .info-card {{
      background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
      border-radius: 15px;
      padding: 1.5rem;
      border-left: 4px solid #4f46e5;
    }}
    
    .info-label {{
      font-weight: 600;
      color: #475569;
      margin-bottom: 0.5rem;
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    
    .info-value {{
      font-size: 1.1rem;
      color: #1e293b;
      word-break: break-all;
    }}
    
    .back-link {{
      display: inline-flex;
      align-items: center;
      margin-bottom: 2rem;
      padding: 0.75rem 1.5rem;
      background: #4f46e5;
      color: white;
      text-decoration: none;
      border-radius: 10px;
      transition: all 0.3s ease;
    }}
    
    .back-link:hover {{
      background: #7c3aed;
      transform: translateY(-2px);
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>{icon} Información del Servidor</h1>
      <p>Detalles del sistema y recursos en tiempo real</p>
    </div>
    
    <div class="content">
      <a href="/" class="back-link">← Volver al inicio</a>
      
      <div class="info-grid">
        <div class="info-card">
          <div class="info-label">Sistema Operativo</div>
          <div class="info-value">{sistema_operativo}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Versión del SO</div>
          <div class="info-value">{version}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Nombre del Host</div>
          <div class="info-value">{nombre_maquina}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Puerto</div>
          <div class="info-value">{puerto}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Directorio Raíz</div>
          <div class="info-value">{directorio_raiz}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Hora Actual (UTC)</div>
          <div class="info-value">{hora_actual}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Memoria Total</div>
          <div class="info-value">{mem_total}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">Memoria Usada</div>
          <div class="info-value">{mem_usada}</div>
        </div>
        
        <div class="info-card">
          <div class="info-label">CPU Usada</div>
          <div class="info-value">{cpu_usado}</div>
        </div>
      </div>
    </div>
    
    <div class="footer">
      <p>Actualizado automáticamente • AWS Developer Practice Test v3.0</p>
    </div>
  </div>
</body>
</html>
""".strip()

FILE_ICONS = {
    'folder': '📁',
    'parent': '↩️',
    'pdf': '📄',
    'image': '🖼️',
    'code': '💻',
    'text': '📝',
    'json': '📋',
    'zip': '📦',
    'audio': '🎵',
    'video': '🎬',
    'default': '📄'
}

def get_file_icon(filename, is_dir=False):
    """Obtiene el icono apropiado para un archivo o directorio"""
    if filename == '..':
        return FILE_ICONS['parent']
    elif is_dir:
        return FILE_ICONS['folder']
    
    _, ext = os.path.splitext(filename.lower())
    
    icon_map = {
        '.pdf': 'pdf',
        '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image', '.bmp': 'image', '.svg': 'image',
        '.py': 'code', '.js': 'code', '.html': 'code', '.css': 'code', '.cpp': 'code', '.c': 'code', '.java': 'code',
        '.txt': 'text', '.md': 'text', '.rst': 'text',
        '.json': 'json', '.xml': 'json', '.yaml': 'json', '.yml': 'json',
        '.zip': 'zip', '.rar': 'zip', '.tar': 'zip', '.gz': 'zip',
        '.mp3': 'audio', '.wav': 'audio', '.flac': 'audio',
        '.mp4': 'video', '.avi': 'video', '.mkv': 'video', '.mov': 'video'
    }
    
    return FILE_ICONS.get(icon_map.get(ext, 'default'), FILE_ICONS['default'])

def get_simple_icon(filename):
    if os.path.isdir(filename):
        return '📁'
    ext = os.path.splitext(filename)[1].lower()
    if ext in ['.html', '.htm']: return '🌐'
    if ext in ['.py']: return '🐍'
    return '📄'

def format_size(size):
    """Formatea el tamaño de archivo de manera legible"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"

def generate_breadcrumb(path):
    """Genera breadcrumb para navegación"""
    parts = path.strip('/').split('/')
    if not parts or parts == ['']:
        return '<span>📁 Raíz</span>'
    
    breadcrumb = ['<a href="/files">📁 Raíz</a>']
    current_path = ''
    
    for part in parts:
        if part:
            current_path += '/' + part
            breadcrumb.append(f'<a href="/files{current_path}">📁 {part}</a>')
    
    return ' / '.join(breadcrumb)

def generate_file_listing_html(directory_path, url_path=''):
    """Genera el HTML para el listado de archivos mejorado"""
    try:
        items = []
        
        # Agregar enlace para subir de directorio si no estamos en la raíz
        if url_path:
            parent_path = '/'.join(url_path.rstrip('/').split('/')[:-1])
            items.append({
                'name': '..',
                'is_dir': True,
                'url': f'/files{parent_path}' if parent_path else '/files',
                'size': '-',
                'date': '-',
                'icon': get_file_icon('..', True)
            })
        
        # Listar archivos y directorios
        try:
            entries = sorted(os.listdir(directory_path))
        except PermissionError:
            return f"""
            <div class="container">
                <div class="header">
                    <h1>❌ Error de Acceso</h1>
                    <p>No se puede acceder al directorio</p>
                </div>
                <div class="content">
                    <a href="/files" class="back-link">← Volver</a>
                    <p>No tienes permisos para acceder a este directorio.</p>
                </div>
            </div>
            """
        
        for entry in entries:
            if entry.startswith('.'):  # Ocultar archivos ocultos
                continue
                
            full_path = os.path.join(directory_path, entry)
            is_dir = os.path.isdir(full_path)
            
            try:
                stat = os.stat(full_path)
                size = format_size(stat.st_size) if not is_dir else '-'
                date = datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y, %H:%M')
            except (OSError, ValueError):
                size = '-'
                date = '-'
            
            url = f'/files{url_path}/{entry}' if url_path else f'/files/{entry}'
            if is_dir:
                url += '/'
            
            items.append({
                'name': entry,
                'is_dir': is_dir,
                'url': url,
                'size': size,
                'date': date,
                'icon': get_file_icon(entry, is_dir)
            })
        
        # Generar filas de la tabla
        table_rows = []
        for item in items:
            display_name = item['name'] + ('/' if item['is_dir'] and item['name'] != '..' else '')
            table_rows.append(f"""
                <tr>
                    <td>
                        <a href="{item['url']}" class="file-link">
                            <span class="file-icon">{item['icon']}</span>
                            <span class="file-name">{display_name}</span>
                        </a>
                    </td>
                    <td class="file-size">{item['size']}</td>
                    <td class="file-date">{item['date']}</td>
                </tr>
            """)
        
        breadcrumb = generate_breadcrumb(url_path)
        current_dir = os.path.basename(directory_path) or 'Raíz'
        
        return f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Explorador de Archivos - {current_dir}</title>
            {MODERN_CSS}
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📁 Explorador de Archivos</h1>
                    <p>Navegando por: {current_dir}</p>
                </div>
                
                <div class="content">
                    <a href="/" class="back-link">← Volver al inicio</a>
                    
                    <div class="breadcrumb">
                        {breadcrumb}
                    </div>
                    
                    <div class="file-browser">
                        <div class="file-header">
                            📂 Contenido del directorio ({len(items)} elementos)
                        </div>
                        <table class="file-table">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Tamaño</th>
                                    <th>Fecha</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(table_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Explorador de archivos • AWS Developer Practice Test v3.0</p>
                </div>
            </div>
        </body>
        </html>
        """
        
    except Exception as e:
        return f"""
        <div class="container">
            <div class="header">
                <h1>❌ Error</h1>
                <p>No se pudo generar el listado</p>
            </div>
            <div class="content">
                <a href="/files" class="back-link">← Volver</a>
                <p>Error: {str(e)}</p>
            </div>
        </div>
        """

class NoCacheHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Handler HTTP mejorado con interfaz moderna"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

    def is_html_request(self):
        """Determina si la solicitud espera HTML"""
        accept = self.headers.get('Accept', '')
        return 'text/html' in accept or '*/*' in accept

    def get_os_icon(self, os_name):
        """Devuelve un icono SVG según el sistema operativo"""
        icons = {
            "Windows": "🪟",
            "Linux": "🐧", 
            "Darwin": "🍎"
        }
        return icons.get(os_name, "🖥️")
            
    def end_headers(self):
        """Añade headers anti-caché a todas las respuestas"""
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()
    
    def do_GET(self):
        """Maneja solicitudes GET con interfaz mejorada"""
        # Ignorar solicitudes de Chrome DevTools
        if self.path.startswith('/.well-known/'):
            self.send_response(204)
            self.end_headers()
            return

        # Página de inicio mejorada
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

        # Health check endpoint
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
            self.wfile.write(json.dumps(health_data, indent=2).encode('utf-8'))
            return

        # Server info endpoint mejorado
        if self.path.startswith('/server-info'):
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            os_name_param = query_params.get('os', [platform.system()])[0]

            mem = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            data = {
                "sistema_operativo": os_name_param,
                "version": os_release,
                "nombre_maquina": platform.node(),
                "puerto": PORT,
                "directorio_raiz": os.getcwd(),
                "hora_actual": datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC'),
                "mem_total": f"{mem.total // (1024 * 1024)} MB",
                "mem_usada": f"{mem.used // (1024 * 1024)} MB ({mem.percent:.1f}%)",
                "cpu_usado": f"{cpu_percent:.1f}%",
                "icon": self.get_os_icon(os_name_param),
                "MODERN_CSS": MODERN_CSS
            }

            if self.is_html_request():
                html_content = SERVER_INFO_TEMPLATE.format(**data)
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_content.encode('utf-8'))
            else:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
            return
            
        # Explorador de archivos mejorado
        if self.path.startswith('/files'):
            # Extraer la ruta del archivo/directorio
            url_path = self.path[6:]  # Remover '/files'
            if url_path.startswith('/'):
                url_path = url_path[1:]
            
            # Decodificar URL
            url_path = unquote(url_path)
            
            # Construir ruta física
            if url_path:
                physical_path = os.path.join(self.directory, url_path)
            else:
                physical_path = self.directory
            
            # Verificar que la ruta esté dentro del directorio permitido
            try:
                physical_path = os.path.realpath(physical_path)
                if not physical_path.startswith(os.path.realpath(self.directory)):
                    self.send_error(403, "Forbidden")
                    return
            except:
                self.send_error(404, "Not Found")
                return
            
            # Si es un directorio, mostrar listado
            if os.path.isdir(physical_path):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                html_content = generate_file_listing_html(physical_path, '/' + url_path if url_path else '')
                self.wfile.write(html_content.encode('utf-8'))
                return
            
            # Si es un archivo, servirlo
            elif os.path.isfile(physical_path):
                # Determinar tipo MIME
                mime_type, _ = mimetypes.guess_type(physical_path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                
                try:
                    with open(physical_path, 'rb') as f:
                        self.send_response(200)
                        self.send_header("Content-type", mime_type)
                        self.send_header("Content-Length", str(os.path.getsize(physical_path)))
                        self.end_headers()
                        self.wfile.write(f.read())
                    return
                except:
                    self.send_error(500, "Internal Server Error")
                    return
            else:
                self.send_error(404, "Not Found")
                return
        
        # Vista simple de archivos (comportamiento por defecto de SimpleHTTPRequestHandler)
        if self.path == '/simple-files':
          self.send_response(200)
          self.send_header("Content-type", "text/html; charset=utf-8")
          self.end_headers()
          
          # Generar listado simple
          files = "\n".join([
              f'<li>{get_simple_icon(f)} <a href="{f}">{f}</a></li>' 
              for f in os.listdir('.') 
              if not f.startswith('.')
          ])
          
          simple_html = f"""
          <!DOCTYPE html>
          <html>
          <head>
              <title>Vista Simple de Archivos</title>
              <style>
                  body {{ font-family: Arial, sans-serif; padding: 20px; }}
                  ul {{ list-style: none; padding: 0; }}
                  li {{ padding: 5px 0; }}
                  a {{ color: #4f46e5; text-decoration: none; }}
                  a:hover {{ text-decoration: underline; }}
              </style>
          </head>
          <body>
              <h1>Archivos en {os.getcwd()}</h1>
              <p><a href="/">← Volver al inicio</a> | <a href="/files">Vista Avanzada</a></p>
              <ul>{files}</ul>
          </body>
          </html>
          """
          
          self.wfile.write(simple_html.encode('utf-8'))
          return    
        
        # Para todas las demás rutas, usar el comportamiento por defecto
        SimpleHTTPRequestHandler.do_GET(self)

class MyTCPServer(socketserver.TCPServer):
    """Servidor TCP con reutilización de dirección"""
    allow_reuse_address = True
    daemon_threads = True

def signal_handler(sig, frame):
    """Maneja señales de terminación (CTRL+C)"""
    print(f"\nSeñal {sig} recibida. Iniciando apagado...")
    shutdown_thread = threading.Thread(target=httpd.shutdown, daemon=True)
    shutdown_thread.start()
    shutdown_thread.join(timeout=2.0)

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
                                                            
   🚀 Servidor AWS Developer Practice Test (v3.0 Mejorado)                    
   ========================================================                      
   • Puerto: {PORT}                                         
   • Directorio: {os.getcwd()}  
   • Sistema: {os_name} ({os_release})                           
   • Características: No-Cache, Interfaz Moderna, Navegador de Archivos                                   
                                                            
   🌐 Accede: http://localhost:{PORT}                          
   🛑 Detener: CTRL+C o visitar http://localhost:{PORT}/shutdown                     
   📁 Archivos: http://localhost:{PORT}/files
   📁 Arch.Simple: http://localhost:{PORT}/simple-files
   🖥️ Info: http://localhost:{PORT}/server-info
   🩺 Health: http://localhost:{PORT}/health-check
    """)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()
        print("✅ Servidor detenido correctamente")