import requests
import json
import os

# Configuration
POKEMON_COUNT = 151
OUTPUT_FILE = "app/data/pokemon_db.json"


def determine_role(stats):
    """
        Logica simple para asignar un rol basado en stats
    """

    speed = stats['speed']
    atk = max(stats['attack'], stats['special-attack'])
    defense = max(stats['defense'], stats['special-defense'])


    if speed > 90 and atk > 90:
        return "sweeper"    # Rapido y ofensivo
    elif defense > 90 and stats['hp'] > 80:
        return "tank"       # Resistente
    elif speed > 100:
        return "support"    # Rapido, para meter estados
    else:
        return "balanced"   # Balanceado
    

def fetch_pokemon_data():
    database = {}
    print(f"Iniciando descarga de datos de {POKEMON_COUNT} Pokemon...")

    for i in range(1, POKEMON_COUNT + 1):
        try:
            # Peticion a la PokeAPI
            url = f"https://pokeapi.co/api/v2/pokemon/{i}"
            response = requests.get(url)

            if response.status_code != 200:
                print(f"Error al descargar ID {i}")
                continue

            data = response.json()
            name = data['name']

            # Extraemos stats
            stats = {s['stat']['name']: s['base_stat'] for s in data['stats']}

            # Extraemos tipos
            types = [t['type']['name'] for t in data['types']]

            # Extraemos habilidades (solo nombres)
            abilities = [a['ability']['name'] for a in data['abilities']]

            # Extraemos Sprite
            sprite = data['sprites']['front_default']

            # Calculamos Rol
            role = determine_role(stats)


            # Construimos el objeto Pokemon
            # Lo ponemos a 1 por defecto y luego editamos
            pokemon_entry = {
                "name": name.capitalize(),
                "types": types,
                "hp": stats['hp'],
                "attack": stats['attack'],
                "defense": stats['defense'],
                "speed": stats['speed'],
                "special-attack": stats['special-attack'],
                "special-defense": stats['special-defense'],
                "role": role,
                "abilities": abilities,
                "sprite": sprite,
                "cost": 1
            }

            database[name] = pokemon_entry

            # Barra de progreso simple
            if i % 10 == 0:
                print(f"  - Descargados {i}/{POKEMON_COUNT} Pokemon")
            
        except Exception as e:
            print(f"Excepcion al procesar ID {i}: {e}")


    # Guardamos en fichero
    # Nos aseguramos que el directorio existe
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(database, f, indent=2)

    print(f"Datos guardados en {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_pokemon_data()
