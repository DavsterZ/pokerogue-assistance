from pydantic import BaseModel, Field
from typing import List, Optional


class Pokemon(BaseModel):
    name: str
    types: List[str]
    # Base stats
    hp: int
    attack: int
    defense: int
    speed: int

    # Stats Speciales
    sp_attack: int = Field(alias="special_attack")
    sp_defense: int = Field(alias="special_defense")

    # Informacion util para logica avanzada
    role: str = "balanced"       # sweeper, tank, support, etc.
    cost: int = 1                # costo inicial en PokeRogue (1-10)
    abilities: List[str] = []    # Habilidades posibles
    sprite: Optional[str] = None

    # Campo para guardar el estado actual en una run
    current_hp_percentage: Optional[float] = 100.0

    class Config:
        populate_by_name = True

