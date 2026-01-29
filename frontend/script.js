const API_URL = "http://127.0.0.1:8000";

// --- REFERENCIAS AL HTML ---
const mySelect = document.getElementById('my-pokemon-select');
const enemySelect = document.getElementById('enemy-pokemon-select');
const btnAnalyze = document.getElementById('analyze-btn');
const resultArea = document.getElementById('result-area');
const recommendationText = document.getElementById('recommendation-text');
const reasonsList = document.getElementById('reasons-list');

// --- 1. CARGAR LISTA DE POKEMON ---
async function loadPokemonNames() {
    try {
        const response = await fetch(`${API_URL}/pokemon/names`);
        // CORREGIDO: Usamos la variable 'names' correctamente
        const names = await response.json();

        names.forEach(name => {
            // Opción para Mi Equipo
            const option1 = document.createElement('option');
            option1.value = name;
            option1.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            mySelect.appendChild(option1);

            // Opción para Enemigo
            const option2 = document.createElement('option');
            option2.value = name;
            option2.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            enemySelect.appendChild(option2);
        });
    } catch (error) {
        console.error("Error cargando lista:", error);
    }
}

// --- 2. OBTENER DATOS DE UN POKÉMON (Para Combate y Sprite) ---
async function fetchPokemonData(name) {
    // Llama al endpoint /pokemon/{name} del backend
    const response = await fetch(`${API_URL}/pokemon/${name}`);
    if (!response.ok) throw new Error("Pokemon no encontrado");
    return await response.json();
}

// --- 3. LOGICA DE IMÁGENES (SPRITES) ---
async function updateSprite(selectElement, previewId) {
    const name = selectElement.value;
    const previewElement = document.getElementById(previewId);
    
    if (!name) return;

    // Ponemos un relojito mientras carga
    previewElement.innerHTML = '<span style="font-size: 24px;">⏳</span>';

    try {
        const data = await fetchPokemonData(name);
        if (data.sprite) {
            previewElement.innerHTML = `<img src="${data.sprite}" alt="${name}" style="height: 100%;">`;
        } else {
            previewElement.innerHTML = '<span>Sin Imagen</span>';
        }
    } catch (error) {
        console.error("Error imagen:", error);
        previewElement.innerHTML = '<span>❌</span>';
    }
}

// ESCUCHAMOS CAMBIOS EN LOS DESPLEGABLES
mySelect.addEventListener('change', () => {
    updateSprite(mySelect, 'my-pokemon-preview');
});

enemySelect.addEventListener('change', () => {
    updateSprite(enemySelect, 'enemy-pokemon-preview');
});

// --- 4. ANALIZAR COMBATE ---
btnAnalyze.addEventListener('click', async () => {
    const myName = mySelect.value;
    const enemyName = enemySelect.value;

    if (!myName || !enemyName) {
        alert("¡Selecciona dos Pokémon primero!");
        return;
    }

    try {
        // Pedimos datos completos al backend
        const myData = await fetchPokemonData(myName);
        const enemyData = await fetchPokemonData(enemyName);

        const payload = {
            "my_team": { "members": [myData] },
            "enemy_pokemon": enemyData
        };

        const response = await fetch(`${API_URL}/analyze/combat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();

        // MOSTRAR RESULTADOS
        resultArea.classList.remove('hidden');
        
        // CORREGIDO: Ahora 'recommendationText' existe y no dará error
        recommendationText.innerHTML = `<strong>${result.summary}</strong>`;
        
        reasonsList.innerHTML = '';
        const bestAnalysis = result.analysis[0];
        bestAnalysis.reasons.forEach(reason => {
            const li = document.createElement('li');
            li.textContent = reason;
            reasonsList.appendChild(li);
        });

    } catch (error) {
        console.error("Error análisis:", error);
        alert("Error al analizar. Mira la consola (F12) para más detalles.");
    }
});

// INICIAR
loadPokemonNames();