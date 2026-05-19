import { useState, useEffect } from 'react';
import { api } from '../api/api';
import Layout from '../components/Layout';
import MetricChart from '../components/MetricChart';
import { History, Download, Calendar } from 'lucide-react';

export default function HistoryPage() {
  const [historial, setHistorial] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.historial()
      .then(data => setHistorial(data))
      .catch(err => console.error('Error cargando historial:', err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <Layout><div className="empty-state"><h3>Cargando historial...</h3></div></Layout>;
  }

  const dias = historial?.historial_diario || {};
  const diasOrdenados = Object.entries(dias)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .slice(0, 30);

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Historial</h1>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            Registro de los ultimos 30 dias
          </div>
        </div>
        <a href={api.export.historial()} className="btn btn-outline btn-sm" target="_blank" rel="noreferrer">
          <Download size={14} /> Exportar CSV
        </a>
      </div>

      <MetricChart metricas={historial?.metricas || null} />

      <div className="card" style={{ marginTop: '1.25rem' }}>
        <div className="card-header">
          <div className="card-header-icon">
            <Calendar size={17} /> Registro diario
          </div>
        </div>
        {diasOrdenados.length === 0 ? (
          <div className="empty-state">
            <History size={36} />
            <h3>Sin historial</h3>
            <p>Completa tareas para empezar a registrar tu progreso.</p>
          </div>
        ) : (
          <div style={{ overflowX: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Tareas</th>
                  <th>Tiempo total</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>
                {diasOrdenados.map(([fecha, tareas]) => {
                  const tiempoTotal = tareas.reduce(
                    (s, t) => s + (t.tiempo_real || t.tiempo_estimado || 0), 0
                  );
                  return (
                    <tr key={fecha}>
                      <td style={{ fontWeight: 600 }}>{fecha}</td>
                      <td><span className="badge badge-ok">{tareas.length}</span></td>
                      <td>{tiempoTotal} min</td>
                      <td style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {tareas.map(t => t.nombre).join(', ')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </Layout>
  );
}
