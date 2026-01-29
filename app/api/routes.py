from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.team import Team
from app.models.pokemon import Pokemon
from app.core.decision_engine import analyze_combat_matchup
from app.services.pokemon_service import POKEMON_DB


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
