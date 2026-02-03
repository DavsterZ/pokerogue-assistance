const API_URL = "http://127.0.0.1:8000";

// REFERENCIAS DOM
const teamContainer = document.getElementById('team-container');
const btnAddMember = document.getElementById('add-member-btn');
const teamCountSpan = document.getElementById('team-count');
const enemySelect = document.getElementById('enemy-pokemon-select');

const btnAnalyze = document.getElementById('analyze-btn');
const btnCatch = document.getElementById('catch-btn');
const btnItem = document.getElementById('item-btn');

const rewardSelects = [
    document.getElementById('reward-1'),
    document.getElementById('reward-2'),
    document.getElementById('reward-3')
];

const resultArea = document.getElementById('result-area');
const recommendationText = document.getElementById('recommendation-text');
const reasonsList = document.getElementById('reasons-list');

// Variables Globales
let allPokemonNames = [];
let allItemNames = [];
const pokemonCache = {};


async function init() {
    try {
        const [respPoke, respItems] = await Promise.all([
            fetch(`${API_URL}/pokemon/names`),
            fetch(`${API_URL}/items/list`)
        ]);

        allPokemonNames = await respPoke.json();
        allItemNames = await respItems.json();

        fillSelect(enemySelect, allPokemonNames);
        rewardSelects.forEach(sel => fillItemSelect(sel));

        // Cargar estado guardado
        loadState();

        // Listeners globales
        enemySelect.addEventListener('change', () => {
            updatePreview(enemySelect, 'enemy-pokemon-preview');
            saveState();
        });
        
        rewardSelects.forEach(sel => {
            sel.addEventListener('change', saveState);
        });

        updateCount();

    } catch (error) {
        console.error("Error conectando con el servidor:", error);
    }
}


function saveState() {
    const currentTeam = [];
    document.querySelectorAll('.team-select').forEach(sel => {
        currentTeam.push(sel.value);
    });

    const state = {
        team: currentTeam,
        enemy: enemySelect.value,
        rewards: rewardSelects.map(s => s.value)
    };

    localStorage.setItem('pokerogue_save', JSON.stringify(state));
}

function loadState() {
    const savedJSON = localStorage.getItem('pokerogue_save');
    if (!savedJSON) {
        // Estado inicial por defecto
        teamContainer.innerHTML = '';
        createSlotHTML(""); 
        return;
    }

    try {
        const state = JSON.parse(savedJSON);

        if (state.enemy) {
            enemySelect.value = state.enemy;
            updatePreview(enemySelect, 'enemy-pokemon-preview');
        }

        if (state.rewards) {
            rewardSelects.forEach((sel, i) => {
                if(state.rewards[i]) sel.value = state.rewards[i];
            });
        }

        teamContainer.innerHTML = ''; 
        if (state.team && state.team.length > 0) {
            state.team.forEach(poke => createSlotHTML(poke));
        } else {
            createSlotHTML("");
        }

    } catch (e) {
        // En caso de error, reseteamos a un slot vacío
        teamContainer.innerHTML = '';
        createSlotHTML("");
    }
}


function createSlotHTML(preselectedValue = "") {
    const id = `slot-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
    
    const slotDiv = document.createElement('div');
    slotDiv.className = 'pokemon-slot';
    slotDiv.id = id;
    
    slotDiv.innerHTML = `
        <select class="team-select"></select>
        <div class="mini-preview">?</div>
        <button class="remove-btn">×</button>
    `;

    teamContainer.appendChild(slotDiv);

    const select = slotDiv.querySelector('select');
    const preview = slotDiv.querySelector('.mini-preview');
    const btnRemove = slotDiv.querySelector('.remove-btn');

    fillSelect(select, allPokemonNames);

    if (preselectedValue) {
        select.value = preselectedValue;
        updatePreview(select, null, preview);
    }

    select.addEventListener('change', () => {
        updatePreview(select, null, preview);
        saveState();
    });

    btnRemove.addEventListener('click', () => {
        removeSlot(id);
    });
}

function removeSlot(id) {
    const slots = document.querySelectorAll('.pokemon-slot');
    if (slots.length <= 1) {
        const slot = document.getElementById(id);
        slot.querySelector('select').value = "";
        slot.querySelector('.mini-preview').innerHTML = "?";
        saveState();
        return;
    }
    document.getElementById(id).remove();
    saveState();
    updateCount();
}

function updateCount() {
    const count = document.querySelectorAll('.pokemon-slot').length;
    if (teamCountSpan) teamCountSpan.textContent = count;
}


function fillSelect(selectElement, dataList) {
    const val = selectElement.value;
    const fragment = document.createDocumentFragment();
    
    const def = document.createElement('option');
    def.value = ""; def.textContent = "Elige..."; def.disabled = true;
    if(!val) def.selected = true;
    fragment.appendChild(def);

    dataList.forEach(name => {
        const opt = document.createElement('option');
        opt.value = name; opt.textContent = name.charAt(0).toUpperCase() + name.slice(1);
        fragment.appendChild(opt);
    });
    
    selectElement.innerHTML = '';
    selectElement.appendChild(fragment);
    if(val) selectElement.value = val;
}

function fillItemSelect(selectElement) {
    const val = selectElement.value;
    selectElement.innerHTML = '<option value="" disabled selected>Opción...</option>';
    allItemNames.forEach(item => {
        const opt = document.createElement('option');
        opt.value = item.id;
        let label = item.name;
        if(item.tier && item.tier !== "Unknown" && item.tier !== "Common") label += ` [${item.tier}]`;
        opt.textContent = label;
        selectElement.appendChild(opt);
    });
    if(val) selectElement.value = val;
}

async function updatePreview(selectElement, previewId = null, previewElement = null) {
    const name = selectElement.value;
    const container = previewElement || document.getElementById(previewId);
    if (!name) return;

    container.innerHTML = '⏳';
    try {
        const data = await fetchPokemonData(name);
        container.innerHTML = data.sprite ? `<img src="${data.sprite}" style="height:100%">` : '?';
    } catch(e) { container.innerHTML = '❌'; }
}


async function fetchPokemonData(name) {
    if (pokemonCache[name]) return pokemonCache[name];
    const resp = await fetch(`${API_URL}/pokemon/${name}`);
    if (!resp.ok) throw new Error("Not found");
    const data = await resp.json();
    pokemonCache[name] = data;
    return data;
}

async function getTeamData() {
    const selects = document.querySelectorAll('.team-select');
    const membersData = [];
    for (const select of selects) {
        if (select.value) membersData.push(await fetchPokemonData(select.value));
    }
    return membersData;
}

async function handleAction(endpoint, isItemAnalysis = false) {
    const teamMembers = await getTeamData();
    if (!teamMembers.length) { alert("Tu equipo está vacío."); return; }
    let payload = {};

    if (isItemAnalysis) {
        const options = rewardSelects.map(s => s.value).filter(v => v);
        if (!options.length) { alert("Elige opciones."); return; }
        payload = { "my_team": { "members": teamMembers }, "options": options };
    } else {
        const enemyName = enemySelect.value;
        if (!enemyName) { alert("Falta enemigo."); return; }
        const enemyData = await fetchPokemonData(enemyName);
        payload = { "my_team": { "members": teamMembers }, "enemy_pokemon": enemyData };
    }

    try {
        const resp = await fetch(`${API_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const result = await resp.json();
        showResults(result, isItemAnalysis);
    } catch (e) { alert("Error de conexión con el Asistente."); }
}

function showResults(result, isItemAnalysis) {
    resultArea.classList.remove('hidden');
    reasonsList.innerHTML = '';

    if (isItemAnalysis) {
        resultArea.style.borderLeftColor = '#f9e2af';
        const bestItem = result.best_option;
        const bestDesc = bestItem.data.description || "Sin descripción.";
        
        recommendationText.innerHTML = `
            <div style="margin-bottom: 10px;">
                <strong style="font-size: 1.2em;">🏆 ${result.summary}</strong>
                <div style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 6px; margin-top: 5px; font-style: italic; color: #bac2de;">"${bestDesc}"</div>
            </div>`;
        
        result.analysis.forEach(opt => {
            const li = document.createElement('li');
            const desc = opt.data.description || "";
            li.style.marginBottom = "12px";
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
        recommendationText.innerHTML = `<strong style="color:${result.color}">${result.verdict}</strong>`;
        resultArea.style.borderLeftColor = result.color === 'green' ? '#a6e3a1' : '#f38ba8';
        result.reasons.forEach(r => {
            const li = document.createElement('li'); li.textContent = r; reasonsList.appendChild(li);
        });
    } else {
        recommendationText.innerHTML = `<strong>${result.summary}</strong>`;
        resultArea.style.borderLeftColor = '#89b4fa';
        const reasons = result.reasons || (result.analysis && result.analysis[0].reasons) || [];
        reasons.forEach(r => {
            const li = document.createElement('li'); li.textContent = r; reasonsList.appendChild(li);
        });
    }
}

// Listeners Botones
btnAddMember.addEventListener('click', () => {
    if (document.querySelectorAll('.pokemon-slot').length >= 6) { alert("Máximo 6."); return; }
    createSlotHTML("");
    saveState();
    updateCount();
});

btnAnalyze.addEventListener('click', () => handleAction('/analyze/combat'));
btnCatch.addEventListener('click', () => handleAction('/analyze/catch'));
btnItem.addEventListener('click', () => handleAction('/analyze/rewards', true));

// Arrancar
document.addEventListener('DOMContentLoaded', init);