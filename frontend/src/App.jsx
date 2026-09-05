import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  ClipboardList,
  FileSearch,
  LayoutDashboard,
  ShieldCheck,
  Users,
} from "lucide-react";

import Dashboard from "./pages/Dashboard";
import RecoveryFeed from "./pages/RecoveryFeed";
import CaseDetail from "./pages/CaseDetail";
import Analytics from "./pages/Analytics";
import AuditTrail from "./pages/AuditTrail";
import HumanReview from "./pages/HumanReview";

const navigation = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/recovery", label: "Recovery Feed", icon: Activity },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/audit", label: "Audit Trail", icon: ClipboardList },
  { to: "/review", label: "Human Review", icon: Users },
];

function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-mark">
              <ShieldCheck size={24} />
            </div>
            <div>
              <h1>REVIVE</h1>
              <span>Revenue Recovery AI</span>
            </div>
          </div>

          <nav className="sidebar-nav">
            {navigation.map(({ to, label, icon: Icon, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={19} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className="system-status">
              <span className="status-dot" />
              <span>System Operational</span>
            </div>
            <small>Autonomous recovery engine</small>
          </div>
        </aside>

        <main className="main-content">
          <header className="topbar">
            <div>
              <div className="breadcrumb">
                <FileSearch size={15} />
                <span>Revenue Intelligence</span>
              </div>
            </div>

            <div className="topbar-status">
              <AlertTriangle size={17} />
              <span>AI Guardrails Active</span>
            </div>
          </header>

          <div className="page-container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/recovery" element={<RecoveryFeed />} />
              <Route path="/cases/:caseId" element={<CaseDetail />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/audit" element={<AuditTrail />} />
              <Route path="/review" element={<HumanReview />} />
            </Routes>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;