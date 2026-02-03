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
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace('\n', ' ').strip()
    return text

def determine_category(name, desc):
    name_lower = name.lower()
    desc_lower = desc.lower()

    # --- CATEGORÍAS PRIORITARIAS ---
    if "voucher" in name_lower: return "voucher"
    
    # Pokéballs
    if "master ball" in name_lower: return "pokeball" # Forzamos Master
    if "rogue ball" in name_lower: return "pokeball"
    if "ball" in name_lower and "up" not in name_lower: return "pokeball"

    # TMs / HMs
    if re.search(r'\b(tm|hm)\d+', name_lower) or "machine" in name_lower: return "tm"

    # Bayas
    if "berry" in name_lower: return "berry"

    # Objetos de Stat Temporales (X Items)
    if name_lower.startswith("x ") or "dire hit" in name_lower or "guard spec" in name_lower: 
        return "temp-buff"

    # Curación y Estado
    if "revive" in name_lower: return "revive"
    if "potion" in name_lower or "milk" in name_lower or "soda" in name_lower or "lemonade" in name_lower or "water" in name_lower and "fresh" in name_lower: return "healing"
    if "heal" in name_lower or "restore" in desc_lower: return "healing"
    if "ether" in name_lower or "elixir" in name_lower: return "pp-restore"
    if "status" in desc_lower or "cure" in desc_lower or "full heal" in name_lower: return "status-cure"

    # Vitaminas (Permanentes)
    if "calcium" in name_lower or "protein" in name_lower or "carbos" in name_lower or "zinc" in name_lower or "iron" in name_lower or "hp up" in name_lower or "vitamin" in name_lower or "pp up" in name_lower: 
        return "perm-buff"

    # Mentas
    if "mint" in name_lower: return "mint"

    # Evolutivos
    if "stone" in name_lower or "link" in name_lower or "scale" in name_lower or "upgrade" in name_lower or "wire" in name_lower or "electirizer" in name_lower or "magmarizer" in name_lower or "protector" in name_lower or "reaper cloth" in name_lower or "dubious disc" in name_lower: 
        return "evolution"

    # --- OBJETOS EQUIPABLES (HELD ITEMS) ---
    # Aquí es donde fallaba el Black Belt. He añadido muchas más palabras clave.
    held_keywords = [
        "belt", "glasses", "specs", "scarf", "band", "lens", "scope", "fang", 
        "claw", "beak", "spoon", "charcoal", "miracle seed", "magnet", 
        "sharp", "coat", "powder", "rock", "sand", "herb", "grip", "metronome", 
        "shell", "bell", "remains", "sludge", "orb", "plate", "drive", "incense"
    ]
    
    if any(k in name_lower for k in held_keywords):
        return "held-item"
    
    if "boosts" in desc_lower or "power" in desc_lower:
        return "held-item"

    # Objetos Clave
    if "map" in name_lower or "case" in name_lower or "ticket" in name_lower or "charm" in name_lower: 
        return "key-item"
    
    return "misc"

def scrape_smart_fixed():
    print("🤖 Iniciando Scraper Mejorado...")
    
    chrome_options = Options()
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
        
        print("\n🛑 RESUELVE EL CAPTCHA SI APARECE Y PULSA ENTER AQUÍ.")
        input("👉 Pulsa ENTER cuando veas la Wiki... ")

        # Abrir desplegables
        toggles = driver.find_elements(By.CSS_SELECTOR, "a[data-toggle='collapse']")
        for toggle in toggles:
            try:
                driver.execute_script("arguments[0].click();", toggle)
                time.sleep(0.05)
            except: pass
        time.sleep(3)

        # Procesar
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = soup.find_all('table')

        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue

            headers = rows[0].find_all(['th', 'td'])
            header_texts = [h.get_text(strip=True).lower() for h in headers]
            
            name_idx = -1
            desc_idx = -1
            tier_idx = -1

            for i, text in enumerate(header_texts):
                if "item" in text or "name" in text: name_idx = i
                if "effect" in text or "description" in text or "summary" in text or "evolves" in text: desc_idx = i
                if "rarity" in text or "tier" in text: tier_idx = i

            # Fallback para tablas sin cabecera clara
            if name_idx == -1 and len(header_texts) >= 2: name_idx = 0

            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                if not cols: continue

                offset = 0
                if len(cols) > len(header_texts): offset = len(cols) - len(header_texts)
                
                current_name_idx = name_idx + offset
                current_desc_idx = desc_idx + offset if desc_idx != -1 else -1
                current_tier_idx = tier_idx + offset if tier_idx != -1 else -1

                if current_name_idx >= len(cols): continue

                raw_name = cols[current_name_idx].get_text(strip=True)
                name = clean_text(raw_name)

                if not name or len(name) < 2 or name.lower() == "item": continue

                description = "Sin descripción"
                if current_desc_idx != -1 and current_desc_idx < len(cols):
                    description = clean_text(cols[current_desc_idx].get_text(strip=True))
                
                tier = "Common" # Valor por defecto si no hay columna
                if current_tier_idx != -1 and current_tier_idx < len(cols):
                    read_tier = clean_text(cols[current_tier_idx].get_text(strip=True))
                    if read_tier: tier = read_tier
                
                # PARCHE MANUAL: Si es Master Ball y no detectó tier, poner Master
                if "Master Ball" in name: tier = "Master"
                if "Rogue Ball" in name: tier = "Rogue"

                item_id = name.lower().replace(" ", "-").replace("'", "").replace(".", "").replace("é", "e")
                category = determine_category(name, description)

                items_db[item_id] = {
                    "name": name,
                    "description": description,
                    "tier": tier,
                    "category": category
                }

        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(items_db, f, indent=2, ensure_ascii=False)

        print(f"✅ ¡Base de datos actualizada! {len(items_db)} objetos guardados.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_smart_fixed()