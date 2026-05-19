import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { api } from '../api/api';
import Layout from '../components/Layout';
import TaskForm from '../components/TaskForm';

export default function AddTask() {
  const navigate = useNavigate();
  const { id } = useParams();
  const [existingTask, setExistingTask] = useState(null);
  const [existingTasks, setExistingTasks] = useState([]);
  const [loading, setLoading] = useState(!!id);

  useEffect(() => {
    api.tareas.list().then(d => setExistingTasks(d.tareas || [])).catch(() => {});
  }, []);

  useEffect(() => {
    if (id) {
      const all = [...existingTasks];
      const t = all.find(t => t.id === id);
      if (t) setExistingTask(t);
      setLoading(false);
    }
  }, [id, existingTasks]);

  const handleSubmit = async (formData) => {
    try {
      if (id) {
        await api.tareas.update(id, { ...formData, completada: existingTask?.completada || false });
      } else {
        await api.tareas.create(formData);
      }
      navigate('/tareas');
    } catch (err) {
      console.error('Error guardando tarea:', err);
      alert('Error al guardar la tarea: ' + err.message);
    }
  };

  if (loading) {
    return <Layout><div className="empty-state"><p>Cargando...</p></div></Layout>;
  }

  return (
    <Layout>
      <div className="page-header">
        <h1 className="page-title">{id ? 'Editar Tarea' : 'Nueva Tarea'}</h1>
      </div>
      <div className="card">
        {existingTasks.length > 0 && !id && (
          <div style={{ marginBottom: '1rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Tareas existentes para dependencias:{' '}
            {existingTasks.map(t => (
              <span key={t.id} className="badge badge-personal" style={{ margin: '0 2px' }}>
                {t.nombre} ({t.id.slice(0, 6)})
              </span>
            ))}
          </div>
        )}
        <TaskForm
          initialData={existingTask}
          onSubmit={handleSubmit}
          buttonLabel={id ? 'Actualizar Tarea' : 'Crear Tarea'}
        />
      </div>
    </Layout>
  );
}
