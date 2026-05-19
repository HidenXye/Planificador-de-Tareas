import heapq


def heap_sort_tareas(tareas):
    """
    Ordena tareas de mayor a menor prioridad usando un max-heap.
    Complejidad: O(n log n)
    """
    heap = []
    for tarea in tareas:
        heapq.heappush(heap, tarea)
    resultado = []
    while heap:
        resultado.append(heapq.heappop(heap))
    return resultado


def get_top_n(tareas, n=5):
    """
    Retorna las n tareas de mayor prioridad.
    Usa heapq.nlargest para eficiencia.
    """
    return heapq.nlargest(n, tareas, key=lambda t: t.prioridad)


def heap_sort_by_ratio(tareas):
    """
    Ordena por ratio prioridad/tiempo (valor por minuto).
    """
    heap = []
    for tarea in tareas:
        ratio = tarea.prioridad / max(tarea.tiempo_estimado, 1)
        heapq.heappush(heap, (-ratio, tarea))
    resultado = []
    while heap:
        ratio_neg, tarea = heapq.heappop(heap)
        resultado.append(tarea)
    return resultado
