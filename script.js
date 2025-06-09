// Variables globales
let allQuestions = []; // Todas las preguntas cargadas desde el JSON
let questions = [];    // Las 10 preguntas seleccionadas aleatoriamente
let currentQuestion = 0;
let score = 0;
let userAnswers = []; // Para almacenar las respuestas del usuario

// Elementos del DOM
const quizDiv = document.getElementById('quiz');
const submitButton = document.getElementById('submit');
const resultDiv = document.getElementById('result');

// Cargar el archivo JSON usando fetch
fetch('questions.json')
  .then(response => response.json())
  .then(data => {
    allQuestions = data; // Guardar todas las preguntas en la variable global
    selectRandomQuestions(); // Seleccionar 10 preguntas aleatorias
    loadQuestion();          // Cargar la primera pregunta
  })
  .catch(error => {
    console.error('Error al cargar las preguntas:', error);
    quizDiv.textContent = 'No se pudieron cargar las preguntas. Por favor, verifica el archivo JSON.';
  });

// Función para seleccionar 10 preguntas aleatorias
function selectRandomQuestions() {
  const shuffledQuestions = allQuestions.sort(() => 0.5 - Math.random()); // Mezclar el array
  questions = shuffledQuestions.slice(0, 10); // Tomar las primeras 10 preguntas
}

// Función para cargar una pregunta
function loadQuestion() {
  const q = questions[currentQuestion];
  quizDiv.innerHTML = `
    <div class="question">
      <strong>Pregunta ${currentQuestion + 1} de ${questions.length}</strong><br><br>
      <strong>Categoría: ${q.category}</strong><br><br>${q.question}
    </div>
    ${q.options.map(option => `
      <label>
        <input type="radio" name="answer" value="${option}">
        ${option}
      </label><br>
    `).join('')}
  `;
}

// Función para verificar la respuesta
function checkAnswer() {
  const selectedOption = document.querySelector('input[name="answer"]:checked');
  if (!selectedOption) {
    alert("Por favor, selecciona una respuesta.");
    return;
  }

  // Guardar la respuesta del usuario
  userAnswers[currentQuestion] = {
    question: questions[currentQuestion].question,
    category: questions[currentQuestion].category,
    userAnswer: selectedOption.value,
    correctAnswer: questions[currentQuestion].answer,
    isCorrect: selectedOption.value === questions[currentQuestion].answer,
    explanation: questions[currentQuestion].explanation
  };

  if (userAnswers[currentQuestion].isCorrect) {
    score++;
  }

  currentQuestion++;
  if (currentQuestion < questions.length) {
    loadQuestion();
  } else {
    showResult();
  }
}

// Función para mostrar el resultado final
function showResult() {
  quizDiv.style.display = 'none';
  submitButton.style.display = 'none';

  // Mostrar el puntaje
  resultDiv.innerHTML = `<p>Tu puntaje es: ${score} / ${questions.length}</p>`;

  // Mostrar el termómetro de respuestas acertadas
  const percentage = (score / questions.length) * 100;
  resultDiv.innerHTML += `
    <div style="width: 100%; background-color: #f3f3f3; border-radius: 5px; overflow: hidden;">
      <div style="width: ${percentage}%; height: 20px; background-color: ${
    percentage >= 70 ? 'green' : percentage >= 40 ? 'orange' : 'red'
  }; text-align: center; color: white; font-weight: bold;">
        ${Math.round(percentage)}%
      </div>
    </div>
    <p style="margin-top: 10px;">Nivel de desempeño: ${
      percentage >= 70
        ? 'Excelente'
        : percentage >= 40
        ? 'Aceptable'
        : 'Necesita mejorar'
    }</p>
  `;

  // Mostrar las preguntas falladas organizadas por categoría
  const failedQuestions = userAnswers.filter(answer => !answer.isCorrect);
  if (failedQuestions.length > 0) {
    resultDiv.innerHTML += `<h3>Preguntas falladas:</h3>`;
    const groupedByCategory = groupBy(failedQuestions, 'category');
    for (const [category, questionsInCategory] of Object.entries(groupedByCategory)) {
      resultDiv.innerHTML += `<h4>${category}:</h4>`;
      questionsInCategory.forEach((fail, index) => {
        resultDiv.innerHTML += `
          <div>
            <p><strong>Pregunta:</strong> ${fail.question}</p>
            <p><strong>Tu respuesta:</strong> ${fail.userAnswer}</p>
            <p><strong>Respuesta correcta:</strong> ${fail.correctAnswer}</p>
            <p><strong>Explicación:</strong> ${fail.explanation}</p>
          </div>
        `;
      });
    }
  } else {
    resultDiv.innerHTML += `<p>¡Felicidades! No has fallado ninguna pregunta.</p>`;
  }
}

// Función auxiliar para agrupar elementos por categoría
function groupBy(array, key) {
  return array.reduce((acc, item) => {
    (acc[item[key]] = acc[item[key]] || []).push(item);
    return acc;
  }, {});
}

// Evento para el botón "Enviar respuestas"
submitButton.addEventListener('click', checkAnswer);