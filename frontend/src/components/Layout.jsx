import { NavLink } from 'react-router-dom';
import { useDarkMode } from '../hooks/useDarkMode';
import { LayoutDashboard, ListTodo, CalendarCheck, History, BarChart3, Moon, Sun, FileDown, ChevronRight } from 'lucide-react';

export default function Layout({ children }) {
  const [dark, toggleDark] = useDarkMode();

  const links = [
    { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/tareas', label: 'Tareas', icon: ListTodo },
    { to: '/plan', label: 'Plan Diario', icon: CalendarCheck },
    { to: '/historial', label: 'Historial', icon: History },
    { to: '/resumen', label: 'Resumen', icon: BarChart3 },
  ];

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-dot">
            <ChevronRight size={16} strokeWidth={2.5} />
          </div>
          Planificador
        </div>
        <ul className="sidebar-menu">
          {links.map(link => {
            const Icon = link.icon;
            return (
              <li key={link.to}>
                <NavLink to={link.to} end={link.to === '/'}
                  className={({ isActive }) => isActive ? 'active' : ''}>
                  <Icon size={18} strokeWidth={1.8} />
                  {link.label}
                </NavLink>
              </li>
            );
          })}
        </ul>
        <div className="sidebar-footer">
          <button className="theme-toggle" onClick={toggleDark}>
            {dark ? <Sun size={14} /> : <Moon size={14} />}
            {dark ? 'Modo Claro' : 'Modo Oscuro'}
          </button>
          <a href="/api/export/tareas" className="export-link">
            <FileDown size={13} />
            Exportar CSV
          </a>
        </div>
      </aside>
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}
