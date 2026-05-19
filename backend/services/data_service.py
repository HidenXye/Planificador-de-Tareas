import json
import os
from datetime import date


class DataService:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.tareas_path = os.path.join(data_dir, "tareas.json")
        self.historial_path = os.path.join(data_dir, "historial.json")

    def cargar_todo(self):
        tareas_data = self._cargar_json(self.tareas_path)
        historial_data = self._cargar_json(self.historial_path)
        return {
            "tareas": tareas_data,
            "historial": historial_data
        }

    def guardar_tareas(self, data):
        self._guardar_json(self.tareas_path, data)

    def guardar_historial(self, data):
        self._guardar_json(self.historial_path, data)

    def _cargar_json(self, path):
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _guardar_json(self, path, data):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def registrar_dia_completado(self, tareas_completadas):
        hoy = date.today().isoformat()
        historial = self._cargar_json(self.historial_path)
        if "historial_diario" not in historial:
            historial["historial_diario"] = {}
        historial["historial_diario"][hoy] = [
            t.to_dict() if hasattr(t, 'to_dict') else t
            for t in tareas_completadas
        ]
        self._guardar_json(self.historial_path, historial)
