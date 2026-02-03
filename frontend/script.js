const API_URL = "http://127.0.0.1:8000";

// REFERENCIAS
const teamContainer = document.getElementById('team-container');
const btnAddMember = document.getElementById('add-member-btn');
const teamCountSpan = document.getElementById('team-count');
const enemySelect = document.getElementById('enemy-pokemon-select');

// Botones de Acción
const btnAnalyze = document.getElementById('analyze-btn');
const btnCatch = document.getElementById('catch-btn');
const btnItem = document.getElementById('item-btn'); // NUEVO

// Selectores de Recompensa (NUEVOS)
const rewardSelects = [
    document.getElementById('reward-1'),
    document.getElementById('reward-2'),
    document.getElementById('reward-3')
];

const resultArea = document.getElementById('result-area');
const recommendationText = document.getElementById('recommendation-text');
const reasonsList = document.getElementById('reasons-list');

let allPokemonNames = [];
let allItemNames = []; // NUEVA LISTA

// 1. INICIALIZACIÓN
async function init() {
    try {
        // Cargar nombres de Pokémon
        const respPoke = await fetch(`${API_URL}/pokemon/names`);
        allPokemonNames = await respPoke.json();
        
        // NUEVO: Cargar nombres de Objetos/MTs
        const respItems = await fetch(`${API_URL}/items/list`);
        allItemNames = await respItems.json();

        // Inicializar selectores
        fillSelect(enemySelect, allPokemonNames);
        
        const firstSlot = document.getElementById('slot-0');
        const firstSelect = firstSlot.querySelector('select');
        fillSelect(firstSelect, allPokemonNames);
        setupSlotEvents(firstSlot);

        // NUEVO: Llenar selectores de objetos
        rewardSelects.forEach(sel => fillItemSelect(sel));

        updateCount();

    } catch (error) {
        console.error("Error inicial:", error);
    }
}

// Auxiliar para llenar Pokémon
function fillSelect(selectElement, dataList) {
    const currentValue = selectElement.value;
    selectElement.innerHTML = '<option value="" disabled selected>Elige...</option>';
    dataList.forEach(name => {
        const option = document.createElement('option');
        option.value = name;
        option.textContent = name.charAt(0).toUpperCase() + name.slice(1);
        selectElement.appendChild(option);
    });
    if(currentValue) selectElement.value = currentValue;
}

// NUEVO: Auxiliar para llenar Objetos (tienen ID y Name)
function fillItemSelect(selectElement) {
    selectElement.innerHTML = '<option value="" disabled selected>Opción...</option>';
    allItemNames.forEach(item => {
        const option = document.createElement('option');
        option.value = item.id; // El ID interno (ej: "tm-swords-dance")
        // Mostramos el nombre bonito + Tier si existe
        let label = item.name;
        if(item.tier && item.tier !== "Unknown") label += ` [${item.tier}]`;
        option.textContent = label;
        selectElement.appendChild(option);
    });
}

// 2. GESTIÓN DE SLOTS DE EQUIPO
btnAddMember.addEventListener('click', () => {
    const currentSlots = document.querySelectorAll('.pokemon-slot').length;
    if (currentSlots >= 6) { alert("Máximo 6 Pokémon."); return; }

    const newId = `slot-${Date.now()}`;
    const slotDiv = document.createElement('div');
    slotDiv.className = 'pokemon-slot';
    slotDiv.id = newId;
    slotDiv.innerHTML = `
        <select class="team-select"><option value="" disabled selected>Nuevo...</option></select>
        <div class="mini-preview">?</div>
        <button class="remove-btn" onclick="removeSlot('${newId}')">×</button>
    `;
    teamContainer.appendChild(slotDiv);
    
    const newSelect = slotDiv.querySelector('select');
    fillSelect(newSelect, allPokemonNames);
    setupSlotEvents(slotDiv);
    updateCount();
});

window.removeSlot = (id) => {
    if (id === 'slot-0') {
        const slot0 = document.getElementById('slot-0');
        slot0.querySelector('select').value = "";
        slot0.querySelector('.mini-preview').innerHTML = "?";
        return; 
    }
    const element = document.getElementById(id);
    if (element) { element.remove(); updateCount(); }
};

function updateCount() {
    teamCountSpan.textContent = document.querySelectorAll('.pokemon-slot').length;
}

function setupSlotEvents(slotDiv) {
    const select = slotDiv.querySelector('select');
    const preview = slotDiv.querySelector('.mini-preview');
    const newSelect = select.cloneNode(true);
    select.parentNode.replaceChild(newSelect, select);

    newSelect.addEventListener('change', async () => {
        const name = newSelect.value;
        if (!name) return;
        preview.innerHTML = '⏳';
        try {
            const data = await fetchPokemonData(name);
            preview.innerHTML = data.sprite ? `<img src="${data.sprite}" style="height:100%">` : '?';
        } catch(e) { preview.innerHTML = '❌'; }
    });
}

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

// 3. API FETCHING
async function fetchPokemonData(name) {
    const response = await fetch(`${API_URL}/pokemon/${name}`);
    if (!response.ok) throw new Error("Not found");
    return await response.json();
}

async function getTeamData() {
    const selects = document.querySelectorAll('.team-select');
    const membersData = [];
    for (const select of selects) {
        const name = select.value;
        if (name && name !== "") {
            const data = await fetchPokemonData(name);
            membersData.push(data);
        }
    }
    return membersData;
}

// 4. LÓGICA DE ACCIONES (COMBATE, CAPTURA Y ITEMS)
async function handleAction(endpoint, isItemAnalysis = false) {
    const teamMembers = await getTeamData();
    if (teamMembers.length === 0) { alert("Elige tu equipo primero."); return; }

    let payload = {};

    if (isItemAnalysis) {
        // LÓGICA DE RECOMPENSAS
        const options = [];
        rewardSelects.forEach(sel => {
            if(sel.value) options.push(sel.value);
        });

        if (options.length === 0) { alert("Selecciona al menos 1 objeto."); return; }

        payload = {
            "my_team": { "members": teamMembers },
            "options": options
        };

    } else {
        // LÓGICA DE COMBATE/CAPTURA
        const enemyName = enemySelect.value;
        if (!enemyName) { alert("¡Elige un enemigo!"); return; }
        const enemyData = await fetchPokemonData(enemyName);
        
        payload = {
            "my_team": { "members": teamMembers },
            "enemy_pokemon": enemyData
        };
    }

    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        showResults(result, isItemAnalysis);

    } catch (error) {
        console.error(error);
        alert("Error en la petición. Mira la consola.");
    }
}

function showResults(result, isItemAnalysis) {
    resultArea.classList.remove('hidden');
    reasonsList.innerHTML = '';

    if (isItemAnalysis) {
        // --- MODO RECOMPENSAS (CON DESCRIPCIÓN) ---
        resultArea.style.borderLeftColor = '#f9e2af'; // Borde dorado
        
        // 1. Cabecera con la mejor opción y su descripción destacada
        const bestItem = result.best_option;
        const bestDesc = bestItem.data.description || "Sin descripción disponible.";
        
        recommendationText.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong style="font-size: 1.2em;">🏆 ${result.summary}</strong>
                <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; margin-top: 5px; font-style: italic; color: #bac2de;">
                    "${bestDesc}"
                </div>
            </div>
        `;

        // 2. Lista detallada de todas las opciones comparadas
        result.analysis.forEach(opt => {
            const li = document.createElement('li');
            const desc = opt.data.description || "";
            
            li.style.marginBottom = "12px"; // Separación entre items
            li.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: baseline;">
                    <strong>${opt.name}</strong>
                    <small style="color: ${opt.score > 0 ? '#a6e3a1' : '#f38ba8'}">${opt.score} pts</small>
                </div>
                <div style="font-size: 0.9em; color: #a6adc8; margin-bottom: 2px;">${desc}</div>
                <div style="font-size: 0.85em; color: #f9e2af;">💡 ${opt.reasons.join(", ")}</div>
            `;
            reasonsList.appendChild(li);
        });

    } else if (result.verdict) {
        // --- MODO CAPTURA ---
        recommendationText.innerHTML = `<strong style="color:${result.color}">${result.verdict}</strong>`;
        resultArea.style.borderLeftColor = result.color === 'green' ? '#a6e3a1' : '#f38ba8';
        result.reasons.forEach(r => {
            const li = document.createElement('li'); li.textContent = r; reasonsList.appendChild(li);
        });

    } else {
        // --- MODO COMBATE ---
        recommendationText.innerHTML = `<strong>${result.summary}</strong>`;
        resultArea.style.borderLeftColor = '#89b4fa';
        const reasons = result.reasons || (result.analysis && result.analysis[0].reasons) || [];
        reasons.forEach(r => {
            const li = document.createElement('li'); li.textContent = r; reasonsList.appendChild(li);
        });
    }
}

// LISTENERS
btnAnalyze.addEventListener('click', () => handleAction('/analyze/combat'));
btnCatch.addEventListener('click', () => handleAction('/analyze/catch'));
btnItem.addEventListener('click', () => handleAction('/analyze/rewards', true)); // True indica que es modo Item

init();