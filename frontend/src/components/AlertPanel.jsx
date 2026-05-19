import { AlertTriangle, AlertCircle, Info } from 'lucide-react';

export default function AlertPanel({ alertas = [] }) {
  if (!alertas || alertas.length === 0) return null;

  const iconMap = { urgente: AlertTriangle, sobrecarga: AlertCircle, info: Info };

  return (
    <div style={{ marginBottom: '1.25rem' }}>
      {alertas.map((a, i) => {
        const Icon = iconMap[a.tipo] || Info;
        return (
          <div key={i} className={`alert-banner alert-${a.tipo === 'urgente' ? 'urgent' : 'warning'}`}>
            <Icon size={16} />
            <span><strong>{a.tipo === 'urgente' ? 'Urgente' : 'Aviso'}:</strong> {a.mensaje}</span>
          </div>
        );
      })}
    </div>
  );
}
