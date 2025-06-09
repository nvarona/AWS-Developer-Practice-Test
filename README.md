
# 📚 AWS Developer Practice Test

![AWS Developer Practice Test](https://img.shields.io/badge/AWS-Developer-blue) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?logo=javascript&logoColor=black) ![HTML5](https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white)

Este proyecto es una **aplicación web interactiva** diseñada para ayudarte a practicar preguntas del examen **AWS Certified Developer**. La aplicación te permite realizar pruebas con preguntas aleatorias, ver tus respuestas falladas y recibir explicaciones detalladas para mejorar tu aprendizaje.

---

## 🛠 Características principales

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

### 2. Ejecutar el servidor local
Puedes usar Python para servir la aplicación localmente. Asegúrate de tener Python instalado y ejecuta el siguiente comando:

```bash
python -m http.server 8000
```

Y si quiere ejecutar el sevidor local sin que realice cache, puede ejecutar este comando:

```bash
python server.py
```

Luego, abre tu navegador y visita:

```
http://localhost:8000
```

### 3. Alternativa: Abrir los archivos directamente
Si no deseas usar un servidor local, también puedes abrir el archivo `index.html` directamente en tu navegador. Sin embargo, algunos navegadores pueden bloquear la carga del archivo JSON debido a restricciones de seguridad (CORS). Usar un servidor local es la opción recomendada.

---

## 📂 Estructura del proyecto

El proyecto está organizado de la siguiente manera:

```
/aws-developer-practice-test
  ├── quizz.html       # Página principal de la aplicación
  ├── server.py        # Si quiere ejecutar en local un servidor web para ofrecer sin cache el Quizz
  ├── script.js        # Lógica de la aplicación (carga de preguntas, validación, etc.)
  ├── questions.json   # Base de datos de preguntas con explicaciones y categorías
  ├── README.md        # Este archivo
  ├── LICENSE          # Licencia del proyecto
  ├── .gitignore       # Archivos ignorados por Git
```

---

## ✨ Personalización

Si deseas agregar más preguntas o modificar las existentes, simplemente edita el archivo `questions.json`. Cada pregunta debe seguir este formato:

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
