import { NavLink, useNavigate } from "react-router-dom";
import { LayoutDashboard, Briefcase, LogOut, ScanSearch } from "lucide-react";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/jobs", label: "Jobs", icon: Briefcase },
];

export default function Layout({ title, actions, children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="flex min-h-screen bg-surface">
      <aside className="hidden w-64 shrink-0 flex-col bg-navy text-white md:flex">
        <div className="flex items-center gap-2.5 px-6 py-6">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-mint/20 text-mint">
            <ScanSearch size={20} />
          </span>
          <div className="leading-tight">
            <p className="font-display text-base font-semibold">IRSCS</p>
            <p className="text-[11px] text-white/60">Resume Screening</p>
          </div>
        </div>

        <nav className="mt-2 flex-1 space-y-1 px-3">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive ? "bg-white/10 text-white" : "text-white/70 hover:bg-white/5 hover:text-white"
                }`
              }
            >
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-white/10 px-4 py-4">
          <p className="truncate text-xs text-white/50">Signed in as</p>
          <p className="truncate text-sm font-medium text-white">{user}</p>
          <button
            onClick={handleLogout}
            className="mt-3 flex w-full items-center gap-2 rounded-lg px-2 py-2 text-sm text-white/70 hover:bg-white/5 hover:text-white"
          >
            <LogOut size={16} />
            Log out
          </button>
        </div>
      </aside>

      <div className="flex min-h-screen flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-border bg-white px-5 py-4 md:px-8">
          <h1 className="font-display text-xl font-semibold text-ink md:text-2xl">{title}</h1>
          <div className="flex items-center gap-2">{actions}</div>
        </header>
        <main className="flex-1 px-5 py-6 md:px-8 md:py-8">{children}</main>
      </div>
    </div>
  );
}
