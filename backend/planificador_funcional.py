from dataclasses import replace
from datetime import date
from functools import reduce
from typing import Tuple, Optional, List

from tipos import Tarea, Usuario, Estado
from funciones import (
    tarea_to_dict, calcular_prioridad, marcar_completada, procesar_recurrencia,
    toggle_subtarea_de_tarea, agregar_subtarea_a_tarea,
    usuario_to_dict, usuario_from_dict, tarea_from_dict
)


# ---- Acceso a datos (puro) ----

def obtener_tarea(estado: Estado, id_tarea: str) -> Optional[Tarea]:
    for t in estado.tareas_pendientes:
        if t.id == id_tarea:
            return t
    for t in estado.tareas_completadas:
        if t.id == id_tarea:
            return t
    return None


def tareas_pendientes(estado: Estado) -> Tuple[Tarea, ...]:
    return tuple(t for t in estado.tareas_pendientes if not t.completada)


def filtrar_por_categoria(estado: Estado, categoria: str) -> Tuple[Tarea, ...]:
    if categoria == "todas":
        return estado.tareas_pendientes
    return tuple(t for t in estado.tareas_pendientes if t.categoria == categoria)


# ---- Mutaciones de estado (retornan nuevo Estado) ----

def agregar_tarea(estado: Estado, tarea: Tarea) -> Estado:
    tarea = calcular_prioridad(tarea)
    nuevas = tuple(sorted(
        estado.tareas_pendientes + (tarea,),
        key=lambda t: t.prioridad, reverse=True
    ))
    return replace(estado, tareas_pendientes=nuevas)


def eliminar_tarea(estado: Estado, id_tarea: str) -> Estado:
    return replace(estado,
        tareas_pendientes=tuple(t for t in estado.tareas_pendientes if t.id != id_tarea),
        tareas_completadas=tuple(t for t in estado.tareas_completadas if t.id != id_tarea)
    )


def completar_tarea_estado(estado: Estado, id_tarea: str,
                           tiempo_real: Optional[int] = None) -> Optional[Estado]:
    tarea = obtener_tarea(estado, id_tarea)
    if tarea is None:
        return None
    tarea_completada = marcar_completada(tarea, tiempo_real)

    # Remover de pendientes, agregar a completadas
    nuevas_pend = tuple(t for t in estado.tareas_pendientes if t.id != id_tarea)
    nuevas_comp = estado.tareas_completadas + (tarea_completada,)

    # Procesar recurrencia
    nueva_recurrente = procesar_recurrencia(tarea)
    if nueva_recurrente:
        nueva_recurrente = calcular_prioridad(nueva_recurrente)
        nuevas_pend = tuple(sorted(
            nuevas_pend + (nueva_recurrente,),
            key=lambda t: t.prioridad, reverse=True
        ))

    # Registrar en historial
    hoy = date.today().isoformat()
    nuevo_historial = dict(estado.historial_diario)
    nuevo_historial[hoy] = nuevo_historial.get(hoy, []) + [tarea_to_dict(tarea_completada)]

    return replace(estado,
        tareas_pendientes=nuevas_pend,
        tareas_completadas=nuevas_comp,
        historial_diario=nuevo_historial
    )


def actualizar_usuario(estado: Estado, usuario: Usuario) -> Estado:
    return replace(estado, usuario=usuario)


# ---- Alertas (puro) ----

def verificar_alertas(estado: Estado) -> list:
    alertas = []
    pendientes = tareas_pendientes(estado)
    tiempo_total = sum(t.tiempo_estimado for t in pendientes)
    hoy = date.today()

    for tarea in pendientes:
        if tarea.fecha_limite and (tarea.fecha_limite - hoy).days <= 1:
            alertas.append({
                "tipo": "urgente",
                "tarea": tarea_to_dict(tarea),
                "mensaje": f"Tarea '{tarea.nombre}' vence en menos de 24 horas"
            })

    if tiempo_total > estado.usuario.tiempo_disponible:
        alertas.append({
            "tipo": "sobrecarga",
            "tareas_pendientes": len(pendientes),
            "tiempo_requerido": tiempo_total,
            "tiempo_disponible": estado.usuario.tiempo_disponible,
            "mensaje": (f"Tiempo requerido ({tiempo_total} min) excede "
                        f"el disponible ({estado.usuario.tiempo_disponible} min)")
        })

    return alertas


# ---- Eisenhower (puro) ----

def clasificar_eisenhower(estado: Estado) -> dict:
    cuadrantes = {"q1": [], "q2": [], "q3": [], "q4": []}
    pendientes = tareas_pendientes(estado)
    hoy = date.today()

    for t in pendientes:
        urgente = (t.fecha_limite is not None and
                   (t.fecha_limite - hoy).days <= 2)
        importante = t.importancia >= 4

        if urgente and importante:
            cuadrantes["q1"].append(tarea_to_dict(t))
        elif not urgente and importante:
            cuadrantes["q2"].append(tarea_to_dict(t))
        elif urgente and not importante:
            cuadrantes["q3"].append(tarea_to_dict(t))
        else:
            cuadrantes["q4"].append(tarea_to_dict(t))

    return cuadrantes


# ---- Metricas (puro) ----

def calcular_racha(historial_diario: dict) -> int:
    if not historial_diario:
        return 0
    fechas = sorted(historial_diario.keys(), reverse=True)
    racha = 0
    hoy = date.today()
    from datetime import timedelta
    for i, f_str in enumerate(fechas):
        f = date.fromisoformat(f_str)
        dia_esperado = hoy - timedelta(days=i)
        if f == dia_esperado:
            racha += 1
        else:
            break
    return racha


def calcular_metricas(estado: Estado) -> dict:
    hist = estado.historial_diario
    if not hist:
        return {
            "completadas_hoy": 0, "racha": 0, "dias_ultima_semana": [],
            "tiempo_promedio_real": 0, "total_tareas_historial": 0
        }

    from datetime import timedelta
    dias_ultima_semana = []
    hoy = date.today()
    for i in range(7):
        f = (hoy - timedelta(days=i)).isoformat()
        dia_tareas = hist.get(f, [])
        dias_ultima_semana.append({
            "fecha": f,
            "tareas_completadas": len(dia_tareas),
            "tiempo_total": sum(
                (t.get("tiempo_real") or t.get("tiempo_estimado", 0))
                for t in dia_tareas
            )
        })

    hoy_str = hoy.isoformat()
    tareas_hoy = hist.get(hoy_str, [])
    completadas_hoy = len(tareas_hoy)

    total_minutos = sum(
        (t.get("tiempo_real") or t.get("tiempo_estimado", 0))
        for dia_data in hist.values() for t in dia_data
    )
    total_tareas = sum(len(v) for v in hist.values())
    tiempo_promedio = total_minutos / total_tareas if total_tareas > 0 else 0

    return {
        "completadas_hoy": completadas_hoy,
        "racha": calcular_racha(hist),
        "dias_ultima_semana": dias_ultima_semana,
        "tiempo_promedio_real": round(tiempo_promedio, 1),
        "total_tareas_historial": total_tareas
    }


# ---- Serializacion del estado ----

def estado_to_dict(estado: Estado) -> dict:
    return {
        "usuario": usuario_to_dict(estado.usuario),
        "tareas_pendientes": [tarea_to_dict(t) for t in estado.tareas_pendientes],
        "tareas_completadas": [tarea_to_dict(t) for t in estado.tareas_completadas],
        "historial_diario": estado.historial_diario
    }


def estado_from_dict(data: dict) -> Estado:
    usuario = usuario_from_dict(data.get("usuario", {}))
    pendientes = tuple(
        calcular_prioridad(tarea_from_dict(td))
        for td in data.get("tareas_pendientes", [])
    )
    completadas = tuple(
        tarea_from_dict(td)
        for td in data.get("tareas_completadas", [])
    )
    pendientes = tuple(sorted(pendientes, key=lambda t: t.prioridad, reverse=True))
    historial = data.get("historial_diario", {})
    return Estado(
        usuario=usuario,
        tareas_pendientes=pendientes,
        tareas_completadas=completadas,
        historial_diario=historial
    )


# ---- Delegacion a algoritmos ----

def generar_plan_greedy(estado: Estado) -> dict:
    from algorithms.greedy_planner import greedy_plan
    return greedy_plan(tareas_pendientes(estado), estado.usuario.tiempo_disponible)


def generar_plan_knapsack(estado: Estado) -> dict:
    from algorithms.knapsack_dp import knapsack_plan
    return knapsack_plan(tareas_pendientes(estado), estado.usuario.tiempo_disponible)


def generar_planes_backtracking(estado: Estado, top_n: int = 3) -> list:
    from algorithms.backtracking_planner import backtracking_plans
    return backtracking_plans(tareas_pendientes(estado),
                              estado.usuario.tiempo_disponible, top_n)


def generar_plan_genetic(estado: Estado) -> dict:
    from algorithms.genetic_planner import genetic_plan
    return genetic_plan(tareas_pendientes(estado), estado.usuario.tiempo_disponible)
