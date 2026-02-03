import json
import os

ITEMS_FILE = "app/data/items_db.json"
TMS_FILE = "app/data/tms_db.json"

class ItemService:
    def __init__(self):
        self.items_db = {}
        self.tms_db = {}
        self.unified_list = []
        self.load_data()

    def load_data(self):
        # Cargar JSONs
        if os.path.exists(ITEMS_FILE):
            with open(ITEMS_FILE, 'r', encoding='utf-8') as f: self.items_db = json.load(f)
        if os.path.exists(TMS_FILE):
            with open(TMS_FILE, 'r', encoding='utf-8') as f: self.tms_db = json.load(f)

        # Crear lista unificada
        self.unified_list = []
        for item_id, data in self.items_db.items():
            self.unified_list.append({"id": item_id, "name": data["name"], "tier": data.get("tier", "Common")})
        for tm_id, data in self.tms_db.items():
            self.unified_list.append({"id": tm_id, "name": data["name"], "tier": data.get("rarity", "Common")})
        
        self.unified_list.sort(key=lambda x: x["name"])

    def get_all_names(self): return self.unified_list

    def get_item_details(self, item_id):
        if item_id in self.items_db: return self.items_db[item_id]
        if item_id in self.tms_db: return self.tms_db[item_id]
        return None

    def evaluate_reward_options(self, team, options_ids):
        ranked_options = []
        
        print(f"\n--- Analizando: {options_ids} ---") # Debug

        for item_id in options_ids:
            data = self.get_item_details(item_id)
            if not data: continue

            score = 10 # Puntuación base para evitar ceros
            reasons = []
            
            tier = str(data.get("tier", "Common")).lower()
            cat = str(data.get("category", "misc")).lower()
            name = data.get("name", "")

            # 1. RAREZA
            if "master" in tier: score += 1000; reasons.append(f"🌟 TIER MASTER: {data.get("description", "Hola")}")
            elif "rogue" in tier: score += 500; reasons.append(f"🔴 Tier Rogue: {data.get("description", "Hola")}")
            elif "ultra" in tier: score += 150; reasons.append(f"🟡 Tier Ultra: {data.get("description", "Hola")}")
            elif "great" in tier: score += 50; reasons.append(f"🔵 Tier Great: {data.get("description", "Hola")}")

            # 2. CATEGORÍA
            if "mint" in name.lower() or cat == "mint":
                score += 60; reasons.append(f"🌿 Cambia Naturaleza: {data.get("description", "Hola")}")
            elif cat == "evolution":
                score += 70; reasons.append(f"🧬 Evolutivo: {data.get("description", "Hola")}")
            elif cat == "held-item":
                score += 40; reasons.append(f"🎒 Equipable (Potencia Stats/Tipos): {data.get("description", "Hola")}")
            elif cat == "perm-buff":
                score += 35; reasons.append(f"💪 Vitamina Permanente: {data.get("description", "Hola")}")
            elif cat == "tm":
                score += 25; reasons.append(f"💿 Máquina Técnica: {data.get("description", "Hola")}")
            elif cat == "key-item":
                score += 300; reasons.append(f"🔑 Objeto Clave (Muy importante): {data.get("description", "Hola")}")

            # Depuración en consola
            print(f" > {name} | Cat: {cat} | Tier: {tier} | Score: {score}")

            ranked_options.append({
                "id": item_id, "name": name, "score": score, "reasons": reasons, "data": data
            })

        # Ordenar (Mayor puntuación primero)
        ranked_options.sort(key=lambda x: x["score"], reverse=True)
        
        if not ranked_options: return {"summary": "Error al leer objetos", "analysis": []}

        best = ranked_options[0]
        summary = f"🏆 Elige: {best['name']}"
        
        return {"best_option": best, "analysis": ranked_options, "summary": summary}

item_service = ItemService()