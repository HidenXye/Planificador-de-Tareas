import { Bar, Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale, LinearScale, BarElement, LineElement,
  PointElement, Title, Tooltip, Legend
);

export default function MetricChart({ metricas }) {
  if (!metricas || !metricas.dias_ultima_semana?.length) {
    return <div className="empty-state"><p>Carga datos para ver graficos</p></div>;
  }

  const dias = metricas.dias_ultima_semana;
  const labels = dias.map(d => d.fecha.slice(5));

  const barData = {
    labels,
    datasets: [
      {
        label: 'Tareas completadas',
        data: dias.map(d => d.tareas_completadas),
        backgroundColor: '#6c5ce7',
        borderRadius: 4,
      },
    ],
  };

  const lineData = {
    labels,
    datasets: [
      {
        label: 'Minutos trabajados',
        data: dias.map(d => d.tiempo_total),
        borderColor: '#00b894',
        backgroundColor: 'rgba(0,184,148,0.1)',
        fill: true,
        tension: 0.3,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
  };

  return (
    <div className="grid-2">
      <div className="card">
        <div className="card-header">Tareas Completadas (7 dias)</div>
        <div className="chart-container">
          <Bar data={barData} options={options} />
        </div>
      </div>
      <div className="card">
        <div className="card-header">Minutos Trabajados (7 dias)</div>
        <div className="chart-container">
          <Line data={lineData} options={{ ...options, scales: { y: { beginAtZero: true } } }} />
        </div>
      </div>
    </div>
  );
}
