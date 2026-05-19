from algorithms.topological_sort import dependencias_resueltas
from funciones import tarea_to_dict


def greedy_plan(tareas, tiempo_disponible):
    """
    Algoritmo Greedy: selecciona tareas con mayor ratio prioridad/tiempo
    que quepan en el tiempo disponible, respetando dependencias.
    Funcion pura: no modifica las tareas de entrada.
    Complejidad: O(n log n). No garantiza optimalidad global.
    """
    if not tareas:
        return {
            "plan": [], "tiempo_total": 0, "prioridad_total": 0,
            "tiempo_disponible": tiempo_disponible
        }

    completadas_ids = set()
    plan = []
    tiempo_usado = 0
    prioridad_total = 0.0
    pendientes = list(tareas)

    while pendientes:
        candidatos = []
        for t in pendientes:
            if dependencias_resueltas(t, completadas_ids,
                                      {x.id for x in pendientes}):
                ratio = t.prioridad / max(t.tiempo_estimado, 1)
                candidatos.append((ratio, t))

        if not candidatos:
            break

        candidatos.sort(key=lambda x: x[0], reverse=True)
        _, mejor = candidatos[0]

        if tiempo_usado + mejor.tiempo_estimado <= tiempo_disponible:
            plan.append(tarea_to_dict(mejor))
            tiempo_usado += mejor.tiempo_estimado
            prioridad_total += mejor.prioridad
            completadas_ids.add(mejor.id)

        pendientes = [t for t in pendientes if t.id != mejor.id]

    return {
        "plan": plan,
        "tiempo_total": tiempo_usado,
        "prioridad_total": round(prioridad_total, 1),
        "tiempo_disponible": tiempo_disponible,
        "tiempo_restante": tiempo_disponible - tiempo_usado,
        "tareas_incluidas": len(plan),
        "tareas_excluidas": len(tareas) - len(plan)
    }
