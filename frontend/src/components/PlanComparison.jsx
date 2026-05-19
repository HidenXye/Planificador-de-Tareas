import { formatTime } from '../utils/constants';
import { TrendingUp, Clock, CheckSquare, Zap, Award } from 'lucide-react';

export default function PlanComparison({ greedy, knapsack }) {
  const greedyData = greedy || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };
  const knapData = knapsack || { plan: [], tiempo_total: 0, prioridad_total: 0, tiempo_restante: 0 };

  const isKnapBetter = knapData.prioridad_total > greedyData.prioridad_total;
  const greedyBetter = greedyData.prioridad_total > knapData.prioridad_total;

  const renderPlan = (data, label, isBest) => (
    <div className={`card comparison-card ${isBest ? 'best' : ''}`}>
      {isBest && <div className="best-ribbon">Optimo</div>}
      <div className="card-header">
        <div className="card-header-icon">
          {label === 'Greedy' ? <Zap size={17} /> : <Award size={17} />}
          {label}
        </div>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          {label === 'Greedy' ? 'Aproximacion rapida' : 'Programacion dinamica'}
        </span>
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

  return (
    <div className="comparison-container">
      {renderPlan(greedyData, 'Greedy', greedyBetter)}
      {renderPlan(knapData, 'Knapsack DP', isKnapBetter)}
    </div>
  );
}
