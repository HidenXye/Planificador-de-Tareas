import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/api';
import { formatTime } from '../utils/constants';
import Layout from '../components/Layout';
import EisenhowerMatrix from '../components/EisenhowerMatrix';
import AlertPanel from '../components/AlertPanel';
import { BarChart3, Clock, CheckSquare, Timer, Sparkles, ListTodo, Plus, ArrowRight } from 'lucide-react';

function getGreeting() {
  const h = new Date().getHours();
  if (h < 12) return 'Buenos dias';
  if (h < 18) return 'Buenas tardes';
  return 'Buenas noches';
}

export default function Dashboard() {
  const [eisenhower, setEisenhower] = useState({ q1: [], q2: [], q3: [], q4: [] });
  const [alertas, setAlertas] = useState([]);
  const [metricas, setMetricas] = useState(null);
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const [e, a, m, p] = await Promise.all([
        api.eisenhower(), api.alertas(), api.metricas(),
        api.plan.get('greedy'),
      ]);
      setEisenhower(e);
      setAlertas(a.alertas);
      setMetricas(m);
      setPlan(p.greedy || null);
    } catch (err) {
      console.error('Error cargando dashboard:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  if (loading) {
    return (
      <Layout>
        <div className="empty-state">
          <Sparkles size={40} />
          <h3>Preparando tu panel</h3>
          <p>Cargando datos del planificador...</p>
        </div>
      </Layout>
    );
  }

  const pendientes = metricas?.tareas_pendientes || 0;
  const tiempoPendiente = metricas?.tiempo_pendiente || 0;
  const tiempoDisp = metricas?.tiempo_disponible || 480;
  const porcentajeOcupado = tiempoDisp > 0 ? Math.round((tiempoPendiente / tiempoDisp) * 100) : 0;

  return (
    <Layout>
      <div className="page-header">
        <div className="page-header-left">
          <div className="greeting">{getGreeting()},</div>
          <h1 className="page-title">Panel de Control</h1>
        </div>
        <Link to="/tareas/agregar" className="btn btn-primary">
          <Plus size={16} /> Nueva Tarea
        </Link>
      </div>

      <AlertPanel alertas={alertas} />

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--warning-bg)' }}>
            <Sparkles size={20} style={{ color: 'var(--warning)' }} />
          </div>
          <div>
            <div className="stat-value">{metricas?.racha || 0}</div>
            <div className="stat-label">Racha de dias</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--primary-bg)' }}>
            <ListTodo size={20} style={{ color: 'var(--primary)' }} />
          </div>
          <div>
            <div className="stat-value">{pendientes}</div>
            <div className="stat-label">Pendientes</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--danger-bg)' }}>
            <Timer size={20} style={{ color: 'var(--danger)' }} />
          </div>
          <div>
            <div className="stat-value">{formatTime(tiempoPendiente)}</div>
            <div className="stat-label">Tiempo requerido</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--success-bg)' }}>
            <CheckSquare size={20} style={{ color: 'var(--success)' }} />
          </div>
          <div>
            <div className="stat-value">{metricas?.completadas_hoy || 0}</div>
            <div className="stat-label">Completadas hoy</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--info-bg)' }}>
            <Clock size={20} style={{ color: 'var(--info)' }} />
          </div>
          <div>
            <div className="stat-value">{formatTime(tiempoDisp)}</div>
            <div className="stat-label">Tiempo disponible</div>
            <div className="occupancy-meter" style={{ marginTop: '0.3rem' }}>
              <div className="occupancy-bar">
                <div
                  className={`occupancy-fill ${porcentajeOcupado > 100 ? 'danger' : porcentajeOcupado > 80 ? 'warn' : 'safe'}`}
                  style={{ width: `${Math.min(100, porcentajeOcupado)}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-header-icon">
              <BarChart3 size={17} /> Matriz Eisenhower
            </div>
          </div>
          <EisenhowerMatrix data={eisenhower} />
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-header-icon">
              <Clock size={17} /> Proximas tareas del plan
            </div>
            {plan && plan.plan.length > 0 && (
              <Link to="/plan" className="btn btn-outline btn-sm">
                Ver plan completo <ArrowRight size={13} />
              </Link>
            )}
          </div>
          {plan && plan.plan.length > 0 ? (
            <div className="timeline" style={{ flexDirection: 'column', gap: '0', overflowX: 'visible' }}>
              {plan.plan.slice(0, 5).map((t, i) => (
                <div key={t.id} style={{
                  display: 'flex', gap: '0.75rem', padding: '0.6rem 0',
                  borderBottom: i < Math.min(plan.plan.length - 1, 4) ? '1px solid var(--border-light)' : 'none'
                }}>
                  <div className="plan-index" style={{ marginTop: '2px' }}>{i + 1}</div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 600, fontSize: '0.84rem' }}>{t.nombre}</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', display: 'flex', gap: '0.5rem' }}>
                      <span className={`badge badge-${t.categoria}`}>{t.categoria}</span>
                      <span>{formatTime(t.tiempo_estimado)}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-state" style={{ padding: '2rem' }}>
              <p>Agrega tareas para ver el plan del dia</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}
