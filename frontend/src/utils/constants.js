export const CATEGORIAS = ['trabajo', 'personal', 'estudio'];

export const CATEGORIA_COLORS = {
  trabajo: '#74b9ff',
  personal: '#a29bfe',
  estudio: '#55efc4',
};

export function getPriorityColor(prioridad) {
  if (prioridad >= 70) return 'priority-high';
  if (prioridad >= 40) return 'priority-medium';
  return 'priority-low';
}

export function calculateUrgency(fechaLimite) {
  if (!fechaLimite) return 3;
  const hoy = new Date();
  const limite = new Date(fechaLimite);
  const dias = Math.max(0, (limite - hoy) / (1000 * 60 * 60 * 24));
  if (dias === 0) return 5;
  if (dias <= 1) return 5;
  if (dias <= 3) return 4;
  if (dias <= 7) return 3;
  return 2;
}

export function formatTime(min) {
  if (!min || min === 0) return '0 min';
  const h = Math.floor(min / 60);
  const m = min % 60;
  if (h === 0) return `${m} min`;
  if (m === 0) return `${h}h`;
  return `${h}h ${m}min`;
}

export function todayStr() {
  return new Date().toISOString().split('T')[0];
}
