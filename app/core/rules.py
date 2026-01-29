# Diccionario de Inmunidades por Habilidad
# Clave: Nombre de la habilidad
# Valor: Lista de tipos a los que se vuelve inmune


ABILITY_INMUNITIES = {
    # Tierra
    "levitate": ["ground"],
    "earh-eater": ["gorund"],

    # Fuego
    "flash-fire": ["fire"],
    "well-baked-body": ["fire"],

    # Electricidad
    "volt-absorb": ["electric"],
    "lightning-rod": ["electric"],
    "motor-drive": ["electric"],

    # Agua
    "water-absorb": ["water"],
    "stom-drain": ["water"],
    "dry-skin": ["water"],

    # Planta
    "sap-sipper": ["grass"],
}


def check_ability_inmunity(attack_type: str, defender_abilities: list[str]) -> bool:
    """
        Devuelve True si el defensor tiene una habilidad que le hace inmune 
        al tipo del ataque
    """

    attack_type = attack_type.lower()

    for ability in defender_abilities:
        # Buscamos si la habilidad esta en nuestra lista de inmunidades
        if ability in ABILITY_INMUNITIES:
            if attack_type in ABILITY_INMUNITIES[ability]:
                return True
            
    return False