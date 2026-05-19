import { useState, useEffect } from 'react';
import { api } from '../api/api';
import { formatTime } from '../utils/constants';
import Layout from '../components/Layout';
import { BarChart3, Clock, CheckSquare, Timer, User, Zap, AlertTriangle, TrendingUp } from 'lucide-react';

export default function SummaryPage() {
  const [metricas, setMetricas] = useState(null);
  const [usuario, setUsuario] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.metricas(), api.usuario.get()])
      .then(([m, u]) => { setMetricas(m); setUsuario(u); })
      .catch(err => console.error('Error cargando resumen:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Layout><div className="empty-state"><h3>Cargando resumen...</h3></div></Layout>;
  }

  const tareasHoy = metricas?.completadas_hoy || 0;
  const pendientes = metricas?.tareas_pendientes || 0;
  const tiempoPendiente = metricas?.tiempo_pendiente || 0;
  const tiempoDisp = metricas?.tiempo_disponible || 480;
  const racha = metricas?.racha || 0;
  const totalHistorial = metricas?.total_tareas_historial || 0;
  const tiempoPromedio = metricas?.tiempo_promedio_real || 0;
  const porcentajeOcupado = tiempoDisp > 0 ? Math.round((tiempoPendiente / tiempoDisp) * 100) : 0;

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Resumen Diario</h1>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Metricas de rendimiento y ocupacion
          </div>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--success-bg)' }}>
            <CheckSquare size={20} style={{ color: 'var(--success)' }} />
          </div>
          <div>
            <div className="stat-value">{tareasHoy}</div>
            <div className="stat-label">Completadas hoy</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--primary-bg)' }}>
            <Timer size={20} style={{ color: 'var(--primary)' }} />
          </div>
          <div>
            <div className="stat-value">{pendientes}</div>
            <div className="stat-label">Pendientes</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--warning-bg)' }}>
            <TrendingUp size={20} style={{ color: 'var(--warning)' }} />
          </div>
          <div>
            <div className="stat-value">{racha}</div>
            <div className="stat-label">Racha de dias</div>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'var(--info-bg)' }}>
            <BarChart3 size={20} style={{ color: 'var(--info)' }} />
          </div>
          <div>
            <div className="stat-value">{totalHistorial}</div>
            <div className="stat-label">Total historico</div>
          </div>
        </div>
      </div>

      <div className="grid-2">
        <div className="card">
          <div className="card-header">
            <div className="card-header-icon"><Clock size={17} /> Gestion del Tiempo</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.88rem' }}>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>DISPONIBLE</div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{formatTime(tiempoDisp)}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>REQUERIDO</div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem', color: porcentajeOcupado > 100 ? 'var(--danger)' : 'var(--text)' }}>
                {formatTime(tiempoPendiente)}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>RESTANTE</div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem', color: 'var(--success)' }}>
                {formatTime(Math.max(0, tiempoDisp - tiempoPendiente))}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>PROMEDIO/TAREA</div>
              <div style={{ fontWeight: 700, fontSize: '1.1rem' }}>{tiempoPromedio} min</div>
            </div>
          </div>
          <div className="occupancy-meter" style={{ marginTop: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem', fontSize: '0.72rem' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Ocupacion</span>
              <span style={{ fontWeight: 600, color: porcentajeOcupado > 100 ? 'var(--danger)' : 'var(--text)' }}>
                {porcentajeOcupado}%
              </span>
            </div>
            <div className="occupancy-bar">
              <div
                className={`occupancy-fill ${porcentajeOcupado > 100 ? 'danger' : porcentajeOcupado > 80 ? 'warn' : 'safe'}`}
                style={{ width: `${Math.min(100, porcentajeOcupado)}%` }}
              />
            </div>
            {porcentajeOcupado > 100 && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.4rem', fontSize: '0.78rem', color: 'var(--danger)' }}>
                <AlertTriangle size={14} /> Sobrecarga de trabajo
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-header-icon"><User size={17} /> Perfil</div>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.88rem' }}>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>NOMBRE</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>{usuario?.nombre || 'Usuario'}</div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>ENERGIA</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem', display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Zap size={14} style={{ color: 'var(--warning)' }} /> {usuario?.tipo_energia || 'neutro'}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>FACTOR</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>
                {usuario?.tipo_energia === 'manana' ? '1.15x' :
                 usuario?.tipo_energia === 'noche' ? '0.85x' : '1.0x'}
              </div>
            </div>
            <div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', fontWeight: 600, marginBottom: '0.2rem' }}>ALERTAS</div>
              <div style={{ fontWeight: 700, fontSize: '1.05rem' }}>
                {usuario?.notificaciones !== false ? (
                  <span style={{ color: 'var(--success)' }}>Activadas</span>
                ) : (
                  <span style={{ color: 'var(--text-muted)' }}>Desactivadas</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
}
