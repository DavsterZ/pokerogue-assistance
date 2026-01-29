import json
from app.models.pokemon import Pokemon


with open("app/data/pokemon_db.json") as f:
    POKEMON_DB = json.load(f)


def get_pokemon(name: str) -> Pokemon:
    data = POKEMON_DB.get(name.lower())
    if not data:
        raise ValueError(f"Pokémon '{name}' no encontrado en la base de datos.")
    return Pokemon(name=name, **data)