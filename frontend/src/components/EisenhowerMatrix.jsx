import { AlertTriangle, Clock, ChevronRight, MinusCircle } from 'lucide-react';

export default function EisenhowerMatrix({ data = { q1: [], q2: [], q3: [], q4: [] } }) {
  const quadrants = {
    q1: { label: 'Hacer', sub: 'Urgente e Importante', icon: AlertTriangle },
    q2: { label: 'Planificar', sub: 'Importante, no urgente', icon: Clock },
    q3: { label: 'Delegar', sub: 'Urgente, no importante', icon: ChevronRight },
    q4: { label: 'Eliminar', sub: 'Ni urgente ni importante', icon: MinusCircle },
  };

  return (
    <div className="eisenhower-grid">
      {Object.entries(quadrants).map(([key, q]) => {
        const Icon = q.icon;
        return (
          <div key={key} className={`eisenhower-quadrant ${key}`}>
            <h4><Icon size={13} /> {q.label}</h4>
            <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginBottom: '0.5rem', marginTop: '-0.3rem' }}>
              {q.sub}
            </div>
            {!data[key] || data[key].length === 0 ? (
              <div className="empty-q">Vacio</div>
            ) : (
              data[key].map(t => (
                <div key={t.id} className="task-mini">
                  <span className={`badge badge-${t.categoria}`} style={{ fontSize: '0.6rem', padding: '0.1rem 0.35rem' }}>
                    {t.categoria}
                  </span>
                  {t.nombre}
                </div>
              ))
            )}
          </div>
        );
      })}
    </div>
  );
}
