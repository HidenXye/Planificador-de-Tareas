import { useState, useEffect } from 'react';
import { api } from '../api/api';
import Layout from '../components/Layout';
import PlanComparison from '../components/PlanComparison';
import { CalendarCheck, Download, RefreshCw, Sparkles } from 'lucide-react';

export default function PlanPage() {
  const [planData, setPlanData] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadPlan = async () => {
    setLoading(true);
    try {
      const data = await api.plan.get('todos');
      setPlanData(data);
    } catch (err) {
      console.error('Error generando plan:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadPlan(); }, []);

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Plan Diario</h1>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Comparacion de algoritmos de planificacion
          </div>
        </div>
        <div className="btn-group">
          <a href={api.plan.export('knapsack')} className="btn btn-outline btn-sm" target="_blank" rel="noreferrer">
            <Download size={14} /> Exportar CSV
          </a>
          <button className="btn btn-primary btn-sm" onClick={loadPlan}>
            <RefreshCw size={14} /> Regenerar
          </button>
        </div>
      </div>

      {loading ? (
        <div className="empty-state">
          <Sparkles size={40} />
          <h3>Generando plan optimizado</h3>
          <p>Ejecutando algoritmos Greedy, Knapsack DP, Backtracking y Algoritmo Genetico...</p>
        </div>
      ) : planData ? (
        <>
          <PlanComparison
            greedy={planData.greedy}
            knapsack={planData.knapsack}
            genetic={planData.genetic}
            backtracking={planData.backtracking}
          />

          {planData.backtracking && planData.backtracking.length > 0 && (
            <div className="card" style={{ marginTop: '1.25rem' }}>
              <div className="card-header">
                <div className="card-header-icon">
                  <CalendarCheck size={17} /> Top 3 Planes (Backtracking)
                </div>
              </div>
              <div className="top-plan-selector">
                {planData.backtracking.slice(0, 3).map((p, i) => (
                  <div key={i} className={`top-plan-card ${i === 0 ? 'best' : ''}`}>
                    <h4>
                      {i === 0 ? <Sparkles size={14} style={{ color: 'var(--success)' }} /> :
                       i === 1 ? <CalendarCheck size={14} /> :
                       <CalendarCheck size={14} />}
                      Plan #{i + 1}
                    </h4>
                    <div className="top-plan-meta">
                      <span>P: {p.prioridad_total}</span>
                      <span>{p.tiempo_total} min</span>
                      <span>{p.tareas_incluidas} tareas</span>
                    </div>
                    <ul style={{ fontSize: '0.78rem', paddingLeft: '0', listStyle: 'none' }}>
                      {p.plan.map(t => (
                        <li key={t.id} style={{ padding: '0.2rem 0', color: 'var(--text-secondary)' }}>
                          {t.nombre} ({t.tiempo_estimado}m)
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="empty-state">
          <CalendarCheck size={40} />
          <h3>No se pudo generar el plan</h3>
          <p>Verifica que tengas tareas pendientes y tiempo disponible configurado.</p>
        </div>
      )}
    </Layout>
  );
}
