import { Flame } from 'lucide-react';

export default function StreakBadge({ racha = 0 }) {
  return (
    <div className="streak-display">
      <div className="streak-flame">
        <Flame size={28} style={{ color: racha > 0 ? 'var(--warning)' : 'var(--text-muted)' }} />
      </div>
      <div className="streak-number">{racha}</div>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 500 }}>
        dias consecutivos
      </div>
    </div>
  );
}
