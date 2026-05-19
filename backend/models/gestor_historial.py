from datetime import date, datetime, timedelta
from collections import defaultdict


class GestorHistorial:
    def __init__(self):
        self.historial_diario = {}

    def registrar_dia(self, fecha_str, tareas_completadas):
        fecha = self._parse_fecha(fecha_str)
        self.historial_diario[fecha] = [t.to_dict() if hasattr(t, 'to_dict') else t
                                         for t in tareas_completadas]

    def _parse_fecha(self, fecha_str):
        if isinstance(fecha_str, date):
            return fecha_str.isoformat()
        if isinstance(fecha_str, datetime):
            return fecha_str.date().isoformat()
        if isinstance(fecha_str, str):
            try:
                return datetime.strptime(fecha_str, "%Y-%m-%d").date().isoformat()
            except ValueError:
                return date.today().isoformat()
        return date.today().isoformat()

    def calcular_racha(self):
        if not self.historial_diario:
            return 0
        fechas = sorted(self.historial_diario.keys(), reverse=True)
        racha = 0
        hoy = date.today()
        for i, f_str in enumerate(fechas):
            f = date.fromisoformat(f_str)
            dia_esperado = hoy - timedelta(days=i)
            if f == dia_esperado:
                racha += 1
            else:
                break
        return racha

    def calcular_metricas(self):
        if not self.historial_diario:
            return self._metricas_vacias()

        dias_ultima_semana = []
        hoy = date.today()
        for i in range(7):
            f = (hoy - timedelta(days=i)).isoformat()
            tareas = self.historial_diario.get(f, [])
            dias_ultima_semana.append({
                "fecha": f,
                "tareas_completadas": len(tareas),
                "tiempo_total": sum(t.get("tiempo_real", t.get("tiempo_estimado", 0))
                                    for t in tareas)
            })

        hoy_str = hoy.isoformat()
        tareas_hoy = self.historial_diario.get(hoy_str, [])
        completadas_hoy = len(tareas_hoy)

        total_minutos = sum(
            t.get("tiempo_real", t.get("tiempo_estimado", 0))
            for dia_data in self.historial_diario.values()
            for t in dia_data
        )
        total_tareas = sum(len(v) for v in self.historial_diario.values())
        tiempo_promedio = total_minutos / total_tareas if total_tareas > 0 else 0

        return {
            "completadas_hoy": completadas_hoy,
            "racha": self.calcular_racha(),
            "dias_ultima_semana": dias_ultima_semana,
            "tiempo_promedio_real": round(tiempo_promedio, 1),
            "total_tareas_historial": total_tareas
        }

    def _metricas_vacias(self):
        return {
            "completadas_hoy": 0,
            "racha": 0,
            "dias_ultima_semana": [],
            "tiempo_promedio_real": 0,
            "total_tareas_historial": 0
        }

    def predecir_tiempo(self, tarea_nombre):
        tiempos_reales = []
        for dia_data in self.historial_diario.values():
            for t in dia_data:
                if t.get("nombre") == tarea_nombre and t.get("tiempo_real"):
                    tiempos_reales.append(t["tiempo_real"])
        if not tiempos_reales:
            return None
        return round(sum(tiempos_reales) / len(tiempos_reales), 1)

    def to_dict(self):
        return {
            "historial_diario": self.historial_diario,
            "metricas": self.calcular_metricas()
        }

    @staticmethod
    def from_dict(data):
        gh = GestorHistorial()
        gh.historial_diario = data.get("historial_diario", {})
        return gh

    def exportar_csv(self):
        if not self.historial_diario:
            return "fecha,tareas,tiempo_total\n"
        lineas = ["fecha,tareas,tiempo_total"]
        for f_str in sorted(self.historial_diario.keys()):
            tareas = self.historial_diario[f_str]
            num = len(tareas)
            tiempo = sum(t.get("tiempo_real", t.get("tiempo_estimado", 0)) for t in tareas)
            lineas.append(f"{f_str},{num},{tiempo}")
        return "\n".join(lineas)
