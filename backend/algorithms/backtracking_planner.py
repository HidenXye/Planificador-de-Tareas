from copy import deepcopy


def backtracking_plans(tareas, tiempo_disponible, top_n=3):
    """
    Backtracking con poda para generar las top_n mejores combinaciones
    de tareas que maximizan prioridad total.

    Poda:
    - Tiempo acumulado > tiempo_disponible
    - Prioridad maxima posible restante < peor de las top_n encontradas
    """
    if not tareas:
        return []

    mejores = []
    n = len(tareas)
    prioridad_maxima_restante = [0.0] * (n + 1)
    for i in range(n - 1, -1, -1):
        prioridad_maxima_restante[i] = prioridad_maxima_restante[i + 1] + tareas[i].prioridad

    def backtrack(idx, tiempo_actual, prioridad_actual, seleccionadas):
        if idx == n:
            registro = {
                "plan": [tareas[i].to_dict() for i in seleccionadas],
                "tiempo_total": tiempo_actual,
                "prioridad_total": round(prioridad_actual, 1),
                "tareas_incluidas": len(seleccionadas)
            }
            mejores.append(registro)
            mejores.sort(key=lambda x: x["prioridad_total"], reverse=True)
            if len(mejores) > top_n:
                mejores.pop()
            return

        if tiempo_actual > tiempo_disponible:
            return

        peor_prioridad = mejores[-1]["prioridad_total"] if len(mejores) >= top_n else 0
        if prioridad_actual + prioridad_maxima_restante[idx] < peor_prioridad:
            return

        tarea = tareas[idx]
        if tiempo_actual + tarea.tiempo_estimado <= tiempo_disponible:
            backtrack(idx + 1, tiempo_actual + tarea.tiempo_estimado,
                      prioridad_actual + tarea.prioridad, seleccionadas + [idx])

        backtrack(idx + 1, tiempo_actual, prioridad_actual, seleccionadas)

    backtrack(0, 0, 0.0, [])

    for plan in mejores:
        plan["tiempo_disponible"] = tiempo_disponible
        plan["tiempo_restante"] = tiempo_disponible - plan["tiempo_total"]

    return mejores[:top_n]
