from typing import List, Dict
from app.models.pokemon import Pokemon
from app.models.team import Team
from app.core.type_chart import get_effectiveness
from app.core.rules import check_ability_immunity


def analyze_spped_matchup(my_speed_base: int, enemy_speed_base: int) -> dict:
    """
        Analiza la velocidad con un margen de seguridad por culpa de los IVs/Naturalezas
    """ 

    diff = my_speed_base - enemy_speed_base

    SAFE_MARGIN = 15

    if diff >= SAFE_MARGIN:
        return {
            "score": 20,
            "desc": "Muy probable que ataques primero (Velocidad Segura)"
        }
    elif diff > 0:
        return {
            "score": 5,
            "desc": "ZONA DE RIESGO: Deberías ser más rápido, pero cuidado con sus IVs/Naturaleza."
        }
    elif diff == 0:
        return {
            "score": -5,
            "desc": "SPEED TIE: Misma velocidad base. Es una moneda al aire."
        }
    elif diff > -SAFE_MARGIN:
        return {
            "score": -10,
            "desc": "Probablemente seas más lento (Cerca, pero arriesgado)"
        }
    else:
        return {
            "score": -20,
            "desc": "Eres mucho más lento. Recibirás el golpe antes."
        }
    

def analyze_combat_matchup(team: Team, enemy: Pokemon) -> Dict:
    """
        Analiza que Pokemon de tu equipo es la mejor opcion conra el enemigo actual
    """
    recomendations = []

    for member in team.members:
        score = 0
        reasons = []

        # Calculamos si alguno de mis tipos pega fuerte al enemigo
        max_offensive_mult = 0.0
        best_attack_type = ""

        ability_blocked = False

        for my_type in member.types:
            if check_ability_inmunity(my_type, enemy.abilities):
                eff = 0.0
                ability_blocked = True
            else:
                eff = get_effectiveness(my_type, enemy.types)

            if eff > max_offensive_mult:
                max_offensive_mult = eff
                best_attack_type = my_type

        # Puntuación Ofensiva
        if ability_blocked and max_offensive_mult == 0.0:
            score -= 100
            reasons.append(f"¡CUIDADO! Su habilidad bloquea tus ataques de tipo {best_attack_type or 'principal'}")
        elif max_offensive_mult >= 2.0:
            score += 50
            reasons.append(f"Tu tipo {best_attack_type} es súper eficaz (x{max_offensive_mult})")
        elif max_offensive_mult == 0.0:
            score -= 50
            reasons.append(f"Tus ataques no le afectan (Inmunidad de Tipo)")
        elif max_offensive_mult <= 0.5:
            score -= 30
            reasons.append("Tus ataques no serán muy efectivos")

        
        # Calculamos si el enemigo me pega fuerte a mi
        max_defensive_mult = 0.0
        saved_by_ability = False

        for enemy_type in enemy.types:
            if check_ability_inmunity(enemy_type, member.abilities):
                eff = 0.0
                saved_by_ability = True
            else:
                eff = get_effectiveness(enemy_type, member.types)

            if eff > max_defensive_mult:
                max_defensive_mult = eff


       # Puntuación Defensiva
        if saved_by_ability and max_defensive_mult == 0.0:
            score += 150 # ¡Esto es buenísimo!
            reasons.append(f"✨ Tu habilidad te hace INMUNE a sus ataques de tipo {enemy_type}")
        elif max_defensive_mult >= 2.0:
            score -= 40
            reasons.append(f"Cuidado: Es eficaz contra ti (x{max_defensive_mult})")
        elif max_defensive_mult <= 0.5:
            score += 30
            reasons.append("Resistes sus ataques")
        elif max_defensive_mult == 0.0:
            score += 100
            reasons.append("¡Eres inmune a sus ataques por Tipo!")

        
        # Velocidad
        speed_analysis = analyze_spped_matchup(member.speed, enemy.speed)
        score += speed_analysis['score']
        reasons.append(speed_analysis['desc'])

        if max_defensive_mult >= 2.0 and speed_analysis["score"] < 0:
            score -= 50
            reasons.append("PELIGRO CRÍTICO: Lento y débil = Muerte probable")
        
        
        recomendations.append({
            "pokemon": member.name,
            "score": score,
            "reasons": reasons,
            "sprite": member.sprite # Para frontend
        })

    
    # Ordenmoas las recomendaciones de mejor a menor score
    recomendations.sort(key=lambda x: x["score"], reverse = True)

    best_pick = recomendations[0]

    return {
        "best_pokemon": best_pick["pokemon"],
        "analysis": recomendations,
        "summary": f"Usa a {best_pick['pokemon']}. {best_pick['reasons'][0]}."
    }


def analyze_catch_potential(team: Team, wild_pokemon: Pokemon) -> Dict:
    """
        Analiza si deberias capturar un Pokemon basandose en lo que le falta al equipo
    """
    score = 0
    reasons = []

    # Recopilamos todos los tipos que ya tenemos en el equipo
    existing_types = set()
    for member in team.members:
        for t in member.types:
            existing_types.add(t)

    # Miramos los tipos del pokemos salvaje
    new_types_count = 0
    for wild_type in wild_pokemon.types:
        if wild_type not in existing_types:
            score += 40
            reasons.append(f"Aporta el tipo {wild_type}")
            new_types_count += 1
        else:
            score -= 10
            reasons.append(f"Ya tienes el tipo {wild_type}")

    
    # Analisis de rol
    same_role_count = sum(1 for p in team.members if p.role == wild_pokemon.role)

    if same_role_count == 0:
        score += 20
        reasons.append(f"Necesitas un {wild_pokemon.role}")
    elif same_role_count >= 2:
        score -= 20
        reasons.append(f"Ya tienes demasiados {wild_pokemon.role}s")

    
    # Recomendacion final
    if score >= 40:
        verdict = "CAPTURA RECOMENDADA!"
        color = "green"
    elif score > 0:
        verdict = "Opcion decente"
        color = "orange"
    else:
        verdict = "No lo necesitas"
        color = "red"

    return {
        "score": score,
        "verdict": verdict,
        "color": color,
        "reasons": reasons,
        "summary": f"{verdict}. {reasons[0] if reasons else ''}"
    }

        
