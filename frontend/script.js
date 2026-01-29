const API_URL = "http://127.0.0.1:8000";

// Elementos del DOM
const mySelect = document.getElementById('my-pokemon-select');
const enemySelect = document.getElementById('enemy-pokemon_select');
const btnAnalyze = document.getElementById('analyze-btn');
const reultArea = document.getElementById('result-area');
const recomendationText = document.getElementById('recomendation-text');
const reasonsList = document.getElementById('reasons-list');

// Cargar lista de pokemons al iniciar
async function loadPokemonNames() {
    try {
        const response = await fetch(`${API_URL}/pokemon/names`);
        const name = await response.json();

        names.forEach(name => {
            // Opcion para mi equipo
            const option1 = document.createElement('option');
            option1.value = name;
            option1.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            mySelect.appendChild(option1);

            // Option para equipo enemigo
            const option2 = document.createElement('option');
            option2.value = name;
            option2.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            enemySelect.appendChild(option2);
        });
    } catch (error) {
        console.error('Error al cargar la lista de pokemons:', error);
        alert('Error: No se pudo conectar con el backend. Esta encendido?');
    }
}


// Buscar datos completos de un pokemon
async function fetchPokemonData(name) {
    const response = await fetch(`${API_URL}/pokemon/${name}`);
    return await response.json();
}


// Analizar combate
btnAnalyze.addEventListener('click', async () => {
    const myName = mySelect.value;
    const enemyName = enemySelect.value;

    if (!myName || !enemyName) {
        alert("Por favor, selecciona ambos pokemons.");
        return;
    }

    // Obtenemos los datos completos (Stats, tipos, habilidades, etc.) del Backend
    const myPokemonData = await fetchPokemonData(myName);
    const enemyPokemonData = await fetchPokemonData(enemyName);

    // Construimos el JSON que espera el API
    const payload = {
        "my_team": {
            "members": [myPokemonData]
        },
        "enemy_pokemon": enemyPokemonData
    };

    try {
        const response = await fetch(`${API_URL}/analyze/combat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
    });

    const result = await response.json();

    // Mostrar resultados en el DOM
    resultArea.classList.remove('hidden');
    recomendationText.innerHTML = `<strong>${result.summary}</strong>`;

    // Limpiar lista anterior
    reasonsList.innerHTML = '';

    // Solo mostramos las razones del MEJOR pokemon
    const bestAnalysis = result.analysis[0];
    bestAnalysis.reasons.forEach(reason => {
        const li = document.createElement('li');
        li.textContent = reason;
        reasonsList.appendChild(li);
    });

    } catch (error) {
        console.error('Error al analizar el combate:', error);
        alert("Ocurrio un error al analizar el combate.")
    }
});

// Arrancar
loadPokemonNames();
