import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/api';
import { CATEGORIAS } from '../utils/constants';
import Layout from '../components/Layout';
import TaskCard from '../components/TaskCard';
import { Search, Filter, ArrowUpDown, Plus, RefreshCw, ChevronDown } from 'lucide-react';

export default function TaskList() {
  const [tareas, setTareas] = useState([]);
  const [completadas, setCompletadas] = useState([]);
  const [filtro, setFiltro] = useState('');
  const [categoria, setCategoria] = useState('todas');
  const [orden, setOrden] = useState('prioridad');
  const [loading, setLoading] = useState(true);
  const [showCompletadas, setShowCompletadas] = useState(false);

  const loadTareas = useCallback(async () => {
    try {
      const data = await api.tareas.list({ categoria, q: filtro, orden });
      setTareas(data.tareas || []);
      setCompletadas(data.completadas || []);
    } catch (err) {
      console.error('Error cargando tareas:', err);
    } finally {
      setLoading(false);
    }
  }, [categoria, filtro, orden]);

  useEffect(() => { loadTareas(); }, [loadTareas]);

  const handleComplete = async (id) => {
    try { await api.tareas.completar(id, {}); loadTareas(); }
    catch (err) { console.error(err); }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Eliminar esta tarea?')) return;
    try { await api.tareas.delete(id); loadTareas(); }
    catch (err) { console.error(err); }
  };

  const handleToggleSub = async (tid, sid) => {
    try { await api.tareas.toggleSub(tid, sid); loadTareas(); }
    catch (err) { console.error(err); }
  };

  return (
    <Layout>
      <div className="page-header">
        <div>
          <h1 className="page-title">Tareas</h1>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
            {tareas.length} pendientes &middot; {completadas.length} completadas
          </div>
        </div>
        <div className="btn-group">
          <button className="btn btn-ghost btn-sm" onClick={() => { setLoading(true); setTimeout(loadTareas, 100); }}>
            <RefreshCw size={14} />
          </button>
          <Link to="/tareas/agregar" className="btn btn-primary">
            <Plus size={16} /> Nueva Tarea
          </Link>
        </div>
      </div>

      <div className="filter-bar">
        <div style={{ position: 'relative', flex: 1, minWidth: 200 }}>
          <Search size={14} style={{ position: 'absolute', left: '0.65rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
          <input
            placeholder="Buscar tareas..."
            value={filtro}
            onChange={e => setFiltro(e.target.value)}
            style={{ paddingLeft: '2rem' }}
          />
        </div>
        <select value={categoria} onChange={e => setCategoria(e.target.value)}>
          <option value="todas">Todas las categorias</option>
          {CATEGORIAS.map(c => (
            <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
          ))}
        </select>
        <select value={orden} onChange={e => setOrden(e.target.value)}>
          <option value="prioridad">Por Prioridad</option>
          <option value="fecha">Por Fecha Limite</option>
          <option value="tiempo">Por Tiempo</option>
        </select>
      </div>

      {loading ? (
        <div className="empty-state"><SparklesLoader /></div>
      ) : tareas.length === 0 ? (
        <div className="empty-state">
          <ListEmpty />
          <h3>No hay tareas pendientes</h3>
          <p>Agrega una nueva tarea para empezar a planificar tu dia.</p>
          <Link to="/tareas/agregar" className="btn btn-primary" style={{ marginTop: '0.75rem' }}>
            <Plus size={15} /> Agregar Tarea
          </Link>
        </div>
      ) : (
        <>
          {tareas.map(t => (
            <TaskCard key={t.id} tarea={t}
              onComplete={handleComplete}
              onDelete={handleDelete}
              onToggleSub={handleToggleSub} />
          ))}
        </>
      )}

      <div style={{ marginTop: '1.25rem' }}>
        <button
          className="btn btn-outline btn-sm"
          onClick={() => setShowCompletadas(!showCompletadas)}
        >
          <ChevronDown size={14}
            style={{ transform: showCompletadas ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }} />
          {showCompletadas ? 'Ocultar' : 'Mostrar'} completadas ({completadas.length})
        </button>
      </div>

      {showCompletadas && completadas.length > 0 && (
        <div style={{ marginTop: '1rem' }}>
          <div className="card-header" style={{ paddingLeft: 0, marginBottom: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Completadas
            </span>
          </div>
          {completadas.map(t => (
            <TaskCard key={t.id} tarea={{ ...t, completada: true }}
              onComplete={() => {}} onDelete={handleDelete} onToggleSub={() => {}} />
          ))}
        </div>
      )}
    </Layout>
  );
}

function ListEmpty() {
  return (
    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
      <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2" />
      <rect x="9" y="3" width="6" height="4" rx="1" />
      <path d="M9 14l2 2 4-4" />
    </svg>
  );
}

function SparklesLoader() {
  return (
    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
      strokeLinecap="round" strokeLinejoin="round"
      style={{ animation: 'pulse 1.5s ease-in-out infinite', color: 'var(--primary)' }}>
      <path d="M12 3l1.5 5.5L19 10l-5.5 1.5L12 17l-1.5-5.5L5 10l5.5-1.5z" />
    </svg>
  );
}
