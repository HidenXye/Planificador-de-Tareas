from dataclasses import replace
from datetime import date, datetime
from functools import wraps
from typing import Optional, Tuple, List, Callable

from tipos import (
    Tarea, Subtarea, Usuario, Estado,
    CATEGORIAS, FRECUENCIAS, TIPOS_ENERGIA, _new_id
)


def pipe(*funcs: Callable) -> Callable:
    """Composicion de funciones: pipe(f, g, h)(x) = h(g(f(x)))"""
    def composed(x):
        result = x
        for f in funcs:
            result = f(result)
        return result
    return composed


def composicion(*funcs: Callable) -> Callable:
    """Composicion matematica: comp(f, g)(x) = f(g(x))"""
    def composed(x):
        result = x
        for f in reversed(funcs):
            result = f(result)
        return result
    return composed


# ---- Validacion pura ----

def validar_categoria(cat: str) -> str:
    return cat if cat in CATEGORIAS else "personal"

def validar_importancia(n: int) -> int:
    return max(1, min(5, n))

def validar_urgencia(n: int) -> int:
    return max(1, min(5, n))

def validar_frecuencia(f: str) -> str:
    return f if f in FRECUENCIAS else "ninguna"

def validar_tipo_energia(t: str) -> str:
    return t if t in TIPOS_ENERGIA else "neutro"


# ---- Parseo puro ----

def parsear_fecha(fecha) -> Optional[date]:
    if fecha is None:
        return None
    if isinstance(fecha, date):
        return fecha
    if isinstance(fecha, datetime):
        return fecha.date()
    if isinstance(fecha, str):
        for fmt in ("%Y-%m-%d",):
            try:
                return datetime.strptime(fecha, fmt).date()
            except ValueError:
                pass
        try:
            return datetime.fromisoformat(fecha).date()
        except ValueError:
            return None
    return None


# ---- Subtarea funciones puras ----

def toggle_subtarea(st: Subtarea) -> Subtarea:
    return replace(st, completada=not st.completada)

def subtarea_to_dict(st: Subtarea) -> dict:
    return {"id": st.id, "nombre": st.nombre, "completada": st.completada}

def subtarea_from_dict(d: dict) -> Subtarea:
    return Subtarea(
        id=d.get("id", _new_id()),
        nombre=d.get("nombre", ""),
        completada=d.get("completada", False)
    )


# ---- Factor energia ----

def factor_energia(tipo: str) -> float:
    factores = {"manana": 1.15, "tarde": 1.0, "noche": 0.85, "neutro": 1.0}
    return factores.get(tipo, 1.0)


# ---- Calculo de prioridad (funcion pura) ----

def calcular_urgencia_dias(tarea: Tarea) -> int:
    if tarea.fecha_limite is None:
        return tarea.urgencia
    hoy = date.today()
    return (tarea.fecha_limite - hoy).days


def calcular_prioridad(tarea: Tarea) -> Tarea:
    peso_urgencia = 0.50
    peso_importancia = 0.30
    peso_tiempo = 0.20

    if tarea.fecha_limite is not None:
        hoy = date.today()
        dias_restantes = max(0, (tarea.fecha_limite - hoy).days)
        if dias_restantes == 0:
            factor_urg = 1.0
        elif dias_restantes <= 1:
            factor_urg = 0.95
        elif dias_restantes <= 3:
            factor_urg = 0.80
        elif dias_restantes <= 7:
            factor_urg = 0.55
        else:
            factor_urg = max(0.1, 1.0 / (dias_restantes + 1))
    else:
        factor_urg = tarea.urgencia / 5.0

    prioridad_base = (factor_urg * peso_urgencia +
                      (tarea.importancia / 5.0) * peso_importancia +
                      (60.0 / max(tarea.tiempo_estimado, 1)) * peso_tiempo)

    prioridad_base = min(prioridad_base, 1.0)
    prioridad_base *= 100

    if tarea.dependencias:
        prioridad_base *= 0.8

    if tarea.subtareas:
        completadas = sum(1 for s in tarea.subtareas if s.completada)
        progreso = completadas / len(tarea.subtareas)
        prioridad_base *= (0.9 + 0.1 * progreso)

    nueva_prio = round(min(prioridad_base, 100), 1)
    return replace(tarea, prioridad=nueva_prio)


# ---- Transformaciones de Tarea ----

def marcar_completada(tarea: Tarea, tiempo_real: Optional[int] = None) -> Tarea:
    modificaciones = {"completada": True}
    if tiempo_real is not None:
        modificaciones["tiempo_real"] = tiempo_real
    return replace(tarea, **modificaciones)


def progreso_subtareas(tarea: Tarea) -> int:
    if not tarea.subtareas:
        return 100
    completadas = sum(1 for s in tarea.subtareas if s.completada)
    return int((completadas / len(tarea.subtareas)) * 100)


def agregar_subtarea_a_tarea(tarea: Tarea, nombre: str) -> Tarea:
    return replace(tarea,
        subtareas=tarea.subtareas + (Subtarea(nombre=nombre),))


def toggle_subtarea_de_tarea(tarea: Tarea, id_sub: str) -> Optional[Tarea]:
    for i, st in enumerate(tarea.subtareas):
        if st.id == id_sub:
            nuevas_st = list(tarea.subtareas)
            nuevas_st[i] = toggle_subtarea(st)
            return replace(tarea, subtareas=tuple(nuevas_st))
    return None


# ---- Recurrencia pura ----

def procesar_recurrencia(tarea: Tarea) -> Optional[Tarea]:
    if not tarea.es_recurrente or tarea.frecuencia == "ninguna":
        return None
    delta = {"diario": 1, "semanal": 7, "mensual": 30}.get(tarea.frecuencia, 0)
    nueva_fl = None
    if tarea.fecha_limite:
        from datetime import timedelta
        nueva_fl = tarea.fecha_limite + timedelta(days=delta)
    return Tarea(
        nombre=tarea.nombre,
        tiempo_estimado=tarea.tiempo_estimado,
        importancia=tarea.importancia,
        urgencia=tarea.urgencia,
        categoria=tarea.categoria,
        descripcion=tarea.descripcion,
        dependencias=tarea.dependencias,
        subtareas=tarea.subtareas,
        es_recurrente=True,
        frecuencia=tarea.frecuencia,
        fecha_limite=nueva_fl
    )


# ---- Serializacion (to_dict / from_dict) ----

def tarea_to_dict(tarea: Tarea) -> dict:
    return {
        "id": tarea.id,
        "nombre": tarea.nombre,
        "descripcion": tarea.descripcion,
        "fecha_limite": tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
        "tiempo_estimado": tarea.tiempo_estimado,
        "tiempo_real": tarea.tiempo_real,
        "importancia": tarea.importancia,
        "urgencia": tarea.urgencia,
        "prioridad": tarea.prioridad,
        "categoria": tarea.categoria,
        "completada": tarea.completada,
        "dependencias": list(tarea.dependencias),
        "subtareas": [subtarea_to_dict(st) for st in tarea.subtareas],
        "es_recurrente": tarea.es_recurrente,
        "frecuencia": tarea.frecuencia,
        "hora_inicio": tarea.hora_inicio,
        "duracion": tarea.tiempo_estimado
    }


def tarea_from_dict(d: dict) -> Tarea:
    subtareas = tuple(
        subtarea_from_dict(st) for st in d.get("subtareas", ())
    ) if d.get("subtareas") else ()

    return Tarea(
        id=d.get("id", _new_id()),
        nombre=d.get("nombre", ""),
        descripcion=d.get("descripcion", ""),
        fecha_limite=parsear_fecha(d.get("fecha_limite")),
        tiempo_estimado=d.get("tiempo_estimado", 30),
        tiempo_real=d.get("tiempo_real"),
        importancia=validar_importancia(d.get("importancia", 3)),
        urgencia=validar_urgencia(d.get("urgencia", 3)),
        prioridad=d.get("prioridad", 0.0),
        categoria=validar_categoria(d.get("categoria", "personal")),
        completada=d.get("completada", False),
        dependencias=tuple(d.get("dependencias", ())),
        subtareas=subtareas,
        es_recurrente=d.get("es_recurrente", False),
        frecuencia=validar_frecuencia(d.get("frecuencia", "ninguna")),
        hora_inicio=d.get("hora_inicio")
    )


def usuario_to_dict(u: Usuario) -> dict:
    return {
        "nombre": u.nombre,
        "tiempo_disponible": u.tiempo_disponible,
        "tipo_energia": u.tipo_energia,
        "notificaciones": u.notificaciones,
        "tema_oscuro": u.tema_oscuro
    }


def usuario_from_dict(d: dict) -> Usuario:
    return Usuario(
        nombre=d.get("nombre", "Usuario"),
        tiempo_disponible=d.get("tiempo_disponible", 480),
        tipo_energia=validar_tipo_energia(d.get("tipo_energia", "neutro")),
        notificaciones=d.get("notificaciones", True),
        tema_oscuro=d.get("tema_oscuro", False)
    )
