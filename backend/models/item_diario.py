from abc import ABC, abstractmethod
from uuid import uuid4


class ItemDiario(ABC):
    def __init__(self, nombre, duracion, hora_inicio=None, id_item=None):
        self.id = id_item or str(uuid4())
        self.nombre = nombre
        self.duracion = duracion
        self.hora_inicio = hora_inicio

    @abstractmethod
    def to_dict(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(data):
        pass

    def __str__(self):
        return f"{self.nombre} ({self.duracion} min)"

    def __lt__(self, other):
        if hasattr(self, 'prioridad') and hasattr(other, 'prioridad'):
            return self.prioridad > other.prioridad
        return self.duracion < other.duracion
