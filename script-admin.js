// Variables globales
let questions = [];
let filteredQuestions = [];
let editingIndex = null;
let categories = [];

// Constantes de la pagina web de administracion
const STORAGE_KEY = 'questions'; // Define una constante al inicio del nombre de JSON
const CATEGORIES_STORAGE_KEY = 'quizCategories';
const CATEGORIES_JSON_FILE = 'categories.json';

// Inicialización
document.addEventListener('DOMContentLoaded', function() {
  loadCategoriesData();   // Cargar y configurar categorías
  loadInitialData();      // Tu función existente para cargar preguntas
  
  // Asegurar que el formulario use las categorías actualizadas
  document.getElementById('question-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const categorySelect = document.getElementById('category');
    const category = categorySelect.value === '_new' 
      ? document.getElementById('new-category').value.trim()
      : categorySelect.value;
    
    if (!category) {
      showToast('Por favor selecciona o crea una categoría', 'error');
      return;
    }
  });
  setupEventListeners();  
});

async function loadInitialData() {
  // 1. Intentar cargar de localStorage
  const savedQuestions = localStorage.getItem(STORAGE_KEY);
  
  if (savedQuestions) {
    try {
      questions = JSON.parse(savedQuestions);
      console.log(`Datos cargados de localStorage (${questions.length} preguntas)`);
      updateUI();
      return;
    } catch (e) {
      console.error("Error parseando localStorage:", e);
      localStorage.removeItem(STORAGE_KEY); // Limpiar datos corruptos
    }
  }

  // 2. Intentar cargar del archivo JSON
  try {
    await loadFromFile();
  } catch (error) {
    console.error('Error cargando archivo:', error);
    console.error("Error completo en loadInitialData:", {
      error: error.message,
      stack: error.stack,
      localStorageData: localStorage.getItem('awsQuizQuestions')
    });
    // 3. Cargar datos de muestra como último recurso
    loadSampleData();
  }
}

async function loadFromFile() {
  try {
    const response = await fetch('questions.json');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Validación robusta de la estructura
    if (!Array.isArray(data)) {
      throw new Error("El archivo no contiene un array válido de preguntas");
    }

    const validatedQuestions = data.map((q, index) => {
      // Asignar ID si no existe
      if (!q.id) q.id = index + 1;
      
      // Validar campos obligatorios
      if (!q.question) throw new Error(`Pregunta ${index} no tiene texto`);
      if (!q.options || !Array.isArray(q.options)) {
        throw new Error(`Pregunta ${index} no tiene opciones válidas`);
      }
      if (!q.answer) throw new Error(`Pregunta ${index} no tiene respuesta definida`);
      
      // Asegurar 4 opciones
      const options = [...q.options];
      while (q.options.length < 4) {
        q.options.push("");
      }
      
      // Campos opcionales con valores por defecto
      if (!q.explanation) q.explanation = "";
      if (!q.category) q.category = "General";
      
      return q;
    });

    questions = validatedQuestions;
    saveToStorage();
    console.log(`Datos validados y cargados (${questions.length} preguntas)`);
    updateUI();
    
  } catch (error) {
    console.error('Error en loadFromFile:', error);
    throw error;
  }
}

function loadSampleData() {
  questions = [
    {
      id: 1,
      question: "¿Cuál es el servicio de AWS que proporciona un entorno de ejecución sin servidor para código?",
      options: ["EC2", "Lambda", "ECS", "Fargate"],
      answer: "Lambda",
      explanation: "AWS Lambda es un servicio de computación sin servidor...",
      category: "Serverless"
    },
    {
      id: 2,
      question: "¿Qué servicio de AWS se utiliza para almacenamiento de objetos escalable?",
      options: ["EBS", "EFS", "S3", "FSx"],
      answer: "S3",
      explanation: "Amazon S3 (Simple Storage Service) es un servicio...",
      category: "Storage"
    }
  ];
  
  saveToStorage();
  updateUI();
  showToast('Se cargaron preguntas de muestra', 'warning');
}

function updateUI() {
  filteredQuestions = [...questions];
  renderTable();
  setupEventListeners();
  
  // Mostrar estadísticas
  console.log(`Preguntas cargadas: ${questions.length}`);
  console.log(`Categorías disponibles: ${[...new Set(questions.map(q => q.category))]}`);
}

// Configurar event listeners
function setupEventListeners() {
  // Formulario
  document.getElementById('question-form').addEventListener('submit', handleFormSubmit);
  document.getElementById('cancel-btn').addEventListener('click', cancelEdit);
  
  // Búsqueda y filtros
  document.getElementById('search-input').addEventListener('input', handleSearch);
  document.getElementById('category-filter').addEventListener('change', handleCategoryFilter);
  
  // Importar archivo
  document.getElementById('import-file').addEventListener('change', handleImportFile);
}

// Manejar envío del formulario
function handleFormSubmit(e) {
  e.preventDefault();
  
  const formData = {
    question: document.getElementById('question').value.trim(),
    options: [
      document.getElementById('option0').value.trim(),
      document.getElementById('option1').value.trim(),
      document.getElementById('option2').value.trim(),
      document.getElementById('option3').value.trim()
    ],
    answer: document.getElementById('answer').value.trim(),
    explanation: document.getElementById('explanation').value.trim(),
    category: document.getElementById('category').value
  };

  // Validaciones
  if (!validateForm(formData)) {
    return;
  }

  // Guardar o actualizar
  if (editingIndex !== null) {
    questions[editingIndex] = {
      ...questions[editingIndex],
      ...formData
    };
    showToast('Pregunta actualizada correctamente', 'success');
    cancelEdit();
  } else {
    const newQuestion = {
      id: questions.length > 0 ? Math.max(...questions.map(q => q.id)) + 1 : 1,
      ...formData
    };
    questions.push(newQuestion);
    showToast('Pregunta agregada correctamente', 'success');
  }

  // Después de añadir/editar una pregunta:
  if (!categories.includes(formData.category)) {
    categories.push(formData.category);
    saveCategoriesToStorage();
    updateCategoryDropdowns();
  }

  saveToStorage();
  refreshDisplay();
  document.getElementById('question-form').reset();
}

// Validar formulario
function validateForm(data) {
  // Validación básica
  if (!data.question || !data.answer || !data.category) {
    showToast('Por favor completa todos los campos obligatorios', 'error');
    return false;
  }

  // Asegurar que hay al menos 2 opciones
  if (data.options.length < 2) {
    showToast('Debe haber al menos 2 opciones', 'error');
    return false;
  }

  // Completar hasta 4 opciones si faltan
  while (data.options.length < 4) {
    data.options.push("");
  }

  // Resto de validaciones...
  if (new Set(data.options).size !== data.options.length) {
    showToast('No puedes tener opciones duplicadas', 'error');
    return false;
  }

  if (!data.options.includes(data.answer)) {
    showToast('La respuesta correcta debe estar entre las opciones', 'error');
    return false;
  }

  return true;
}

// Renderizar tabla
function renderTable() {
  const tbody = document.getElementById('questions-tbody');
  
  if (filteredQuestions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" class="empty-state">
          <div>
            <p style="font-size: 1.2rem; margin-bottom: 10px;">📝 No hay preguntas</p>
            <p>Agrega tu primera pregunta usando el formulario anterior</p>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = filteredQuestions.map((question, index) => {
    // Asegurar que siempre hay 4 opciones
    const options = [...(question.options || [])];
    while (options.length < 4) {
      options.push("");
    }

    return `
    <tr>
      <td><strong>#${question.id}</strong></td>
      <td>        
        <div class="question-text" title="${escapeHtml(question.question)}">
          ${escapeHtml(question.question)}
        </div>
      </td>
      <td>
        ${options.map((opt, i) => 
          `${String.fromCharCode(65 + i)}) ${escapeHtml(opt)}<br>`
        ).join('')}
      </td>
      <td><strong style="color: #27ae60;">${escapeHtml(question.answer)}</strong></td>
            <td>
        <span style="background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 0.85rem;">
          ${escapeHtml(question.category)}
        </span>
      </td>
      <td>
        <div style="display: flex; gap: 5px;">
          <button onclick="editQuestion(${questions.indexOf(question)})" class="btn btn-warning btn-small">
            ✏️ Editar
          </button>
          <button onclick="deleteQuestion(${questions.indexOf(question)})" class="btn btn-danger btn-small">
            🗑️ Eliminar
          </button>
        </div>
      </td>
    </tr>
    `;
  }).join('');
}

// Editar pregunta
function editQuestion(index) {
  const question = questions[index];
  editingIndex = index;
  
  // Llenar formulario
  document.getElementById('editing-index').value = index;
  document.getElementById('question').value = question.question;
  document.getElementById('option0').value = question.options[0];
  document.getElementById('option1').value = question.options[1];
  document.getElementById('option2').value = question.options[2];
  document.getElementById('option3').value = question.options[3];
  document.getElementById('answer').value = question.answer;
  document.getElementById('explanation').value = question.explanation;
  document.getElementById('category').value = question.category;
  
  // Cambiar botones
  document.getElementById('save-btn').textContent = '✅ Actualizar Pregunta';
  document.getElementById('cancel-btn').style.display = 'inline-block';
  
  // Scroll al formulario
  document.querySelector('.form-container').scrollIntoView({ behavior: 'smooth' });
  
  renderTable();
}

// Cancelar edición
function cancelEdit() {
  editingIndex = null;
  document.getElementById('question-form').reset();
  document.getElementById('save-btn').textContent = '💾 Guardar Pregunta';
  document.getElementById('cancel-btn').style.display = 'none';
  renderTable();
}

// Eliminar pregunta
function deleteQuestion(index) {
  if (confirm('¿Estás seguro de que quieres eliminar esta pregunta?')) {
    questions.splice(index, 1);
    saveToStorage();
    refreshDisplay();
    showToast('Pregunta eliminada correctamente', 'success');
    
    if (editingIndex === index) {
      cancelEdit();
    }
  }
}

// Búsqueda
function handleSearch(e) {
  const searchTerm = e.target.value.toLowerCase();
  applyFilters(searchTerm, document.getElementById('category-filter').value);
}

// Filtro por categoría
function handleCategoryFilter(e) {
  const category = e.target.value;
  applyFilters(document.getElementById('search-input').value.toLowerCase(), category);
}

// Aplicar filtros
function applyFilters(searchTerm, category) {
  filteredQuestions = questions.filter(question => {
    const matchesSearch = !searchTerm || 
      question.question.toLowerCase().includes(searchTerm) ||
      question.options.some(opt => opt.toLowerCase().includes(searchTerm)) ||
      question.answer.toLowerCase().includes(searchTerm);
    
    const matchesCategory = !category || question.category === category;
    
    return matchesSearch && matchesCategory;
  });
  
  renderTable();
}

// Actualizar display
function refreshDisplay() {
  applyFilters(
    document.getElementById('search-input').value.toLowerCase(),
    document.getElementById('category-filter').value
  );
}

// Exportar preguntas
function exportQuestions() {
  if (questions.length === 0) {
    showToast('No hay preguntas para exportar', 'error');
    return;
  }
  
  const dataStr = JSON.stringify(questions, null, 2);
  const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
  
  const exportFileDefaultName = `aws-quiz-questions-${new Date().toISOString().split('T')[0]}.json`;
  
  const linkElement = document.createElement('a');
  linkElement.setAttribute('href', dataUri);
  linkElement.setAttribute('download', exportFileDefaultName);
  linkElement.click();
  
  showToast('Preguntas exportadas correctamente', 'success');
}

// Importar preguntas
function importQuestions() {
  document.getElementById('import-file').click();
}

// Manejar archivo importado
function handleImportFile(e) {
  const file = e.target.files[0];
  if (!file) return;
  
  const reader = new FileReader();
  reader.onload = function(e) {
    try {
      const importedQuestions = JSON.parse(e.target.result);
      
      // Validación más flexible
      const validatedQuestions = importedQuestions.map((q, i) => ({
        id: q.id || i + 1,
        question: q.question || "Pregunta sin texto",
        options: q.options && q.options.length >= 2 ? q.options : ["Opción 1", "Opción 2"],
        answer: q.answer || (q.options && q.options[0]) || "Opción 1",
        explanation: q.explanation || "",
        category: q.category || "General"
      }));
      
      questions = validatedQuestions;
      saveToStorage();
      refreshDisplay();
      showToast(`${questions.length} preguntas importadas`, 'success');
    } catch (error) {
      showToast('Error al importar: ' + error.message, 'error');
    }
  };
  reader.readAsText(file);
}

// Guardar en localStorage
function saveToStorage() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(questions)); // Clave unificada a STORAGE_KEY
}

// Mostrar toast notification
function showToast(message, type = 'success') {
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  
  document.body.appendChild(toast);
  
  setTimeout(() => {
    toast.remove();
  }, 3000);
}

// Escapar HTML
function escapeHtml(text) {
  if (text === undefined || text === null) return ''; // Manejar valores nulos
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(text).replace(/[&<>"']/g, m => map[m]);
}

function normalizeExistingQuestions() {
  questions = questions.map((q, i) => {
    if (!q.options || q.options.length < 2) {
      q.options = q.options || [];
      while (q.options.length < 2) {
        q.options.push(`Opción ${q.options.length + 1}`);
      }
    }
    while (q.options.length < 4) {
      q.options.push("");
    }
    return q;
  });
  saveToStorage();
  refreshDisplay();
}

// Función para actualizar ambos selects
function updateCategoryDropdowns() {
  updateDropdown('category-filter'); // Select del filtro
  updateDropdown('category');        // Select del formulario
}

function updateDropdown(elementId) {
  const dropdown = document.getElementById(elementId);
  if (!dropdown) return;
  
  const currentValue = dropdown.value;
  
  dropdown.innerHTML = `
    <option value="">${elementId === 'category' ? 'Selecciona una categoría' : 'Todas las categorías'}</option>
    ${categories.map(cat => `
      <option value="${cat}">${cat}</option>
    `).join('')}
    ${elementId === 'category' ? '<option value="_new">+ Añadir nueva categoría</option>' : ''}
  `;
  
  // Restaurar el valor seleccionado si aún existe
  if (categories.includes(currentValue)) {
    dropdown.value = currentValue;
  }
}

// Función para añadir nueva categoría
function addNewCategory(newCategory) {
  if (newCategory && !categories.includes(newCategory)) {
    categories.push(newCategory);
    saveCategories();
    updateCategoryDropdowns();
  }
}

// Configurar listeners para nueva categoría
function setupCategoryListeners() {
  const categorySelect = document.getElementById('category');
  const newCategoryInput = document.getElementById('new-category');
  const addCategoryBtn = document.getElementById('add-category-btn');
  
  categorySelect.addEventListener('change', function() {
    if (this.value === '_new') {
      this.style.display = 'none';
      newCategoryInput.style.display = 'inline-block';
      newCategoryInput.focus();
    }
  });
  
  addCategoryBtn.addEventListener('click', function() {
    categorySelect.style.display = 'none';
    newCategoryInput.style.display = 'inline-block';
    newCategoryInput.focus();
  });
  
  newCategoryInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
      addNewCategory(this.value.trim());
      this.value = '';
      this.style.display = 'none';
      categorySelect.style.display = 'inline-block';
    }
  });
}

// Cargar categorías al inicio
async function loadCategoriesData() {
  // 1. Intentar cargar de localStorage
  const savedCategories = localStorage.getItem(CATEGORIES_STORAGE_KEY);
  
  if (savedCategories) {
    try {
      categories = JSON.parse(savedCategories);
      console.log(`Categorías cargadas de localStorage (${categories.length} categorías)`);
      updateCategoryDropdowns();
      return;
    } catch (e) {
      console.error("Error parseando categorías:", e);
      localStorage.removeItem(CATEGORIES_STORAGE_KEY);
    }
  }

  // 2. Intentar cargar del archivo JSON
  try {
    await loadCategoriesFromFile();
  } catch (error) {
    console.error('Error cargando categorías:', error);
    // 3. Cargar categorías por defecto
    loadDefaultCategories();
  }
}

async function loadCategoriesFromFile() {
  try {
    const response = await fetch(CATEGORIES_JSON_FILE);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    
    const data = await response.json();
    
    // Validar estructura
    if (!Array.isArray(data.categories)) {
      throw new Error("El archivo no contiene un array válido de categorías");
    }
    
    categories = [...new Set(data.categories)]; // Eliminar duplicados
    saveCategoriesToStorage();
    console.log(`Categorías cargadas de archivo (${categories.length} categorías)`);
    updateCategoryDropdowns();
  } catch (error) {
    console.error('Error en loadCategoriesFromFile:', error);
    throw error;
  }
}

function loadDefaultCategories() {
  categories = [
    "AWS DVA-C02",
    "Networking",
    "Security",
    "Serverless",
    "Storage",
    "Database",
    "Compute",
    "Monitoring"
  ];
  saveCategoriesToStorage();
  updateCategoryDropdowns();
}

// Guardar categorías en localStorage
function saveCategoriesToStorage() {
  localStorage.setItem(CATEGORIES_STORAGE_KEY, JSON.stringify(categories));
}

function extractCategoriesFromQuestions() {
  const questionCategories = questions.map(q => q.category).filter(Boolean);
  categories = [...new Set([...categories, ...questionCategories])];
  updateCategoryDropdowns();
}