    // Variables globales
    let allQuestions = [];
    let questions = [];
    let currentQuestion = 0;
    let score = 0;
    let userAnswers = [];

    // Elementos del DOM
    const quizSection = document.getElementById('quiz-section');
    const resultsSection = document.getElementById('results-section');
    const quizContent = document.getElementById('quiz-content');
    const submitBtn = document.getElementById('submit-btn');
    const questionCounter = document.getElementById('question-counter');
    const categoryBadge = document.getElementById('category-badge');
    const progressFill = document.getElementById('progress-fill');

    // Cargar el archivo JSON usando fetch
    fetch('questions.json')
      .then(response => response.json())
      .then(data => {
        allQuestions = data; // Guardar todas las preguntas en la variable global
        //console.log("Datos del JSON:", allQuestions); // 👈 Añade esta línea
        selectRandomQuestions(); // Seleccionar 10 preguntas aleatorias
        loadQuestion();          // Cargar la primera pregunta
      })
      .catch(error => {
        console.error('Error al cargar las preguntas:', error);
        quizDiv.textContent = 'No se pudieron cargar las preguntas. Por favor, verifica el archivo JSON.';
      });

    // Seleccionar 10 preguntas aleatorias
    function selectRandomQuestions() {
      if (!Array.isArray(allQuestions) || allQuestions.length === 0) {
        console.warn("No hay preguntas disponibles para seleccionar.");
        questions = [];
        return;
      }
      const numberOfQuestionsToSelect = Math.min(10, allQuestions.length);
      const shuffled = [...allQuestions].sort(() => 0.5 - Math.random());
      questions = shuffled.slice(0, numberOfQuestionsToSelect);
      //console.log(`Se han seleccionado ${questions.length} preguntas.`);
    }

    // Cargar pregunta actual
    function loadQuestion() {
      const q = questions[currentQuestion];
      const progressPercentage = ((currentQuestion + 1) / questions.length) * 100;
      
      // Actualizar elementos de progreso
      questionCounter.textContent = `Pregunta ${currentQuestion + 1} de ${questions.length}`;
      if (categoryBadge) {
        categoryBadge.textContent = q.category || "Sin categoría"; // Evita mostrar undefined
      }
      //categoryBadge.textContent = q.category;
      progressFill.style.width = `${progressPercentage}%`;
      
      // Generar HTML de la pregunta
      quizContent.innerHTML = `
        <div class="question-text">${q.question}</div>
        <div class="options-container">
          ${q.options.map((option, index) => `
            <div class="option">
              <input type="radio" id="option${index}" name="answer" value="${option}">
              <label for="option${index}" class="option-label">${option}</label>
            </div>
          `).join('')}
        </div>
      `;
      
      // Actualizar texto del botón
      submitBtn.textContent = currentQuestion === questions.length - 1 ? 'Ver Resultados' : 'Siguiente Pregunta';
    }

    // Verificar respuesta
    function checkAnswer() {
      const selectedOption = document.querySelector('input[name="answer"]:checked');
      
      if (!selectedOption) {
        // Animación de error suave
        submitBtn.style.animation = 'shake 0.5s ease-in-out';
        setTimeout(() => submitBtn.style.animation = '', 500);
        return;
      }

      // Guardar respuesta del usuario
      const q = questions[currentQuestion];
      userAnswers[currentQuestion] = {
        question: q.question,
        category: q.category,
        userAnswer: selectedOption.value,
        correctAnswer: q.answer,
        isCorrect: selectedOption.value === q.answer,
        explanation: q.explanation
      };

      if (userAnswers[currentQuestion].isCorrect) {
        score++;
      }

      currentQuestion++;
      
      if (currentQuestion < questions.length) {
        setTimeout(() => loadQuestion(), 300);
      } else {
        setTimeout(() => showResults(), 300);
      }
    }

    // Mostrar resultados finales
    function showResults() {
      quizSection.classList.add('hidden');
      resultsSection.classList.remove('hidden');

      const percentage = Math.round((score / questions.length) * 100);
      let performanceLevel, performanceColor;

      if (percentage >= 70) {
        performanceLevel = '¡Excelente! 🎉';
        performanceColor = 'linear-gradient(135deg, #27ae60, #2ecc71)';
      } else if (percentage >= 40) {
        performanceLevel = 'Aceptable 👍';
        performanceColor = 'linear-gradient(135deg, #f39c12, #e67e22)';
      } else {
        performanceLevel = 'Necesita mejorar 📚';
        performanceColor = 'linear-gradient(135deg, #e74c3c, #c0392b)';
      }

      let resultsHTML = `
        <div class="score-display">${score} / ${questions.length}</div>
        <div class="thermometer-container">
          <div class="thermometer">
            <div class="thermometer-fill" style="width: ${percentage}%; background: ${performanceColor};">
              ${percentage}%
            </div>
          </div>
          <div class="performance-text" style="color: ${percentage >= 70 ? '#27ae60' : percentage >= 40 ? '#f39c12' : '#e74c3c'}">
            ${performanceLevel}
          </div>
        </div>
      `;

      // Mostrar preguntas falladas
      const failedQuestions = userAnswers.filter(answer => !answer.isCorrect);
      
      if (failedQuestions.length > 0) {
        resultsHTML += `<div class="failed-questions">
          <h3>📝 Preguntas para repasar</h3>`;
        
        // Agrupar por categoría
        const groupedByCategory = groupBy(failedQuestions, 'category');
        
        for (const [category, questionsInCategory] of Object.entries(groupedByCategory)) {
          resultsHTML += `
            <div class="category-section">
              <div class="category-title">📂 ${category}</div>`;
          
          questionsInCategory.forEach(fail => {
            resultsHTML += `
              <div class="failed-question">
                <p><strong>Pregunta:</strong> ${fail.question}</p>
                <p><strong>Tu respuesta:</strong> <span class="user-answer">${fail.userAnswer}</span></p>
                <p><strong>Respuesta correcta:</strong> <span class="correct-answer">${fail.correctAnswer}</span></p>
                <div class="explanation">
                  <strong>💡 Explicación:</strong> ${fail.explanation}
                </div>
              </div>`;
          });
          
          resultsHTML += `</div>`;
        }
        
        resultsHTML += `</div>`;
      } else {
        resultsHTML += `
          <div class="congratulations">
            <h3>¡Felicidades! 🏆</h3>
            <p>Has respondido correctamente todas las preguntas. ¡Eres un experto en AWS!</p>
          </div>`;
      }

      // Agregar botón para reiniciar
      resultsHTML += `
        <div class="submit-container" style="margin-top: 40px;">
          <button onclick="restartQuiz()" class="submit-btn">
            🔄 Realizar otro quiz
          </button>
        </div>`;

      resultsSection.innerHTML = resultsHTML;

      // Animar la barra de progreso de resultados
      setTimeout(() => {
        const thermometerFill = document.querySelector('.thermometer-fill');
        if (thermometerFill) {
          thermometerFill.style.width = '0%';
          setTimeout(() => {
            thermometerFill.style.width = `${percentage}%`;
          }, 100);
        }
      }, 500);
    }

    // Función para agrupar por categoría
    function groupBy(array, key) {
      return array.reduce((acc, item) => {
        (acc[item[key]] = acc[item[key]] || []).push(item);
        return acc;
      }, {});
    }

    // Reiniciar quiz
    function restartQuiz() {
      // Resetear variables
      currentQuestion = 0;
      score = 0;
      userAnswers = [];
      
      // Seleccionar nuevas preguntas aleatorias
      selectRandomQuestions();
      
      // Mostrar sección del quiz
      resultsSection.classList.add('hidden');
      quizSection.classList.remove('hidden');
      
      // Cargar primera pregunta
      loadQuestion();
    }

    // Agregar animación de shake para el botón
    const shakeKeyframes = `
      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
      }
    `;
    
    const style = document.createElement('style');
    style.textContent = shakeKeyframes;
    document.head.appendChild(style);

    // Evento listeners para el botón "Enviar respuestas"
    submitBtn.addEventListener('click', checkAnswer);
