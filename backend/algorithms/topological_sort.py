from collections import deque


def orden_topologico(tareas):
    """
    Kahn's Algorithm para topological sort de tareas con dependencias.
    Retorna orden valido o None si hay ciclo.
    """
    ids = {t.id for t in tareas}
    tareas_map = {t.id: t for t in tareas}

    grafo = {t.id: [] for t in tareas}
    in_degree = {t.id: 0 for t in tareas}

    for t in tareas:
        for dep_id in t.dependencias:
            if dep_id in ids:
                grafo[dep_id].append(t.id)
                in_degree[t.id] += 1

    queue = deque([t.id for t in tareas if in_degree[t.id] == 0])
    orden = []

    while queue:
        nodo_id = queue.popleft()
        orden.append(nodo_id)
        for vecino in grafo[nodo_id]:
            in_degree[vecino] -= 1
            if in_degree[vecino] == 0:
                queue.append(vecino)

    if len(orden) != len(tareas):
        return None

    from funciones import tarea_to_dict
    return [tarea_to_dict(tareas_map[tid]) for tid in orden]


def dependencias_resueltas(tarea, completadas_ids, pendientes_ids=None):
    """
    Verifica si todas las dependencias de una tarea estan resueltas.
    """
    if not tarea.dependencias:
        return True
    for dep_id in tarea.dependencias:
        if dep_id not in completadas_ids:
            return False
    return True


def detectar_ciclos(tareas):
    """
    Detecta si hay ciclos en el grafo de dependencias.
    """
    return orden_topologico(tareas) is None
