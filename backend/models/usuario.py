class Usuario:
    TIPOS_ENERGIA = ["manana", "tarde", "noche", "neutro"]

    def __init__(self, nombre="Usuario", tiempo_disponible=480, tipo_energia="neutro",
                 notificaciones=True, tema_oscuro=False):
        self.nombre = nombre
        self.tiempo_disponible = tiempo_disponible
        self.tipo_energia = tipo_energia if tipo_energia in self.TIPOS_ENERGIA else "neutro"
        self.notificaciones = notificaciones
        self.tema_oscuro = tema_oscuro

    def get_factor_energia(self):
        factores = {
            "manana": 1.15,
            "tarde": 1.0,
            "noche": 0.85,
            "neutro": 1.0
        }
        return factores.get(self.tipo_energia, 1.0)

    def to_dict(self):
        return {
            "nombre": self.nombre,
            "tiempo_disponible": self.tiempo_disponible,
            "tipo_energia": self.tipo_energia,
            "notificaciones": self.notificaciones,
            "tema_oscuro": self.tema_oscuro
        }

    @staticmethod
    def from_dict(data):
        return Usuario(
            nombre=data.get("nombre", "Usuario"),
            tiempo_disponible=data.get("tiempo_disponible", 480),
            tipo_energia=data.get("tipo_energia", "neutro"),
            notificaciones=data.get("notificaciones", True),
            tema_oscuro=data.get("tema_oscuro", False)
        )
