from funciones import tarea_to_dict
import random


def _fitness(individuo, tareas, tiempo_disponible):
    tiempo = sum(tareas[i].tiempo_estimado for i in range(len(individuo)) if individuo[i])
    if tiempo > tiempo_disponible:
        return 0.0
    return sum(tareas[i].prioridad for i in range(len(individuo)) if individuo[i])


def _cruce(padre1, padre2):
    punto = random.randint(1, len(padre1) - 1)
    return padre1[:punto] + padre2[punto:], padre2[:punto] + padre1[punto:]


def _mutar(individuo, prob):
    return tuple(1 - gen if random.random() < prob else gen for gen in individuo)


def genetic_plan(tareas, tiempo_disponible, generacion=100, tam_poblacion=50, elite=5):
    """
    Algoritmo Genético para seleccion de tareas.
    Representación: cada gen es 0 o 1 (tarea incluida o no).
    Fitness: prioridad total sin exceder tiempo disponible.
    Función pura: no modifica las tareas de entrada.
    """
    if not tareas:
        return {"plan": [], "tiempo_total": 0, "prioridad_total": 0,
                "tiempo_disponible": tiempo_disponible}

    random.seed(42)
    n = len(tareas)
    poblacion = []

    for _ in range(tam_poblacion):
        tiempo_acum = 0
        individuo = []
        indices = list(range(n))
        random.shuffle(indices)
        for i in indices:
            if tiempo_acum + tareas[i].tiempo_estimado <= tiempo_disponible:
                individuo.append(i)
                tiempo_acum += tareas[i].tiempo_estimado
        vec = tuple(1 if i in set(individuo) else 0 for i in range(n))
        poblacion.append(vec)

    for _ in range(generacion):
        valores = [_fitness(ind, tareas, tiempo_disponible) for ind in poblacion]
        mejores = sorted(zip(valores, poblacion), key=lambda x: x[0], reverse=True)
        elite_ind = [ind for _, ind in mejores[:elite]]

        nueva_poblacion = list(elite_ind)
        while len(nueva_poblacion) < tam_poblacion:
            tournament = random.sample(list(zip(valores, poblacion)), k=3)
            padre1 = max(tournament, key=lambda x: x[0])[1]
            tournament = random.sample(list(zip(valores, poblacion)), k=3)
            padre2 = max(tournament, key=lambda x: x[0])[1]
            hijo1, _ = _cruce(padre1, padre2)
            hijo2, _ = _cruce(padre2, padre1)
            nueva_poblacion.append(_mutar(hijo1, 0.05))
            nueva_poblacion.append(_mutar(hijo2, 0.05))

        poblacion = nueva_poblacion[:tam_poblacion]

    best_ind = max(poblacion, key=lambda ind: _fitness(ind, tareas, tiempo_disponible))
    plan = [tarea_to_dict(tareas[i]) for i in range(n) if best_ind[i]]
    tiempo_usado = sum(t["tiempo_estimado"] for t in plan)
    prioridad_total = sum(t["prioridad"] for t in plan)

    return {
        "plan": plan, "tiempo_total": tiempo_usado,
        "prioridad_total": round(prioridad_total, 1),
        "tiempo_disponible": tiempo_disponible,
        "tiempo_restante": tiempo_disponible - tiempo_usado,
        "tareas_incluidas": len(plan),
        "tareas_excluidas": n - len(plan)
    }