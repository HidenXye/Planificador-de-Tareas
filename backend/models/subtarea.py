from uuid import uuid4


class Subtarea:
    def __init__(self, nombre, completada=False, id_sub=None):
        self.id = id_sub or str(uuid4())
        self.nombre = nombre
        self.completada = completada

    def toggle(self):
        self.completada = not self.completada

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "completada": self.completada
        }

    @staticmethod
    def from_dict(data):
        return Subtarea(
            nombre=data["nombre"],
            completada=data.get("completada", False),
            id_sub=data.get("id")
        )
