import { useState, useEffect } from 'react';
import { CATEGORIAS } from '../utils/constants';
import { FileText, Clock, Star, AlertCircle, Link2, ListChecks, Repeat, Plus, X } from 'lucide-react';

const emptyForm = () => ({
  nombre: '',
  descripcion: '',
  categoria: 'personal',
  tiempo_estimado: 30,
  importancia: 3,
  urgencia: 3,
  fecha_limite: '',
  dependencias: '',
  subtareas: [],
  es_recurrente: false,
  frecuencia: 'ninguna',
});

export default function TaskForm({ initialData, onSubmit, buttonLabel = 'Guardar' }) {
  const [form, setForm] = useState(emptyForm());
  const [subtareaInput, setSubtareaInput] = useState('');

  useEffect(() => {
    if (initialData) {
      setForm({
        nombre: initialData.nombre || '',
        descripcion: initialData.descripcion || '',
        categoria: initialData.categoria || 'personal',
        tiempo_estimado: initialData.tiempo_estimado || 30,
        importancia: initialData.importancia || 3,
        urgencia: initialData.urgencia || 3,
        fecha_limite: initialData.fecha_limite || '',
        dependencias: (initialData.dependencias || []).join(', '),
        subtareas: initialData.subtareas || [],
        es_recurrente: initialData.es_recurrente || false,
        frecuencia: initialData.frecuencia || 'ninguna',
      });
    }
  }, [initialData]);

  const update = (field, value) => setForm(f => ({ ...f, [field]: value }));

  const addSubtarea = () => {
    if (!subtareaInput.trim()) return;
    update('subtareas', [...form.subtareas, { nombre: subtareaInput.trim(), completada: false }]);
    setSubtareaInput('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const payload = {
      ...form,
      dependencias: form.dependencias ? form.dependencias.split(',').map(s => s.trim()).filter(Boolean) : [],
      tiempo_estimado: parseInt(form.tiempo_estimado),
      importancia: parseInt(form.importancia),
      urgencia: parseInt(form.urgencia),
    };
    onSubmit(payload);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="form-section">
        <div className="form-section-title">Informacion Basica</div>
        <div className="grid-2">
          <div className="form-group">
            <label className="form-label"><FileText size={14} /> Nombre *</label>
            <input className="form-control" value={form.nombre}
              onChange={e => update('nombre', e.target.value)} required placeholder="Nombre de la tarea" />
          </div>
          <div className="form-group">
            <label className="form-label"><ListChecks size={14} /> Categoria</label>
            <select className="form-control" value={form.categoria}
              onChange={e => update('categoria', e.target.value)}>
              {CATEGORIAS.map(c => (
                <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>
        <div className="form-group">
          <label className="form-label"><FileText size={14} /> Descripcion</label>
          <textarea className="form-control" value={form.descripcion}
            onChange={e => update('descripcion', e.target.value)} placeholder="Detalles de la tarea..." />
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title">Planificacion</div>
        <div className="grid-2">
          <div className="form-group">
            <label className="form-label"><Clock size={14} /> Tiempo estimado (minutos)</label>
            <div className="range-group">
              <input type="range" min="5" max="480" step="5"
                value={form.tiempo_estimado} onChange={e => update('tiempo_estimado', e.target.value)} />
              <span className="range-value">{form.tiempo_estimado}m</span>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label"><AlertCircle size={14} /> Fecha limite</label>
            <input type="date" className="form-control" value={form.fecha_limite}
              onChange={e => update('fecha_limite', e.target.value)} />
          </div>
        </div>
        <div className="grid-2">
          <div className="form-group">
            <label className="form-label"><Star size={14} /> Importancia</label>
            <div className="range-group">
              <input type="range" min="1" max="5" value={form.importancia}
                onChange={e => update('importancia', e.target.value)} />
              <span className="range-value">{form.importancia}</span>
            </div>
          </div>
          <div className="form-group">
            <label className="form-label"><AlertCircle size={14} /> Urgencia</label>
            <div className="range-group">
              <input type="range" min="1" max="5" value={form.urgencia}
                onChange={e => update('urgencia', e.target.value)} />
              <span className="range-value">{form.urgencia}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title">Dependencias</div>
        <div className="form-group">
          <label className="form-label"><Link2 size={14} /> Dependencias (IDs separados por coma)</label>
          <input className="form-control" value={form.dependencias}
            onChange={e => update('dependencias', e.target.value)} placeholder="ID1, ID2, ..." />
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title">Subtareas</div>
        <div className="form-group">
          <div className="chip-group">
            {form.subtareas.map((st, i) => (
              <span key={i} className="chip" style={{ paddingRight: '0.25rem' }}>
                {st.nombre}
                <button type="button" className="btn-ghost btn-sm"
                  onClick={() => update('subtareas', form.subtareas.filter((_, j) => j !== i))}
                  style={{ padding: '0 0.15rem' }}><X size={12} /></button>
              </span>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.65rem' }}>
            <input className="form-control" value={subtareaInput}
              onChange={e => setSubtareaInput(e.target.value)}
              placeholder="Nueva subtarea"
              onKeyDown={e => e.key === 'Enter' && (e.preventDefault(), addSubtarea())} />
            <button type="button" className="btn btn-primary btn-sm" onClick={addSubtarea}>
              <Plus size={14} /> Agregar
            </button>
          </div>
        </div>
      </div>

      <div className="form-section">
        <div className="form-section-title">Recurrencia</div>
        <div className="form-group">
          <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer', fontWeight: 500, fontSize: '0.88rem' }}>
            <input type="checkbox" checked={form.es_recurrente}
              onChange={e => update('es_recurrente', e.target.checked)} />
            <Repeat size={14} /> Tarea recurrente
          </label>
          {form.es_recurrente && (
            <select className="form-control" value={form.frecuencia}
              onChange={e => update('frecuencia', e.target.value)} style={{ marginTop: '0.5rem' }}>
              <option value="ninguna">Sin recurrencia</option>
              <option value="diario">Diario</option>
              <option value="semanal">Semanal</option>
              <option value="mensual">Mensual</option>
            </select>
          )}
        </div>
      </div>

      <button type="submit" className="btn btn-primary">{buttonLabel}</button>
    </form>
  );
}
