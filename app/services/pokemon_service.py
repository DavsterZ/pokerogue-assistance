import json
import os
from app.models.pokemon import Pokemon


DB_PATH = "app/data/pokemon_db.json"


def get_pokemon(name: str) -> Pokemon:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("La base de datos de Pokémon no se encontró.")
    
    with open("app/data/pokemon_db.json") as f:
        POKEMON_DB = json.load(f)

    data = POKEMON_DB.get(name.lower())

    if not data:
        raise ValueError(f"Pokémon '{name}' no encontrado en la base de datos.")
    
    # Al pasar data, Pydantic usara los alias automaticamente
    return Pokemon(**data)