from dataclasses import dataclass, field, replace
from datetime import date as Date
from typing import Optional, Tuple, Dict
from uuid import uuid4


def _new_id():
    return str(uuid4())


CATEGORIAS = ("trabajo", "personal", "estudio")
FRECUENCIAS = ("ninguna", "diario", "semanal", "mensual")
TIPOS_ENERGIA = ("manana", "tarde", "noche", "neutro")


@dataclass(frozen=True)
class Subtarea:
    id: str = field(default_factory=_new_id)
    nombre: str = ""
    completada: bool = False


@dataclass(frozen=True)
class Tarea:
    id: str = field(default_factory=_new_id)
    nombre: str = ""
    descripcion: str = ""
    fecha_limite: Optional[Date] = None
    tiempo_estimado: int = 30
    tiempo_real: Optional[int] = None
    importancia: int = 3
    urgencia: int = 3
    prioridad: float = 0.0
    categoria: str = "personal"
    completada: bool = False
    dependencias: Tuple[str, ...] = ()
    subtareas: Tuple[Subtarea, ...] = ()
    es_recurrente: bool = False
    frecuencia: str = "ninguna"
    hora_inicio: Optional[str] = None


@dataclass(frozen=True)
class Evento:
    id: str = field(default_factory=_new_id)
    nombre: str = ""
    duracion: int = 60
    ubicacion: str = ""
    es_recurrente: bool = False
    frecuencia: str = "ninguna"
    hora_inicio: Optional[str] = None


@dataclass(frozen=True)
class Usuario:
    nombre: str = "Usuario"
    tiempo_disponible: int = 480
    tipo_energia: str = "neutro"
    notificaciones: bool = True
    tema_oscuro: bool = False


@dataclass(frozen=True)
class Estado:
    usuario: Usuario = field(default_factory=Usuario)
    tareas_pendientes: Tuple[Tarea, ...] = ()
    tareas_completadas: Tuple[Tarea, ...] = ()
    historial_diario: Dict[str, list] = field(default_factory=dict)
