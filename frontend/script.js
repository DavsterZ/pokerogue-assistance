const API_URL = "http://127.0.0.1:8000";

// REFERENCIAS
const teamContainer = document.getElementById('team-container');
const btnAddMember = document.getElementById('add-member-btn');
const teamCountSpan = document.getElementById('team-count');
const enemySelect = document.getElementById('enemy-pokemon-select');
const btnAnalyze = document.getElementById('analyze-btn');
const btnCatch = document.getElementById('catch-btn');
const resultArea = document.getElementById('result-area');
const recommendationText = document.getElementById('recommendation-text');
const reasonsList = document.getElementById('reasons-list');

let allPokemonNames = [];

// 1. INICIALIZACIÓN
async function init() {
    try {
        const response = await fetch(`${API_URL}/pokemon/names`);
        allPokemonNames = await response.json();
        
        // Rellenar enemigo
        fillSelect(enemySelect);
        
        // CORRECCIÓN CRÍTICA:
        // Buscamos el slot-0 que ya existe en el HTML
        const firstSlot = document.getElementById('slot-0');
        const firstSelect = firstSlot.querySelector('select');
        
        // Lo rellenamos y activamos sus eventos MANUALMENTE
        fillSelect(firstSelect);
        setupSlotEvents(firstSlot);

        // Actualizamos el contador al inicio para asegurar que marque 1/6
        updateCount();

    } catch (error) {
        console.error("Error inicial:", error);
    }
}

// Auxiliar para llenar un select
function fillSelect(selectElement) {
    // Guardamos la selección actual si la hubiera (para no resetear al re-llenar)
    const currentValue = selectElement.value;
    
    // Limpiamos opciones anteriores (menos la primera de "Elige...")
    selectElement.innerHTML = '<option value="" disabled selected>Elige...</option>';
    
    allPokemonNames.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
        selectElement.appendChild(option);
    });

    if(currentValue) selectElement.value = currentValue;
}

// 2. GESTIÓN DINÁMICA DE SLOTS
btnAddMember.addEventListener('click', () => {
    // Contamos cuántos hay ahora mismo
    const currentSlots = document.querySelectorAll('.pokemon-slot').length;
    
    if (currentSlots >= 6) {
        alert("Máximo 6 Pokémon en el equipo.");
        return;
    }

    const newId = `slot-${Date.now()}`;
    
    // Crear el HTML del nuevo slot
    const slotDiv = document.createElement('div');
    slotDiv.className = 'pokemon-slot';
    slotDiv.id = newId;
    slotDiv.innerHTML = `
        <select class="team-select">
            <option value="" disabled selected>Nuevo...</option>
        </select>
        <div class="mini-preview">?</div>
        <button class="remove-btn" onclick="removeSlot('${newId}')">×</button>
    `;

    teamContainer.appendChild(slotDiv);
    
    // Rellenar y activar eventos
    const newSelect = slotDiv.querySelector('select');
    fillSelect(newSelect);
    setupSlotEvents(slotDiv);
    
    updateCount();
});

// Función global para borrar slots
window.removeSlot = (id) => {
    // CORRECCIÓN: Evitar borrar el slot-0 si es el único que queda
    if (id === 'slot-0') {
        // Opcional: Si quieres que el primero se pueda "vaciar" pero no borrar:
        const slot0 = document.getElementById('slot-0');
        slot0.querySelector('select').value = "";
        slot0.querySelector('.mini-preview').innerHTML = "?";
        return; 
    }

    const element = document.getElementById(id);
    if (element) {
        element.remove();
        updateCount();
    }
};

function updateCount() {
    const count = document.querySelectorAll('.pokemon-slot').length;
    teamCountSpan.textContent = count;
}

// 3. EVENTOS DE IMAGENES
function setupSlotEvents(slotDiv) {
    const select = slotDiv.querySelector('select');
    const preview = slotDiv.querySelector('.mini-preview');

    // Quitamos eventos anteriores para evitar duplicados
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    newSelect.addEventListener('change', async () => {
        const name = newSelect.value;
        if (!name) return;
        
        preview.innerHTML = '⏳';
        try {
            const data = await fetchPokemonData(name);
            if(data.sprite) {
                preview.innerHTML = `<img src="${data.sprite}" style="height:100%">`;
            } else {
                preview.innerHTML = '?';
            }
        } catch(e) {
            preview.innerHTML = '❌';
        }
    });
}

// Evento Enemigo
enemySelect.addEventListener('change', async () => {
    const name = enemySelect.value;
    const preview = document.getElementById('enemy-pokemon-preview');
    if (!name) return;
    
    preview.innerHTML = '⏳';
    try {
        const data = await fetchPokemonData(name);
        preview.innerHTML = data.sprite ? `<img src="${data.sprite}" style="height:100%">` : '?';
    } catch(e) { preview.innerHTML = '❌'; }
});

// 4. DATOS Y LLAMADAS
async function getTeamData() {
    const selects = document.querySelectorAll('.team-select');
    const membersData = [];

    for (const select of selects) {
        const name = select.value;
        if (name && name !== "") { // Solo añadimos si hay un nombre seleccionado
            const data = await fetchPokemonData(name);
            membersData.push(data);
        }
    }
    return membersData;
}

async function fetchPokemonData(name) {
    // Si ya tenemos el dato en caché (opcional), lo usamos, si no fetch
    const response = await fetch(`${API_URL}/pokemon/${name}`);
    if (!response.ok) throw new Error("Not found");
    return await response.json();
}

async function handleAction(endpoint) {
    const enemyName = enemySelect.value;
    if (!enemyName) { alert("¡Elige un enemigo!"); return; }

    const teamMembers = await getTeamData();
    if (teamMembers.length === 0) { alert("¡Elige al menos 1 Pokémon en tu equipo!"); return; }

    try {
        const enemyData = await fetchPokemonData(enemyName);

        const payload = {
            "my_team": { "members": teamMembers },
            "enemy_pokemon": enemyData
        };

        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        showResults(result);

    } catch (error) {
        console.error(error);
        alert("Error en la petición");
    }
}

function showResults(result) {
    resultArea.classList.remove('hidden');
    
    if (result.verdict) {
        recommendationText.innerHTML = `<strong style="color:${result.color}">${result.verdict}</strong>`;
        resultArea.style.borderLeftColor = result.color === 'green' ? '#a6e3a1' : '#f38ba8';
    } else {
        recommendationText.innerHTML = `<strong>${result.summary}</strong>`;
        resultArea.style.borderLeftColor = '#89b4fa';
    }

    reasonsList.innerHTML = '';
    const reasons = result.reasons || (result.analysis && result.analysis[0].reasons) || [];
    
    reasons.forEach(r => {
        const li = document.createElement('li');
        li.textContent = r;
        reasonsList.appendChild(li);
    });
}

btnAnalyze.addEventListener('click', () => handleAction('/analyze/combat'));
btnCatch.addEventListener('click', () => handleAction('/analyze/catch'));

init();