
# 📚 AWS Developer Practice Test

![AWS Developer Practice Test](https://img.shields.io/badge/AWS-Developer-blue) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)

Este proyecto consta de dos **aplicaciónes web interactivas** diseñadas para ayudarte a practicar preguntas del examen **AWS Certified Developer y DevOps**. La aplicación te permite realizar pruebas con preguntas aleatorias, ver tus respuestas falladas y recibir explicaciones detalladas para mejorar tu aprendizaje. La segunda aplicacion web consite en poder gestionar tu base de datos de preguntas.

---

## 🛠 Características principales de AWS Developer Practice Test

✔️ **Preguntas aleatorias**: Cada test selecciona 10 preguntas al azar de una base de datos amplia.  
✔️ **Explicaciones detalladas**: Cada pregunta incluye una explicación para ayudarte a comprender mejor los conceptos.  
✔️ **Categorías organizadas**: Las preguntas están agrupadas por categorías como "Sin servidor", "Seguridad", "Bases de datos", etc.  
✔️ **Resumen final**: Al terminar el test, obtienes un resumen con:
   - Tu puntaje total.
   - Un termómetro visual de desempeño.
   - Una lista de preguntas falladas con sus explicaciones.  
✔️ **Interfaz intuitiva**: Diseñada para ser fácil de usar y accesible desde cualquier navegador.

---

## 🚀 Cómo funciona

La aplicación carga las preguntas desde un archivo JSON (`questions.json`) y las muestra una por una. Después de responder todas las preguntas, se genera un informe con:
- El número de respuestas correctas e incorrectas.
- Un indicador visual de tu rendimiento (termómetro).
- Un desglose de las preguntas falladas, organizadas por categoría, con explicaciones claras.

---

## 📦 Requisitos previos

Para ejecutar esta aplicación, necesitas lo siguiente:

1. **Un navegador web moderno**: Chrome, Firefox, Edge, etc.
2. **Python (opcional)**: Si deseas ejecutar el servidor localmente.

---

## 🖥 Cómo ejecutar la aplicación

### 1. Clonar el repositorio
Primero, clona este repositorio en tu máquina local:

```bash
git clone https://github.com/nvarona/aws-developer-practice-test.git
cd aws-developer-practice-test
```

## 📋 Documentación del Servidor Web Local

### 2. Ejecutar el servidor local

Puedes ejecutar este servidor web local usando Python. Asegúrate de tener instalado **Python 3.x** y realiza los siguientes pasos:

#### 🔹 Usar el servidor HTTP estándar (con caché)

Si solo necesitas servir archivos estáticos y no te importa el caché:

```bash
python -m http.server 8000
```

#### 🔹 Usar el servidor personalizado (sin caché y con funcionalidades adicionales)

Este servidor incluye funcionalidades como:
- Desactivación del caché (`Cache-Control`)
- Endpoint seguro de apagado (`/shutdown`)
- Información detallada del servidor (`/server-info`)
- Health check ligero (`/health-check`)

Para iniciarlo:

```bash
python server.py
```

---

### 🌐 Acceder al servidor

Una vez iniciado el servidor, abre tu navegador y visita:

```
http://localhost:8000
```

---

### 🔒 Cerrar el servidor

Puedes detener el servidor de dos formas:

- **Mediante terminal**: Pulsa `Ctrl+C`
- **Mediante navegador o herramienta REST**:
  
  Visita esta URL o haz una solicitud GET a:
  ```
  http://localhost:8000/shutdown
  ```

---

### 🧪 Endpoints disponibles

Tu servidor ofrece varias rutas útiles para monitoreo y desarrollo:

| Ruta            | Descripción                                                                           |
|-----------------|---------------------------------------------------------------------------------------|
| `/`             | Sirve los archivos estáticos desde el directorio actual                               |
| `/shutdown`     | Apaga el servidor de forma controlada                                                 |
| `/server-info`  | Muestra información detallada del servidor (SO, memoria, hora, etc.)                  |
| `/health-check` | Devuelve estado básico del servidor en formato JSON (ideal para monitoreo automático) |

---

### 🖥️ Simular diferentes sistemas operativos

Para probar cómo se muestra la información del sistema operativo puedes usar parámetros en la URL:

```
http://localhost:8000/server-info?os=Windows
http://localhost:8000/server-info?os=Linux
http://localhost:8000/server-info?os=Darwin
http://localhost:8000/server-info?os=Android
http://localhost:8000/server-info?os=Unknown
```

> Esto permite ver los distintos iconos y datos asociados a cada tipo de sistema operativo sin cambiar de máquina.

---

### ✅ Requisitos

- Python 3.6+
- (Opcional) Para funcionalidades avanzadas como uso de CPU/Memoria: `psutil`

```bash
pip install psutil
```

---

### 3. Alternativa: Abrir los archivos directamente
Si no deseas usar un servidor local, también puedes abrir el archivo `quiz.html` o `admin.html` directamente en tu navegador. Sin embargo, algunos navegadores pueden bloquear la carga del archivo JSON debido a restricciones de seguridad (CORS). Usar un servidor local es la opción recomendada.

---

## 📂 Estructura del proyecto

El proyecto con las dos aplicaciones está organizado de la siguiente manera:

```
/aws-developer-practice-test
  ├── quiz.html        # Página principal de la aplicación
  ├── server.py        # Si quiere ejecutar en local un servidor web para ofrecer sin cache el Quizz
  ├── script.js        # Lógica de la aplicación (carga de preguntas, validación, etc.)
  ├── questions.json   # Base de datos de preguntas con explicaciones y categorías
  ├── README.md        # Este archivo
  ├── LICENSE          # Licencia del proyecto
  ├── .gitignore       # Archivos ignorados por Git
  ├── admin.html       # Panel de administración de preguntas
  ├── script-admin.js  # Lógica del gestor de preguntas
  ├── categories.json  # Configuración de categorías
  ├── style-admin.css  # Archivo con el diseño de la pagina web
  ├── ...              # (resto de archivos existentes)  
```

---

## ✨ Personalización

Si deseas agregar más preguntas o modificar las existentes, tienes dos formas para hacerlo, la primera simplemente edita el archivo `questions.json`. Asumes el riesgo de poder equivocarte. La segunda mas profesional es entrar en la pagina de `admin.html`, donde tendras todas las facilidades para editar el contenido de las preguntas. Cada pregunta debe seguir este formato:

```json
{
  "id": 1,
  "question": "¿Qué servicio de AWS se utiliza para ejecutar código sin aprovisionar servidores?",
  "options": ["EC2", "Lambda", "S3", "RDS"],
  "answer": "Lambda",
  "explanation": "AWS Lambda es un servicio sin servidor que permite ejecutar código en respuesta a eventos sin necesidad de aprovisionar o administrar servidores.",
  "category": "Sin servidor"
}
```

# 📚 AWS Developer Practice Test - Gestor de Preguntas

![AWS Developer Practice Test](https://img.shields.io/badge/AWS-Developer-blue) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white) ![LocalStorage](https://img.shields.io/badge/LocalStorage-API-FFA500)

## 🌟 Nuevas Funcionalidades del Gestor de Preguntas

Además del sistema de práctica de exámenes, ahora incluimos un **sistema completo CRUD** para gestionar tu banco de preguntas:

### 🛠 Características Avanzadas del Gestor

✔️ **Gestión Completa de Preguntas**:
   - Crear, Leer, Actualizar y Eliminar preguntas (CRUD)
   - Búsqueda y filtrado avanzado por categoría o texto
   - Validación automática de formato

✔️ **Sistema de Categorías Dinámico**:
   - Carga desde archivo JSON o localStorage
   - Añadir nuevas categorías directamente desde la interfaz
   - Autocompletado al escribir categorías

✔️ **Importar/Exportar Datos**:
   - Exportar todo el banco de preguntas a JSON
   - Importar preguntas desde archivos JSON externos
   - Compatibilidad con múltiples formatos

✔️ **Persistencia de Datos**:
   - Guardado automático en localStorage
   - Recuperación de datos al recargar la página
   - Sistema de respaldo integrado

✔️ **Interfaz Administrativa Mejorada**:
   - Tabla responsive con paginación
   - Formularios con validación en tiempo real
   - Notificaciones toast para acciones importantes

## 📂 Estructura Ampliada del Proyecto

```
/aws-developer-practice-test
  ├── admin.html              # Panel de administración de preguntas
  ├── script-admin.js         # Lógica del gestor de preguntas
  ├── categories.json         # Configuración de categorías
  ├── config.json             # Configuración general
  ├── ...                     # (resto de archivos existentes)
```

## 🖥 Cómo Acceder al Gestor

1. Ejecuta el servidor local como antes:
   ```bash
   python -m http.server 8000
   ```

2. Abre en tu navegador:
   ```
   http://localhost:8000/admin.html
   ```

## ✨ Personalización Avanzada

Ahora puedes configurar:
- **Categorías predeterminadas** editando `categories.json`
- **Preguntas iniciales** en `questions.json`
- **Estilos personalizados** en el CSS

Ejemplo de `categories.json`:
```json
{
  "categories": [
    "Compute",
    "Storage",
    "Database",
    "Security",
    "Serverless",
    "Networking",
    "DevOps"
  ]
}
```

## 🔄 Flujo de Trabajo Recomendado

1. **Añade preguntas** mediante el formulario administrativo
2. **Organiza por categorías** usando el sistema dinámico
3. **Exporta tu banco** de preguntas para hacer copias de seguridad
4. **Importa preguntas** de otros colegas o recursos
5. **Practica** con tu propio banco de preguntas

## 📌 Próximas Mejoras (Roadmap)

- Sistema de usuarios y autenticación
- Sincronización con base de datos en la nube
- Estadísticas de rendimiento por categoría
- Modo creación de exámenes personalizados
- Integración con AWS API para datos actualizados

---

## 🤝 Contribuciones Ampliadas

Ahora aceptamos:
- Nuevas preguntas con explicaciones detalladas
- Mejoras al sistema de categorías
- Traducciones a otros idiomas
- Diseños alternativos de interfaz

---

🌟 **Con este gestor, ahora tienes control total sobre tu proceso de aprendizaje para el examen AWS Certified Developer!** 🌟

---

> **Nota**: Todos los datos se guardan localmente en tu navegador. Para hacer copias de seguridad, exporta regularmente tu banco de preguntas.

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Si encuentras errores, tienes sugerencias o deseas agregar nuevas preguntas, sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m "Añadir nueva funcionalidad"`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un pull request.

---

## 🙌 Agradecimientos

Este proyecto fue desarrollado en colaboración con **tu asistente de IA favorito** 😊. Juntos creamos una herramienta útil para estudiantes y profesionales que desean prepararse para el examen **AWS Certified Developer**. ¡Esperamos que te sea de gran ayuda!

---

## 📄 Licencia

Este proyecto está bajo la licencia [MIT](LICENSE). Esto significa que puedes usarlo, modificarlo y distribuirlo libremente, siempre que incluyas la licencia original.

---

## 📢 Contacto

Si tienes preguntas o comentarios sobre este proyecto, no dudes en contactarme:

- **GitHub**: [nvarona](https://github.com/nvarona)
- **Email**: nvarona@hotmail.es

---

🌟 **Gracias por usar AWS Developer Practice Test!** 🌟

---

### Nota adicional:
