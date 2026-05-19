from .item_diario import ItemDiario


class Evento(ItemDiario):
    def __init__(self, nombre, duracion, ubicacion="", es_recurrente=False,
                 frecuencia="ninguna", hora_inicio=None, id_item=None):
        super().__init__(nombre, duracion, hora_inicio, id_item)
        self.ubicacion = ubicacion
        self.es_recurrente = es_recurrente
        self.frecuencia = frecuencia

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "duracion": self.duracion,
            "ubicacion": self.ubicacion,
            "es_recurrente": self.es_recurrente,
            "frecuencia": self.frecuencia,
            "hora_inicio": self.hora_inicio
        }

    @staticmethod
    def from_dict(data):
        return Evento(
            nombre=data["nombre"],
            duracion=data.get("duracion", 60),
            ubicacion=data.get("ubicacion", ""),
            es_recurrente=data.get("es_recurrente", False),
            frecuencia=data.get("frecuencia", "ninguna"),
            hora_inicio=data.get("hora_inicio"),
            id_item=data.get("id")
        )
