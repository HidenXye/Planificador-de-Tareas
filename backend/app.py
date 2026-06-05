import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from tipos import Tarea, Usuario, Estado
from funciones import (
    tarea_to_dict, tarea_from_dict, usuario_to_dict, usuario_from_dict,
    calcular_prioridad, toggle_subtarea_de_tarea, agregar_subtarea_a_tarea
)
from planificador_funcional import (
    estado_from_dict, estado_to_dict,
    agregar_tarea, eliminar_tarea, completar_tarea_estado, obtener_tarea,
    tareas_pendientes, filtrar_por_categoria,
    generar_plan_greedy, generar_plan_knapsack, generar_planes_backtracking,
    generar_plan_genetic,
    verificar_alertas, clasificar_eisenhower, calcular_metricas,
    actualizar_usuario
)
from services import data_service, export_service

app = Flask(__name__)
CORS(app)

estado_actual = Estado()


def cargar_datos():
    global estado_actual
    datos = data_service.cargar_todo()
    estado_actual = estado_from_dict(datos.get("tareas", {}))
    if datos.get("historial", {}).get("historial_diario"):
        from dataclasses import replace
        estado_actual = replace(
            estado_actual,
            historial_diario=datos["historial"]["historial_diario"]
        )


def guardar_datos():
    data_service.guardar_tareas(estado_to_dict(estado_actual))
    data_service.guardar_historial({
        "historial_diario": estado_actual.historial_diario
    })


cargar_datos()


# ---- Endpoints ----

@app.route("/api/tareas", methods=["GET"])
def listar_tareas():
    categoria = request.args.get("categoria", "todas")
    q = request.args.get("q", "").lower()
    orden = request.args.get("orden", "prioridad")

    tareas = list(filtrar_por_categoria(estado_actual, categoria))
    tareas = [t for t in tareas if not t.completada]

    if q:
        tareas = [t for t in tareas
                  if q in t.nombre.lower() or q in t.descripcion.lower()]

    if orden == "fecha":
        tareas.sort(key=lambda t: (
            t.fecha_limite is None, t.fecha_limite or ""))
    elif orden == "tiempo":
        tareas.sort(key=lambda t: t.tiempo_estimado)
    else:
        tareas.sort(key=lambda t: t.prioridad, reverse=True)

    return jsonify({
        "tareas": list(map(tarea_to_dict, tareas)),
        "total": len(tareas),
        "completadas": list(map(tarea_to_dict, estado_actual.tareas_completadas))
    })


@app.route("/api/tareas", methods=["POST"])
def crear_tarea():
    data = request.get_json()
    if not data or "nombre" not in data:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

    global estado_actual
    tarea = tarea_from_dict(data)
    estado_actual = agregar_tarea(estado_actual, tarea)
    guardar_datos()

    tarea_guardada = obtener_tarea(estado_actual, tarea.id)
    return jsonify({"tarea": tarea_to_dict(tarea_guardada)}), 201


@app.route("/api/tareas/<id_tarea>", methods=["PUT"])
def editar_tarea(id_tarea):
    global estado_actual
    data = request.get_json()
    existente = obtener_tarea(estado_actual, id_tarea)
    if not existente:
        return jsonify({"error": "Tarea no encontrada"}), 404

    estado_actual = eliminar_tarea(estado_actual, id_tarea)

    tarea = tarea_from_dict(data)
    tarea = calcular_prioridad(tarea)

    if data.get("completada", False):
        from dataclasses import replace
        tarea = replace(tarea, completada=True)
        estado_actual = replace(
            estado_actual,
            tareas_completadas=estado_actual.tareas_completadas + (tarea,)
        )
    else:
        estado_actual = agregar_tarea(estado_actual, tarea)

    guardar_datos()
    return jsonify({"tarea": tarea_to_dict(tarea)})


@app.route("/api/tareas/<id_tarea>", methods=["DELETE"])
def endpoint_eliminar_tarea(id_tarea):
    global estado_actual
    tarea = obtener_tarea(estado_actual, id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    estado_actual = eliminar_tarea(estado_actual, id_tarea)
    guardar_datos()
    return jsonify({"ok": True, "mensaje": f"Tarea '{tarea.nombre}' eliminada"})


@app.route("/api/tareas/<id_tarea>/completar", methods=["POST"])
def endpoint_completar_tarea(id_tarea):
    data = request.get_json() or {}
    tiempo_real = data.get("tiempo_real")

    global estado_actual
    nuevo = completar_tarea_estado(estado_actual, id_tarea, tiempo_real)
    if nuevo is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    estado_actual = nuevo
    guardar_datos()

    tarea_comp = obtener_tarea(estado_actual, id_tarea)
    return jsonify({
        "tarea": tarea_to_dict(tarea_comp) if tarea_comp else None,
        "racha": calcular_metricas(estado_actual)["racha"],
        "metricas": calcular_metricas(estado_actual)
    })


@app.route("/api/tareas/<id_tarea>/sub/<id_sub>/toggle", methods=["POST"])
def endpoint_toggle_subtarea(id_tarea, id_sub):
    global estado_actual
    tarea = obtener_tarea(estado_actual, id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    nueva_tarea = toggle_subtarea_de_tarea(tarea, id_sub)
    if nueva_tarea is None:
        return jsonify({"error": "Subtarea no encontrada"}), 404

    nueva_tarea = calcular_prioridad(nueva_tarea)

    estado_actual = eliminar_tarea(estado_actual, id_tarea)
    if nueva_tarea.completada:
        from dataclasses import replace
        estado_actual = replace(
            estado_actual,
            tareas_completadas=estado_actual.tareas_completadas + (nueva_tarea,)
        )
    else:
        estado_actual = agregar_tarea(estado_actual, nueva_tarea)
    guardar_datos()

    from funciones import subtarea_to_dict
    for st in nueva_tarea.subtareas:
        if st.id == id_sub:
            return jsonify({
                "subtarea": subtarea_to_dict(st),
                "progreso": int(
                    sum(1 for s in nueva_tarea.subtareas if s.completada) /
                    max(len(nueva_tarea.subtareas), 1) * 100
                )
            })
    return jsonify({"error": "Subtarea no encontrada"}), 404


@app.route("/api/tareas/<id_tarea>/sub", methods=["POST"])
def endpoint_agregar_subtarea(id_tarea):
    global estado_actual
    data = request.get_json()
    tarea = obtener_tarea(estado_actual, id_tarea)
    if not tarea:
        return jsonify({"error": "Tarea no encontrada"}), 404

    nueva_tarea = agregar_subtarea_a_tarea(
        tarea, data.get("nombre", "Nueva subtarea"))
    nueva_tarea = calcular_prioridad(nueva_tarea)
    estado_actual = eliminar_tarea(estado_actual, id_tarea)
    estado_actual = agregar_tarea(estado_actual, nueva_tarea)
    guardar_datos()

    from funciones import subtarea_to_dict
    return jsonify({
        "subtarea": subtarea_to_dict(nueva_tarea.subtareas[-1])
    }), 201


@app.route("/api/plan", methods=["GET"])
def obtener_plan():
    tipo = request.args.get("tipo", "todos")
    resultado = {}

    if tipo in ("greedy", "todos"):
        resultado["greedy"] = generar_plan_greedy(estado_actual)
    if tipo in ("knapsack", "todos"):
        resultado["knapsack"] = generar_plan_knapsack(estado_actual)
    if tipo in ("backtracking", "todos"):
        resultado["backtracking"] = generar_planes_backtracking(
            estado_actual, top_n=3
        )
    if tipo in ("genetic", "todos"):
        resultado["genetic"] = generar_plan_genetic(estado_actual)

    return jsonify(resultado)


@app.route("/api/plan/export", methods=["GET"])
def exportar_plan():
    tipo = request.args.get("tipo", "knapsack")
    plan = (generar_plan_greedy(estado_actual) if tipo == "greedy"
            else generar_plan_knapsack(estado_actual))
    csv_data = export_service.plan_to_csv(plan,
                                          nombre_plan=tipo.capitalize())
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            f"attachment; filename=plan_{tipo}.csv"
        }
    )


@app.route("/api/metricas", methods=["GET"])
def obtener_metricas():
    metricas = calcular_metricas(estado_actual)
    pendientes = tareas_pendientes(estado_actual)
    metricas["tareas_pendientes"] = len(pendientes)
    metricas["tiempo_pendiente"] = sum(t.tiempo_estimado for t in pendientes)
    metricas["tiempo_disponible"] = estado_actual.usuario.tiempo_disponible
    return jsonify(metricas)


@app.route("/api/alertas", methods=["GET"])
def obtener_alertas():
    return jsonify({"alertas": verificar_alertas(estado_actual)})


@app.route("/api/historial", methods=["GET"])
def obtener_historial():
    return jsonify({
        "historial_diario": estado_actual.historial_diario,
        "metricas": calcular_metricas(estado_actual)
    })


@app.route("/api/eisenhower", methods=["GET"])
def obtener_eisenhower():
    return jsonify(clasificar_eisenhower(estado_actual))


@app.route("/api/usuario", methods=["GET"])
def obtener_usuario():
    return jsonify(usuario_to_dict(estado_actual.usuario))


@app.route("/api/usuario", methods=["PUT"])
def actualizar_usuario_endpoint():
    data = request.get_json()
    global estado_actual
    estado_actual = actualizar_usuario(
        estado_actual, usuario_from_dict(data))
    guardar_datos()
    return jsonify(usuario_to_dict(estado_actual.usuario))


@app.route("/api/export/tareas", methods=["GET"])
def exportar_tareas_csv():
    todas = list(estado_actual.tareas_pendientes) + \
            list(estado_actual.tareas_completadas)
    csv_data = export_service.tareas_to_csv(
        list(map(tarea_to_dict, todas)))
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition":
                 "attachment; filename=tareas.csv"}
    )


@app.route("/api/export/historial", methods=["GET"])
def exportar_historial_csv():
    csv_data = export_service.historial_to_csv(
        estado_actual.historial_diario
    )
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition":
                 "attachment; filename=historial.csv"}
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
