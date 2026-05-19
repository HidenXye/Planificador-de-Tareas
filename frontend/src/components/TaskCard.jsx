import { formatTime } from '../utils/constants';
import { CheckCircle, Edit2, Trash2, Briefcase, User, GraduationCap, Clock, AlertTriangle, ChevronDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

const catConfig = {
  trabajo: { icon: Briefcase, bg: 'var(--info-bg)', color: 'var(--info)' },
  personal: { icon: User, bg: 'var(--primary-bg)', color: 'var(--primary)' },
  estudio: { icon: GraduationCap, bg: 'var(--success-bg)', color: 'var(--success)' },
};

export default function TaskCard({ tarea, onComplete, onDelete, onToggleSub }) {
  const [expanded, setExpanded] = useState(false);
  const cfg = catConfig[tarea.categoria] || catConfig.personal;
  const CatIcon = cfg.icon;
  const hasSubtareas = tarea.subtareas?.length > 0;

  const isUrgent = tarea.fecha_limite && (() => {
    const diff = (new Date(tarea.fecha_limite) - new Date()) / (1000 * 60 * 60 * 24);
    return diff <= 1;
  })();

  return (
    <div className={`task-row ${tarea.completada ? 'completada' : ''}`}>
      <div className="task-left">
        <div className="task-category-icon" style={{ background: cfg.bg }}>
          <CatIcon size={16} style={{ color: cfg.color }} />
        </div>
        <div className="task-info">
          <div className="task-name">
            {tarea.nombre}
            {isUrgent && !tarea.completada && (
              <span className="badge badge-urgent" style={{ marginLeft: '0.5rem' }}>
                <AlertTriangle size={10} /> Urgente
              </span>
            )}
          </div>
          {tarea.descripcion && <div className="task-desc">{tarea.descripcion}</div>}
          <div className="task-meta">
            <span className={`badge badge-${tarea.categoria}`}>{tarea.categoria}</span>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
              <Clock size={12} />{formatTime(tarea.tiempo_estimado)}
            </span>
            <span>P: {tarea.prioridad}</span>
            {tarea.fecha_limite && <span style={{ display: 'flex', alignItems: 'center', gap: '0.2rem' }}>{tarea.fecha_limite}</span>}
            {tarea.tiempo_real && <span style={{ color: 'var(--success)' }}>Real: {formatTime(tarea.tiempo_real)}</span>}
          </div>
          <div className="priority-bar">
            <div className="priority-fill" style={{ width: `${tarea.prioridad}%` }} />
          </div>
          {hasSubtareas && (
            <div style={{ marginTop: '0.3rem' }}>
              <button
                className="btn-ghost btn-sm"
                onClick={() => setExpanded(!expanded)}
                style={{ fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.2rem' }}
              >
                {expanded ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                Subtareas ({tarea.subtareas.filter(s => s.completada).length}/{tarea.subtareas.length})
              </button>
              {expanded && (
                <div className="subtarea-tags">
                  {tarea.subtareas.map(st => (
                    <label key={st.id} className={`subtarea-tag ${st.completada ? 'done' : ''}`}
                      onClick={() => onToggleSub(tarea.id, st.id)}>
                      <input
                        type="checkbox"
                        checked={st.completada}
                        onChange={() => onToggleSub(tarea.id, st.id)}
                        style={{ width: '14px', height: '14px' }}
                      />
                      {st.nombre}
                    </label>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
      <div className="task-actions">
        {!tarea.completada && (
          <button className="btn btn-success btn-sm btn-icon" title="Completar"
            onClick={() => onComplete(tarea.id)}>
            <CheckCircle size={16} />
          </button>
        )}
        <a href={`/tareas/${tarea.id}/editar`} className="btn btn-outline btn-sm btn-icon" title="Editar">
          <Edit2 size={14} />
        </a>
        <button className="btn btn-danger btn-sm btn-icon" title="Eliminar"
          onClick={() => onDelete(tarea.id)}>
          <Trash2 size={14} />
        </button>
      </div>
    </div>
  );
}
