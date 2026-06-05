# Planificador Inteligente de Tareas

Planifica tu día automáticamente usando cuatro algoritmos de optimización comparados lado a lado. Desarrollado bajo programación funcional pura en Python.

## ¿Qué hace?

- Prioriza tareas según urgencia, importancia y tiempo estimado
- Genera un plan diario optimizado con Greedy, Knapsack DP, Backtracking y Algoritmo Genético
- Clasifica tareas en matriz Eisenhower
- Muestra métricas, rachas e historial con gráficos
- Exporta planes a CSV

## Algoritmos

| Algoritmo | Complejidad | ¿Óptimo? |
|-----------|-------------|----------|
| Greedy | O(n log n) | No |
| Knapsack DP | O(n·T) | Sí |
| Backtracking | O(2ⁿ) con poda | Sí |
| Algoritmo Genético | O(G·N·n) | Aproximado |

## Stack

Backend → Python 3.10 + Flask + dataclasses inmutables  
Frontend → React 18 + Vite + Chart.js  
Datos → JSON plano

## Requisitos

- Python 3.10 o superior
- Node.js 18 o superior

## Estructura

```
backend/
├── algorithms/       # greedy, knapsack, backtracking, genetic
├── services/         # persistencia JSON y exportación CSV
├── tipos.py          # dataclasses inmutables (Tarea, Usuario, Estado)
├── funciones.py      # funciones puras de transformación
├── planificador_funcional.py
├── app.py            # API Flask
└── data/             # tareas.json, historial.json

frontend/
└── src/
    ├── components/   # PlanComparison, EisenhowerMatrix, TaskCard
    ├── pages/        # Dashboard, PlanPage, History, Summary
    ├── api/          # cliente HTTP
    └── hooks/        # useDarkMode
```

## Cómo correrlo

```bash
cd backend && pip install -r requirements.txt && python app.py
cd frontend && npm install && npm run dev
```

Backend en `localhost:5000` · Frontend en `localhost:3000`
