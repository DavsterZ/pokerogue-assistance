from typing import List, Dict
from app.models.pokemon import Pokemon
from app.models.team import Team
from app.core.type_chart import get_effectiveness


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
        for my_type in member.types:
            eff = get_effectiveness(my_type, enemy.types)
            if eff > max_offensive_mult:
                max_offensive_mult = eff
        
        if max_offensive_mult >= 2.0:
            score += 50
            reasons.append(f"Tu tipo {my_type} es super eficaz contra {enemy.name} (x{max_offensive_mult})")
        elif max_offensive_mult <= 0.5:
            score -= 30
            reasons.append("Tus ataques no seran muy efectivos contra este enemigo")

        
        # Calculamos si el enemigo me pega fuerte a mi
        max_defensive_mult = 0.0
        for enemy_type in enemy.types:
            eff = get_effectiveness(enemy_type, member.types)
            if eff > max_defensive_mult:
                max_defensive_mult = eff

        if max_defensive_mult >= 2.0:
            score -= 40
            reasons.append(f"Cuidado: Es eficaz contra ti (x{max_defensive_mult})")
        elif max_defensive_mult <= 0.5:
            score += 30
            reasons.append("Resistes sus ataques")
        elif max_defensive_mult == 0.0:
            score += 100        # Inmunidad es oro
            reasons.append("Eres inmune a sus ataques!")

        
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
            # "offensive_multiplier": max_offensive_mult,
            # "defensive_multiplier": max_defensive_mult,
            "reasons": reasons
        })

    
    # Ordenmoas las recomendaciones de mejor a menor score
    recomendations.sort(key=lambda x: x["score"], reverse = True)

    best_pick = recomendations[0]

    return {
        "best_pokemon": best_pick["pokemon"],
        "analysis": recomendations,
        "summary": f"Usa a {best_pick['pokemon']}. {', '.join(best_pick['reasons'][:2])}"
    }

        
