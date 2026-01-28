from typing import List, Dict
from app.models.pokemon import Pokemon
from app.models.team import Team
from app.core.type_chart import get_effectiveness


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

        
        # Matar antes de que te toquen es vital
        if member.speed > enemy.speed:
            score += 20
            reasons.append("Eres mas rapido")
        else:
            score -= 10
            reasons.append("Eres mas lento, recibiras daño antes de atacar")

        
        recomendations.append({
            "pokemon": member.name,
            "score": score,
            "offensive_multiplier": max_offensive_mult,
            "defensive_multiplier": max_defensive_mult,
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

        
