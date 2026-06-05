import { formatTime } from '../utils/constants';
import { TrendingUp, Clock, CheckSquare, Zap, Award, Dna, GitBranch } from 'lucide-react';

export default function PlanComparison({ greedy, knapsack, backtracking, genetic }) {
  const greedyData = greedy || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };
  const knapData = knapsack || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };
  const geneticData = genetic || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };
  const backtrackPlans = backtracking || [];
  const backtrackData = backtrackPlans[0] || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };

  const allPlans = [
    { data: greedyData, label: 'Greedy', sub: 'Aproximacion rapida', icon: Zap, key: 'greedy' },
    { data: knapData, label: 'Knapsack DP', sub: 'Programacion dinamica', icon: Award, key: 'knapsack' },
    { data: geneticData, label: 'Algoritmo Genetico', sub: 'Evolutivo', icon: Dna, key: 'genetic' },
    { data: backtrackData, label: 'Backtracking', sub: 'Exhaustivo con poda', icon: GitBranch, key: 'backtrack' }
  ];

  const maxPriority = Math.max(...allPlans.map(p => p.data.prioridad_total));

  const renderPlan = ({ data, label, sub, icon: Icon, key }) => {
    const isBest = data.prioridad_total >= maxPriority && data.prioridad_total > 0;
    return (
      <div key={key} className={`card comparison-card ${isBest ? 'best' : ''}`}>
        {isBest && <div className="best-ribbon">Optimo</div>}
        <div className="card-header">
          <div className="card-header-icon">
            <Icon size={17} />
            {label}
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{sub}</span>
        </div>

        <div className="plan-details">
          <div className="plan-metric">
            <div className="plan-metric-value">{data.prioridad_total}</div>
            <div className="plan-metric-label">Prioridad Total</div>
          </div>
          <div className="plan-metric">
            <div className="plan-metric-value">{formatTime(data.tiempo_total)}</div>
            <div className="plan-metric-label">Tiempo Usado</div>
          </div>
          <div className="plan-metric">
            <div className="plan-metric-value">{data.plan.length}</div>
            <div className="plan-metric-label">Tareas</div>
          </div>
        </div>

        {data.tiempo_restante !== undefined && (
          <div className="occupancy-meter">
            <div className="occupancy-bar">
              <div
                className={`occupancy-fill ${data.tiempo_restante < 60 ? 'danger' : data.tiempo_restante < 120 ? 'warn' : 'safe'}`}
                style={{ width: `${Math.min(100, (data.tiempo_total / (data.tiempo_disponible || 480)) * 100)}%` }}
              />
            </div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.2rem', textAlign: 'right' }}>
              {formatTime(data.tiempo_restante)} disponible
            </div>
          </div>
        )}

        {data.plan.length === 0 ? (
          <div className="empty-state" style={{ padding: '1.5rem' }}>
            <p>Sin tareas para planificar</p>
          </div>
        ) : (
          <ul className="plan-list">
            {data.plan.map((t, i) => (
              <li key={i}>
                <div className="plan-index">{i + 1}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 600, fontSize: '0.82rem' }}>{t.nombre}</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                    <span className={`badge badge-${t.categoria}`}>{t.categoria}</span>
                    <span>{formatTime(t.tiempo_estimado)}</span>
                    <span>P:{t.prioridad}</span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div className="comparison-container">
        {allPlans.map(renderPlan)}
      </div>
      {backtrackPlans.length > 1 && (
        <div style={{ marginTop: '0.5rem' }}>
          <h4 style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
            Alternativas Backtracking (Top {backtrackPlans.length})
          </h4>
          <div style={{ display: 'flex', gap: '0.5rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
            {backtrackPlans.slice(1).map((plan, i) => (
              <div key={i} className="card" style={{ minWidth: '180px', padding: '0.75rem' }}>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                  Alternativa {i + 2}
                </div>
                <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{plan.prioridad_total}</div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>
                  {plan.tareas_incluidas} tareas / {formatTime(plan.tiempo_total)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}