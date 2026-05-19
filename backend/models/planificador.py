from datetime import date, timedelta
from .tarea import Tarea
from .usuario import Usuario


class PlanificadorTareas:
    def __init__(self, usuario=None):
        self.usuario = usuario or Usuario()
        self.tareas = []
        self.tareas_completadas = []
        self._contador_id = 0

    def agregar_tarea(self, tarea):
        if isinstance(tarea, dict):
            tarea = Tarea.from_dict(tarea)
        tarea.calcular_prioridad()
        self.tareas.append(tarea)
        self.tareas.sort(key=lambda t: t.prioridad, reverse=True)
        return tarea

    def eliminar_tarea(self, id_tarea):
        self.tareas = [t for t in self.tareas if t.id != id_tarea]
        self.tareas_completadas = [t for t in self.tareas_completadas if t.id != id_tarea]

    def obtener_tarea(self, id_tarea):
        for t in self.tareas:
            if t.id == id_tarea:
                return t
        for t in self.tareas_completadas:
            if t.id == id_tarea:
                return t
        return None

    def completar_tarea(self, id_tarea, tiempo_real=None):
        tarea = self.obtener_tarea(id_tarea)
        if tarea:
            tarea.marcar_completada(tiempo_real)
            self.tareas = [t for t in self.tareas if t.id != id_tarea]
            self.tareas_completadas.append(tarea)
            self._procesar_recurrencia(tarea)
            return tarea
        return None

    def _procesar_recurrencia(self, tarea):
        if not tarea.es_recurrente or tarea.frecuencia == "ninguna":
            return
        nueva = Tarea(
            nombre=tarea.nombre,
            tiempo_estimado=tarea.tiempo_estimado,
            importancia=tarea.importancia,
            urgencia=tarea.urgencia,
            categoria=tarea.categoria,
            descripcion=tarea.descripcion,
            dependencias=list(tarea.dependencias),
            subtareas=[st.to_dict() for st in tarea.subtareas],
            es_recurrente=True,
            frecuencia=tarea.frecuencia
        )
        delta = {"diario": 1, "semanal": 7, "mensual": 30}.get(tarea.frecuencia, 0)
        if tarea.fecha_limite:
            nueva.fecha_limite = tarea.fecha_limite + timedelta(days=delta)
        nueva.calcular_prioridad()
        self.tareas.append(nueva)

    def calcular_prioridades(self):
        for tarea in self.tareas:
            tarea.calcular_prioridad()
        self.tareas.sort(key=lambda t: t.prioridad, reverse=True)

    def filtrar_por_categoria(self, categoria):
        if categoria == "todas":
            return self.tareas
        return [t for t in self.tareas if t.categoria == categoria]

    def obtener_tareas_pendientes(self):
        return [t for t in self.tareas if not t.completada]

    def generar_plan_greedy(self):
        from algorithms.greedy_planner import greedy_plan
        return greedy_plan(self.obtener_tareas_pendientes(), self.usuario.tiempo_disponible)

    def generar_plan_knapsack(self):
        from algorithms.knapsack_dp import knapsack_plan
        return knapsack_plan(self.obtener_tareas_pendientes(), self.usuario.tiempo_disponible)

    def generar_planes_backtracking(self, top_n=3):
        from algorithms.backtracking_planner import backtracking_plans
        return backtracking_plans(self.obtener_tareas_pendientes(),
                                  self.usuario.tiempo_disponible, top_n)

    def verificar_alertas(self):
        alertas = []
        pendientes = self.obtener_tareas_pendientes()
        tiempo_total = sum(t.tiempo_estimado for t in pendientes)
        hoy = date.today()

        for tarea in pendientes:
            if tarea.fecha_limite and (tarea.fecha_limite - hoy).days <= 1:
                alertas.append({
                    "tipo": "urgente",
                    "tarea": tarea.to_dict(),
                    "mensaje": f"Tarea '{tarea.nombre}' vence en menos de 24 horas"
                })

        if tiempo_total > self.usuario.tiempo_disponible:
            alertas.append({
                "tipo": "sobrecarga",
                "tareas_pendientes": len(pendientes),
                "tiempo_requerido": tiempo_total,
                "tiempo_disponible": self.usuario.tiempo_disponible,
                "mensaje": (f"Tiempo requerido ({tiempo_total} min) excede "
                            f"el disponible ({self.usuario.tiempo_disponible} min)")
            })

        return alertas

    def verificar_dependencias(self):
        from algorithms.topological_sort import orden_topologico
        pendientes = self.obtener_tareas_pendientes()
        return orden_topologico(pendientes)

    def clasificar_eisenhower(self):
        cuadrantes = {"q1": [], "q2": [], "q3": [], "q4": []}
        pendientes = self.obtener_tareas_pendientes()
        for t in pendientes:
            urgente = (t.fecha_limite is not None and
                       (t.fecha_limite - date.today()).days <= 2)
            importante = t.importancia >= 4
            if urgente and importante:
                cuadrantes["q1"].append(t.to_dict())
            elif not urgente and importante:
                cuadrantes["q2"].append(t.to_dict())
            elif urgente and not importante:
                cuadrantes["q3"].append(t.to_dict())
            else:
                cuadrantes["q4"].append(t.to_dict())
        return cuadrantes

    def to_dict(self):
        return {
            "usuario": self.usuario.to_dict(),
            "tareas_pendientes": [t.to_dict() for t in self.obtener_tareas_pendientes()],
            "tareas_completadas": [t.to_dict() for t in self.tareas_completadas],
            "total_pendientes": len(self.obtener_tareas_pendientes()),
            "total_completadas": len(self.tareas_completadas)
        }

    def cargar_desde_dict(self, data):
        self.usuario = Usuario.from_dict(data.get("usuario", {}))
        self.tareas = []
        self.tareas_completadas = []
        for td in data.get("tareas_pendientes", []):
            t = Tarea.from_dict(td)
            t.calcular_prioridad()
            self.tareas.append(t)
        for td in data.get("tareas_completadas", []):
            t = Tarea.from_dict(td)
            self.tareas_completadas.append(t)
        self.tareas.sort(key=lambda t: t.prioridad, reverse=True)
