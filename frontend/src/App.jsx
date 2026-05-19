import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TaskList from './pages/TaskList';
import AddTask from './pages/AddTask';
import PlanPage from './pages/PlanPage';
import HistoryPage from './pages/HistoryPage';
import SummaryPage from './pages/SummaryPage';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Dashboard />} />
      <Route path="/tareas" element={<TaskList />} />
      <Route path="/tareas/agregar" element={<AddTask />} />
      <Route path="/tareas/:id/editar" element={<AddTask />} />
      <Route path="/plan" element={<PlanPage />} />
      <Route path="/historial" element={<HistoryPage />} />
      <Route path="/resumen" element={<SummaryPage />} />
    </Routes>
  );
}
