import json
import os
from datetime import date


def get_data_dir():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def _cargar_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _guardar_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def cargar_todo(data_dir=None):
    if data_dir is None:
        data_dir = get_data_dir()
    tareas_path = os.path.join(data_dir, "tareas.json")
    historial_path = os.path.join(data_dir, "historial.json")
    return {
        "tareas": _cargar_json(tareas_path),
        "historial": _cargar_json(historial_path)
    }


def guardar_tareas(data, data_dir=None):
    if data_dir is None:
        data_dir = get_data_dir()
    _guardar_json(os.path.join(data_dir, "tareas.json"), data)


def guardar_historial(data, data_dir=None):
    if data_dir is None:
        data_dir = get_data_dir()
    _guardar_json(os.path.join(data_dir, "historial.json"), data)
