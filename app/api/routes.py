from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.team import Team
from app.models.pokemon import Pokemon
from app.core.decision_engine import analyze_combat_matchup
from app.services.pokemon_service import POKEMON_DB
from app.services.pokemon_service import get_pokemon as service_get_pokemon


router = APIRouter()


# Estructura de la peticion que esperamos recibir
class CombatRequest(BaseModel):
    my_team: Team
    enemy_pokemon: Pokemon


@router.get("/pokemon/names")
def get_pokemon_names():
    """
        Devuelve una lista con todos los nombres de Pokemon disponibles.
        Util para rellenar menus en el frontend.
    """
    names = list(POKEMON_DB.keys())

    # Ordenamos alfabeticamente
    names.sort()
    return names;


@router.get("/pokemon/{name}")
def get_single_pokemon(name: str):
    """
        Deuelve los datos completos de un Pokemons dado su nombre.
    """
    try:
        return service_get_pokemon(name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze/combat")
def analyze_combat(request: CombatRequest):
    """
        Endpoint principal: Recibe tu equipo y el enemigo, y devuelve quien debe
        salir a pelear.
    """

    try:
        # Llamamos al cerebro
        result = analyze_combat_matchup(request.my_team, request.enemy_pokemon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/health")
def health_check():
    return {"status": "ok", "version": "0.1"}
