import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from models.tarea import Tarea
from models.usuario import Usuario
from models.planificador import PlanificadorTareas
from models.gestor_historial import GestorHistorial
from services.data_service import DataService
from services.export_service import ExportService

app = Flask(__name__)
CORS(app)

data_service = DataService()
planificador = PlanificadorTareas()
gestor_historial = GestorHistorial()


def cargar_datos():
    global planificador, gestor_historial
    datos = data_service.cargar_todo()
    planificador.cargar_desde_dict(datos.get("tareas", {}))
    gestor_historial = GestorHistorial.from_dict(datos.get("historial", {}))


def guardar_datos():
    data_service.guardar_tareas(planificador.to_dict())
    data_service.guardar_historial(gestor_historial.to_dict())


cargar_datos()


@app.route("/api/tareas", methods=["GET"])
def listar_tareas():
    categoria = request.args.get("categoria", "todas")
    q = request.args.get("q", "").lower()
    orden = request.args.get("orden", "prioridad")

    tareas = planificador.filtrar_por_categoria(categoria)
    tareas = [t for t in tareas if not t.completada]

    if q:
        tareas = [t for t in tareas
                  if q in t.nombre.lower() or q in t.descripcion.lower()]

    if orden == "fecha":
        tareas.sort(key=lambda t: (t.fecha_limite is None, t.fecha_limite or ""))
    elif orden == "tiempo":
        tareas.sort(key=lambda t: t.tiempo_estimado)
    else:
        tareas.sort(key=lambda t: t.prioridad, reverse=True)

    return jsonify({
        "tareas": [t.to_dict() for t in tareas],
        "total": len(tareas),
        "completadas": [t.to_dict() for t in planificador.tareas_completadas]
    })


@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    data = request.get_json()
    if not data or "nombre" not in data:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400
    tarea = Tarea.from_dict(data)
    planificador.agregar_tarea(tarea)
    guardar_datos()
    return jsonify({"tarea": tarea.to_dict()}), 201


@app.route("/api/tareas/<id_tarea>", methods=["PUT"])
def editar_tarea(id_tarea):
    data = request.get_json()
    tarea_existente = planificador.obtener_tarea(id_tarea)
    if not tarea_existente:
        return jsonify({"error": "Tarea no encontrada"}), 404
    planificador.eliminar_tarea(id_tarea)
    updated = Tarea.from_dict(data)
    updated.id = id_tarea
    if data.get("completada", False):
        planificador.tareas_completadas.append(updated)
        updated.calcular_prioridad()
    else:
        planificador.agregar_tarea(updated)
    guardar_datos()
    return jsonify({"tarea": updated.to_dict()})


@app.route("/api/tareas/<id_tarea>", methods=["DELETE"])
def eliminar_tarea(id_tarea):
    tarea = planificador.obtener_tarea(id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    planificador.eliminar_tarea(id_tarea)
    guardar_datos()
    return jsonify({"ok": True, "mensaje": f"Tarea '{tarea.nombre}' eliminada"})


@app.route("/api/tareas/<id_tarea>/completar", methods=["POST"])
def completar_tarea(id_tarea):
    data = request.get_json() or {}
    tiempo_real = data.get("tiempo_real")
    tarea = planificador.completar_tarea(id_tarea, tiempo_real)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    gestor_historial.registrar_dia("", [tarea])
    guardar_datos()
    return jsonify({
        "tarea": tarea.to_dict(),
        "racha": gestor_historial.calcular_racha(),
        "metricas": gestor_historial.calcular_metricas()
    })


@app.route("/api/tareas/<id_tarea>/sub/<id_sub>/toggle", methods=["POST"])
def toggle_subtarea(id_tarea, id_sub):
    tarea = planificador.obtener_tarea(id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    for st in tarea.subtareas:
        if st.id == id_sub:
            st.toggle()
            tarea.calcular_prioridad()
            guardar_datos()
            return jsonify({"subtarea": st.to_dict(), "progreso": tarea.progreso_subtareas()})
    return jsonify({"error": "Subtarea no encontrada"}), 404


@app.route("/api/tareas/<id_tarea>/sub", methods=["POST"])
def agregar_subtarea(id_tarea):
    data = request.get_json()
    tarea = planificador.obtener_tarea(id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404
    st = tarea.agregar_subtarea(data.get("nombre", "Nueva subtarea"))
    guardar_datos()
    return jsonify({"subtarea": st.to_dict()}), 201


@app.route("/api/plan", methods=["GET"])
def obtener_plan():
    tipo = request.args.get("tipo", "todos")
    resultado = {}

    if tipo in ("greedy", "todos"):
        resultado["greedy"] = planificador.generar_plan_greedy()
    if tipo in ("knapsack", "todos"):
        resultado["knapsack"] = planificador.generar_plan_knapsack()
    if tipo in ("backtracking", "todos"):
        resultado["backtracking"] = planificador.generar_planes_backtracking(top_n=3)

    return jsonify(resultado)


@app.route("/api/plan/export", methods=["GET"])
def exportar_plan():
    tipo = request.args.get("tipo", "knapsack")
    if tipo == "greedy":
        plan = planificador.generar_plan_greedy()
    else:
        plan = planificador.generar_plan_knapsack()
    csv_data = ExportService.plan_to_csv(plan, nombre_plan=tipo.capitalize())
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename=plan_{tipo}.csv"}
    )


@app.route("/api/metricas", methods=["GET"])
def obtener_metricas():
    metricas = gestor_historial.calcular_metricas()
    metricas["tareas_pendientes"] = len(planificador.obtener_tareas_pendientes())
    metricas["tiempo_pendiente"] = sum(
        t.tiempo_estimado for t in planificador.obtener_tareas_pendientes()
    )
    metricas["tiempo_disponible"] = planificador.usuario.tiempo_disponible
    return jsonify(metricas)


@app.route("/api/alertas", methods=["GET"])
def obtener_alertas():
    return jsonify({"alertas": planificador.verificar_alertas()})


@app.route("/api/historial", methods=["GET"])
def obtener_historial():
    return jsonify(gestor_historial.to_dict())


@app.route("/api/eisenhower", methods=["GET"])
def obtener_eisenhower():
    return jsonify(planificador.clasificar_eisenhower())


@app.route("/api/usuario", methods=["GET"])
def obtener_usuario():
    return jsonify(planificador.usuario.to_dict())


@app.route("/api/usuario", methods=["PUT"])
def actualizar_usuario():
    data = request.get_json()
    planificador.usuario = Usuario.from_dict(data)
    guardar_datos()
    return jsonify(planificador.usuario.to_dict())


@app.route("/api/export/tareas", methods=["GET"])
def exportar_tareas_csv():
    tareas = planificador.tareas + planificador.tareas_completadas
    csv_data = ExportService.tareas_to_csv([t.to_dict() for t in tareas])
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=tareas.csv"}
    )


@app.route("/api/export/historial", methods=["GET"])
def exportar_historial_csv():
    csv_data = ExportService.historial_to_csv(
        gestor_historial.historial_diario
    )
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=historial.csv"}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
