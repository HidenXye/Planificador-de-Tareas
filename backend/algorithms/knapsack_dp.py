def knapsack_plan(tareas, tiempo_disponible):
    """
    DP 0/1 Knapsack para seleccion optima de tareas.
    Maximiza prioridad total sin exceder tiempo disponible.

    Complejidad: O(n * T) donde T = tiempo_disponible
    Garantiza optimalidad global.
    """
    if not tareas:
        return {"plan": [], "tiempo_total": 0, "prioridad_total": 0, "tiempo_disponible": tiempo_disponible}

    n = len(tareas)
    T = tiempo_disponible

    dp = [[0.0] * (T + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        tarea = tareas[i - 1]
        for t in range(T + 1):
            if tarea.tiempo_estimado <= t:
                dp[i][t] = max(dp[i - 1][t],
                               dp[i - 1][t - tarea.tiempo_estimado] + tarea.prioridad)
            else:
                dp[i][t] = dp[i - 1][t]

    plan = []
    t_restante = T
    for i in range(n, 0, -1):
        if dp[i][t_restante] != dp[i - 1][t_restante]:
            tarea = tareas[i - 1]
            plan.append(tarea.to_dict())
            t_restante -= tarea.tiempo_estimado

    plan.reverse()
    tiempo_usado = sum(t["tiempo_estimado"] for t in plan)
    prioridad_total = sum(t["prioridad"] for t in plan)

    return {
        "plan": plan,
        "tiempo_total": tiempo_usado,
        "prioridad_total": round(prioridad_total, 1),
        "tiempo_disponible": T,
        "tiempo_restante": T - tiempo_usado,
        "tareas_incluidas": len(plan),
        "tareas_excluidas": n - len(plan)
    }
