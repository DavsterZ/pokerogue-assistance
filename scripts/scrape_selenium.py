import time
import json
import os
import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

TARGET_URL = "https://wiki.pokerogue.net/gameplay:items"
OUTPUT_FILE = "app/data/items_db.json"

def clean_text(text):
    if not text: return ""
    # Eliminar referencias [1], saltos de línea y espacios extra
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace('\n', ' ').strip()
    return text

def determine_category(name, desc):
    name_lower = name.lower()
    desc_lower = desc.lower()

    # Prioridades Claras
    if "voucher" in name_lower: return "voucher"
    if "ball" in name_lower or "master" in name_lower: return "pokeball"
    if re.search(r'\b(tm|hm)\d+', name_lower) or "machine" in name_lower or "tm " in name_lower: return "tm"
    if "berry" in name_lower: return "berry"
    if "tera shard" in name_lower: return "tera-shard"
    
    # Objetos de Stat (Species Stat Boosters)
    # Detectamos palabras clave como "Doubles", "Latia", "Pikachu", "Light Ball"
    if "light ball" in name_lower or "stick" in name_lower or "club" in name_lower or "powder" in name_lower or "dew" in name_lower or "tooth" in name_lower or "scale" in name_lower:
        return "held-item"

    if name_lower.startswith("x ") or "dire hit" in name_lower or "guard spec" in name_lower: return "temp-buff"
    if "revive" in name_lower: return "revive"
    if "heal" in desc_lower or "restore" in desc_lower or "potion" in name_lower or "milk" in name_lower: return "healing"
    if "pp" in desc_lower or "ether" in name_lower or "elixir" in name_lower: return "pp-restore"
    if "status" in desc_lower or "cure" in desc_lower or "full heal" in name_lower: return "status-cure"
    if "calcium" in name_lower or "protein" in name_lower or "carbos" in name_lower or "zinc" in name_lower or "iron" in name_lower or "hp up" in name_lower or "vitamin" in name_lower: return "perm-buff"
    if "mint" in name_lower: return "mint"
    if "stone" in name_lower or "link" in name_lower or "scale" in name_lower or "upgrade" in name_lower or "wire" in name_lower: return "evolution"
    if "charm" in name_lower or "lens" in name_lower or "band" in name_lower or "scarf" in name_lower or "glasses" in name_lower or "seed" in name_lower or "beak" in name_lower or "spoon" in name_lower or "fang" in name_lower or "coat" in name_lower: return "held-item"
    if "map" in name_lower or "case" in name_lower or "ticket" in name_lower: return "key-item"
    
    return "misc"

def scrape_smart():
    print("🤖 Iniciando navegador...")
    
    chrome_options = Options()
    # Desactivar automatización para evitar bloqueos
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1280,1024")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    items_db = {}
    
    try:
        print(f"🌍 Entrando en {TARGET_URL}...")
        driver.get(TARGET_URL)
        
        # --- PARADA CLOUDFLARE ---
        print("\n" + "!"*60)
        print("🛑 SI VES CLOUDFLARE, RESUÉLVELO AHORA.")
        print("Esperando a que cargues la página correctamente...")
        input("👉 Pulsa ENTER en esta terminal cuando veas la Wiki... ")
        print("!"*60 + "\n")

        # --- ABRIR DESPLEGABLES ---
        print("🔓 Buscando botones ocultos...")
        toggles = driver.find_elements(By.CSS_SELECTOR, "a[data-toggle='collapse']")
        
        for toggle in toggles:
            try:
                driver.execute_script("arguments[0].click();", toggle)
                time.sleep(0.05)
            except: pass
        
        print("⏳ Esperando 3 segundos a que se despliegue todo...")
        time.sleep(3)

        # --- LECTURA DINÁMICA ---
        print("📖 Analizando estructura de las tablas...")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"📊 Tablas encontradas: {len(tables)}")

        count_total = 0

        for t_idx, table in enumerate(tables):
            rows = table.find_all('tr')
            if not rows: continue

            # 1. ANALIZAR CABECERAS PARA ENCONTRAR INDICES
            headers = rows[0].find_all(['th', 'td'])
            header_texts = [h.get_text(strip=True).lower() for h in headers]
            
            # Buscamos en qué posición está cada columna clave
            name_idx = -1
            desc_idx = -1
            tier_idx = -1

            for i, text in enumerate(header_texts):
                if "item" in text or "name" in text: name_idx = i
                if "effect" in text or "description" in text or "summary" in text or "evolves" in text: desc_idx = i
                if "rarity" in text or "tier" in text: tier_idx = i

            # Si no encontramos cabecera de nombre, saltamos la tabla (probablemente no es de items)
            if name_idx == -1 and len(header_texts) > 1:
                # Intento desesperado: Asumir col 0 o 1
                name_idx = 0 

            # 2. PROCESAR FILAS
            for r_idx, row in enumerate(rows[1:]):
                try:
                    cols = row.find_all(['td', 'th'])
                    if not cols: continue

                    # CALCULAR DESFASE (OFFSET)
                    # A veces la fila de datos tiene una columna extra (la imagen) que no está en la cabecera
                    # Ejemplo: Cabecera [Item, Effect] (2) - Datos [Img, Potion, Heals] (3)
                    offset = 0
                    if len(cols) > len(header_texts):
                        offset = len(cols) - len(header_texts)
                    
                    # Índices ajustados
                    current_name_idx = name_idx + offset
                    current_desc_idx = desc_idx + offset if desc_idx != -1 else -1
                    current_tier_idx = tier_idx + offset if tier_idx != -1 else -1

                    # Extraer datos con seguridad
                    if current_name_idx >= len(cols): continue # Algo va mal con esta fila

                    raw_name = cols[current_name_idx].get_text(strip=True)
                    name = clean_text(raw_name)

                    # Filtros de basura
                    if not name or len(name) < 2 or name.lower() == "item": continue

                    description = "Sin descripción"
                    if current_desc_idx != -1 and current_desc_idx < len(cols):
                        description = clean_text(cols[current_desc_idx].get_text(strip=True))
                    
                    tier = "Unknown"
                    if current_tier_idx != -1 and current_tier_idx < len(cols):
                        tier = clean_text(cols[current_tier_idx].get_text(strip=True))

                    # Guardar
                    item_id = name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("é", "e")
                    category = determine_category(name, description)

                    items_db[item_id] = {
                        "name": name,
                        "description": description,
                        "tier": tier,
                        "category": category
                    }
                    count_total += 1
                
                except Exception as e:
                    # Si falla una fila, la ignoramos y seguimos
                    # print(f"Error en fila {r_idx} tabla {t_idx}: {e}")
                    continue

        # Guardar JSON
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(items_db, f, indent=2, ensure_ascii=False)

        print(f"\n✨ ¡SCRAPING COMPLETADO!")
        print(f"📦 Se han guardado {count_total} objetos únicos.")
        print(f"📂 Archivo: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error fatal: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_smart()