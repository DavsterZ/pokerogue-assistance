from pydantic import BaseModel
from typing import List

from app.models.pokemon import Pokemon


class Team(BaseModel):
    members: List[Pokemon]