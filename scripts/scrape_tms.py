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

TARGET_URL = "https://wiki.pokerogue.net/items:tms"
OUTPUT_FILE = "app/data/tms_db.json"

def clean_text(text):
    if not text: return ""
    text = re.sub(r'\[.*?\]', '', text)
    text = text.replace('\n', ' ').strip()
    return text

def scrape_tms_visual():
    print("💿 INICIANDO SCRAPER DE TMs (Basado en Captura)...")
    
    chrome_options = Options()
    # Modo "Humano" para pasar Cloudflare
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--window-size=1280,1024")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    tms_db = {}
    
    try:
        print(f"🌍 Navegando a {TARGET_URL}...")
        driver.get(TARGET_URL)
        
        # --- PAUSA CLOUDFLARE ---
        print("\n" + "!"*60)
        print("🛑 SI SALE CLOUDFLARE, HAZ CLIC EN 'SOY HUMANO'.")
        print("Espera a ver la tabla de 'TM Rarity / TM### / Move'...")
        input("👉 Pulsa ENTER aquí cuando la veas... ")
        print("!"*60 + "\n")

        # --- LECTURA ---
        print("📖 Leyendo datos...")
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"📊 Tablas encontradas: {len(tables)}")

        count_total = 0

        for table in tables:
            rows = table.find_all('tr')
            if not rows: continue

            # 1. VALIDAR SI ES LA TABLA CORRECTA
            # Buscamos las cabeceras exactas de tu captura
            headers_row = rows[0]
            headers_text = [h.get_text(strip=True).lower() for h in headers_row.find_all(['th', 'td'])]
            
            # Tu tabla tiene: [rarity, tm###, move, type, description]
            # Verificamos si tiene "tm###" y "move" para estar seguros
            is_tm_table = False
            for h in headers_text:
                if "tm#" in h or "tm###" in h: is_tm_table = True
                if "move" in h and "description" not in h: is_tm_table = True
            
            if not is_tm_table:
                continue # Saltamos tablas que no sean esta

            # 2. PROCESAR FILAS
            for row in rows[1:]:
                cols = row.find_all(['td', 'th'])
                # La tabla de tu captura tiene 5 columnas
                if len(cols) < 5: continue
                
                # --- MAPEO EXACTO SEGÚN TU CAPTURA ---
                # Col 0: Rarity (Common)
                # Col 1: TM### (TM006)
                # Col 2: Move (Swords Dance)
                # Col 3: Type (IMAGEN)
                # Col 4: Description
                
                rarity = clean_text(cols[0].get_text(strip=True))
                tm_num = clean_text(cols[1].get_text(strip=True))
                move_name = clean_text(cols[2].get_text(strip=True))
                description = clean_text(cols[4].get_text(strip=True))
                
                # EXTRACCIÓN ESPECIAL DEL TIPO (IMAGEN)
                move_type = "Normal" # Por defecto
                type_cell = cols[3]
                img = type_cell.find('img')
                if img:
                    # Intentamos sacar el tipo del 'alt', 'title' o del nombre del archivo src
                    possible_type = img.get('alt') or img.get('title')
                    if not possible_type:
                        src = img.get('src', '')
                        # Si el archivo es "type_fire.png", sacamos "fire"
                        match = re.search(r'type_(\w+)', src, re.IGNORECASE)
                        if match: possible_type = match.group(1)
                    
                    if possible_type:
                        move_type = clean_text(possible_type).capitalize()
                else:
                    # A veces es solo texto
                    text_type = clean_text(type_cell.get_text(strip=True))
                    if text_type: move_type = text_type

                # FILTROS
                if not move_name or move_name.lower() == "move": continue

                # GENERAR ID
                tm_id = f"tm-{move_name.lower().replace(' ', '-')}"

                tms_db[tm_id] = {
                    "name": f"{tm_num}: {move_name}", # Ej: "TM006: Swords Dance"
                    "move_name": move_name,
                    "tm_number": tm_num,
                    "type": move_type,
                    "rarity": rarity,
                    "description": description,
                    "category": "tm" # Categoría forzada
                }
                count_total += 1

        # GUARDAR
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(tms_db, f, indent=2, ensure_ascii=False)

        print(f"\n✨ ¡ÉXITO! Base de datos de MTs generada.")
        print(f"💿 Movimientos guardados: {count_total}")
        print(f"📂 Archivo: {OUTPUT_FILE}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_tms_visual()