from datetime import datetime, date
from .item_diario import ItemDiario
from .subtarea import Subtarea


class Tarea(ItemDiario):
    CATEGORIAS = ["trabajo", "personal", "estudio"]
    FRECUENCIAS = ["ninguna", "diario", "semanal", "mensual"]

    def __init__(self, nombre, fecha_limite=None, tiempo_estimado=30,
                 importancia=3, urgencia=3, categoria="personal",
                 descripcion="", dependencias=None, subtareas=None,
                 es_recurrente=False, frecuencia="ninguna",
                 completada=False, tiempo_real=None, hora_inicio=None,
                 id_item=None):
        super().__init__(nombre, tiempo_estimado, hora_inicio, id_item)
        self.descripcion = descripcion
        self.fecha_limite = self._parse_fecha(fecha_limite)
        self.tiempo_estimado = tiempo_estimado
        self.tiempo_real = tiempo_real
        self.importancia = max(1, min(5, importancia))
        self.urgencia = max(1, min(5, urgencia))
        self.categoria = categoria if categoria in self.CATEGORIAS else "personal"
        self.completada = completada
        self.dependencias = dependencias or []
        self.subtareas = []
        if subtareas:
            for st in subtareas:
                if isinstance(st, dict):
                    self.subtareas.append(Subtarea.from_dict(st))
                elif isinstance(st, Subtarea):
                    self.subtareas.append(st)
        self.es_recurrente = es_recurrente
        self.frecuencia = frecuencia if frecuencia in self.FRECUENCIAS else "ninguna"
        self.prioridad = self.calcular_prioridad()
        self.duracion = tiempo_estimado

    def _parse_fecha(self, fecha):
        if fecha is None:
            return None
        if isinstance(fecha, str):
            try:
                return datetime.strptime(fecha, "%Y-%m-%d").date()
            except ValueError:
                try:
                    return datetime.fromisoformat(fecha).date()
                except ValueError:
                    return None
        if isinstance(fecha, datetime):
            return fecha.date()
        if isinstance(fecha, date):
            return fecha
        return None

    def calcular_urgencia_dias(self):
        if self.fecha_limite is None:
            return self.urgencia
        hoy = date.today()
        dias = (self.fecha_limite - hoy).days
        return dias

    def calcular_prioridad(self):
        peso_urgencia = 0.50
        peso_importancia = 0.30
        peso_tiempo = 0.20

        if self.fecha_limite is not None:
            hoy = date.today()
            dias_restantes = max(0, (self.fecha_limite - hoy).days)
            if dias_restantes == 0:
                factor_urgencia = 1.0
            elif dias_restantes <= 1:
                factor_urgencia = 0.95
            elif dias_restantes <= 3:
                factor_urgencia = 0.80
            elif dias_restantes <= 7:
                factor_urgencia = 0.55
            else:
                factor_urgencia = max(0.1, 1.0 / (dias_restantes + 1))
        else:
            factor_urgencia = self.urgencia / 5.0

        prioridad_base = (factor_urgencia * peso_urgencia +
                          (self.importancia / 5.0) * peso_importancia +
                          (60.0 / max(self.tiempo_estimado, 1)) * peso_tiempo)

        prioridad_base = min(prioridad_base, 1.0)
        prioridad_base *= 100

        if self.dependencias:
            prioridad_base *= 0.8

        if self.subtareas:
            completadas = sum(1 for s in self.subtareas if s.completada)
            progreso = completadas / len(self.subtareas)
            prioridad_base *= (0.9 + 0.1 * progreso)

        self.prioridad = round(min(prioridad_base, 100), 1)
        self.duracion = self.tiempo_estimado
        return self.prioridad

    def marcar_completada(self, tiempo_real=None):
        self.completada = True
        if tiempo_real:
            self.tiempo_real = tiempo_real

    def progreso_subtareas(self):
        if not self.subtareas:
            return 100
        completadas = sum(1 for s in self.subtareas if s.completada)
        return int((completadas / len(self.subtareas)) * 100)

    def agregar_subtarea(self, nombre):
        st = Subtarea(nombre)
        self.subtareas.append(st)
        return st

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "fecha_limite": self.fecha_limite.isoformat() if self.fecha_limite else None,
            "tiempo_estimado": self.tiempo_estimado,
            "tiempo_real": self.tiempo_real,
            "importancia": self.importancia,
            "urgencia": self.urgencia,
            "prioridad": self.prioridad,
            "categoria": self.categoria,
            "completada": self.completada,
            "dependencias": self.dependencias,
            "subtareas": [st.to_dict() for st in self.subtareas],
            "es_recurrente": self.es_recurrente,
            "frecuencia": self.frecuencia,
            "hora_inicio": self.hora_inicio,
            "duracion": self.duracion
        }

    @staticmethod
    def from_dict(data):
        return Tarea(
            nombre=data["nombre"],
            fecha_limite=data.get("fecha_limite"),
            tiempo_estimado=data.get("tiempo_estimado", 30),
            importancia=data.get("importancia", 3),
            urgencia=data.get("urgencia", 3),
            categoria=data.get("categoria", "personal"),
            descripcion=data.get("descripcion", ""),
            dependencias=data.get("dependencias", []),
            subtareas=data.get("subtareas", []),
            es_recurrente=data.get("es_recurrente", False),
            frecuencia=data.get("frecuencia", "ninguna"),
            completada=data.get("completada", False),
            tiempo_real=data.get("tiempo_real"),
            hora_inicio=data.get("hora_inicio"),
            id_item=data.get("id")
        )

    def __repr__(self):
        return (f"Tarea(nombre='{self.nombre}', prioridad={self.prioridad}, "
                f"tiempo={self.tiempo_estimado}min, completada={self.completada})")
