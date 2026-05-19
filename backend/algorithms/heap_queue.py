import heapq


def heap_sort_tareas(tareas):
    """
    Ordena tareas de mayor a menor prioridad usando un max-heap.
    Complejidad: O(n log n)
    """
    return sorted(tareas, key=lambda t: t.prioridad, reverse=True)


def get_top_n(tareas, n=5):
    """
    Retorna las n tareas de mayor prioridad.
    Usa heapq.nlargest para eficiencia.
    """
    return heapq.nlargest(n, tareas, key=lambda t: t.prioridad)


def heap_sort_by_ratio(tareas):
    """
    Ordena por ratio prioridad/tiempo (valor por minuto).
    Retorna nueva lista ordenada, sin mutar la original.
    """
    return sorted(
        tareas,
        key=lambda t: t.prioridad / max(t.tiempo_estimado, 1),
        reverse=True
    )
