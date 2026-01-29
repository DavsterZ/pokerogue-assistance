import json
import os
from app.models.pokemon import Pokemon


DB_PATH = "app/data/pokemon_db.json"


def _load_db():
    if not os.path.exists(DB_PATH):
        return {}
    
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
    

POKEMON_DB = _load_db()


def get_pokemon(name: str) -> Pokemon:
    data = POKEMON_DB.get(name.lower())

    if not data:
        if not POKEMON_DB:
            raise FileNotFoundError("La base de datos de Pokémon no se ha cargado correctamente.")
        raise ValueError(f"Pokémon '{name}' no encontrado en la base de datos.")
    
    # Al pasar data, Pydantic usara los alias automaticamente
    return Pokemon(**data)