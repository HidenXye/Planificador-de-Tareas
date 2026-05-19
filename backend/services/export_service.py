import csv
import io


def tareas_to_csv(tareas):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Nombre", "Categoria", "Prioridad", "Tiempo Estimado (min)",
        "Importancia", "Urgencia", "Fecha Limite", "Completada"
    ])
    for t in tareas:
        writer.writerow([
            t.get("nombre", ""),
            t.get("categoria", ""),
            t.get("prioridad", ""),
            t.get("tiempo_estimado", ""),
            t.get("importancia", ""),
            t.get("urgencia", ""),
            t.get("fecha_limite", ""),
            "Si" if t.get("completada") else "No"
        ])
    return output.getvalue()


def plan_to_csv(plan_data, nombre_plan="Plan"):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Orden", "Nombre", "Categoria", "Prioridad",
        "Tiempo Estimado (min)", "Fecha Limite"
    ])
    for i, t in enumerate(plan_data.get("plan", []), 1):
        writer.writerow([
            i,
            t.get("nombre", ""),
            t.get("categoria", ""),
            t.get("prioridad", ""),
            t.get("tiempo_estimado", ""),
            t.get("fecha_limite", "")
        ])
    writer.writerow([])
    writer.writerow(["Resumen"])
    writer.writerow(["Tiempo total usado",
                     f"{plan_data.get('tiempo_total', 0)} min"])
    writer.writerow(["Prioridad total", plan_data.get("prioridad_total", 0)])
    writer.writerow(["Tareas incluidas", plan_data.get("tareas_incluidas", 0)])
    writer.writerow(["Tiempo restante",
                     f"{plan_data.get('tiempo_restante', 0)} min"])
    return output.getvalue()


def historial_to_csv(historial_diario):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Tareas Completadas", "Tiempo Total (min)"])
    for f_str in sorted(historial_diario.keys()):
        tareas = historial_diario[f_str]
        num = len(tareas)
        tiempo = sum(
            (t.get("tiempo_real") or t.get("tiempo_estimado", 0))
            for t in tareas
        )
        writer.writerow([f_str, num, tiempo])
    return output.getvalue()
