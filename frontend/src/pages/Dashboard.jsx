import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  IndianRupee,
  TrendingUp,
  Zap,
} from "lucide-react";

import { getDashboard } from "../services/api";

function Dashboard() {
  const [dashboard, setDashboard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const data = await getDashboard();
        setDashboard(data);
        setError("");
      } catch (error) {
        console.error("Dashboard API error:", error);
        setError("Unable to load dashboard data from the backend.");
      } finally {
        setLoading(false);
      }
    };

    loadDashboard();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Revenue Intelligence</p>
            <h2>Dashboard</h2>
            <p>Loading REVIVE intelligence...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Revenue Intelligence</p>
            <h2>Dashboard</h2>
            <p className="error-message">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const stats = dashboard?.stats || dashboard || {};

  const recentCases =
    dashboard?.recent_cases ||
    dashboard?.cases ||
    dashboard?.items ||
    [];

  const revenueRecovered =
    stats.revenue_recovered ??
    dashboard?.revenue_recovered ??
    0;

  const recoveryRate =
    stats.recovery_rate ??
    dashboard?.recovery_rate ??
    0;

  const revenueAtRisk =
    stats.revenue_at_risk ??
    dashboard?.revenue_at_risk ??
    0;

  const casesProcessed =
    stats.cases_processed ??
    dashboard?.cases_processed ??
    0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Autonomous Revenue Recovery</p>
          <h2>Dashboard</h2>
          <p>
            Detect, diagnose and recover revenue automatically with bounded AI
            decisions.
          </p>
        </div>

        <div className="page-header-icon">
          <Activity size={22} />
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <IndianRupee size={20} />
          </div>

          <div>
            <span className="stat-label">Revenue Recovered</span>
            <strong>
              ₹{Number(revenueRecovered).toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TrendingUp size={20} />
          </div>

          <div>
            <span className="stat-label">Recovery Rate</span>
            <strong>{recoveryRate}%</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>

          <div>
            <span className="stat-label">Revenue at Risk</span>
            <strong>
              ₹{Number(revenueAtRisk).toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Zap size={20} />
          </div>

          <div>
            <span className="stat-label">Cases Processed</span>
            <strong>
              {Number(casesProcessed).toLocaleString("en-IN")}
            </strong>
          </div>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Recent Revenue Risk</h3>
            <p>
              Latest cases detected and processed by the REVIVE engine.
            </p>
          </div>

          <Activity size={20} />
        </div>

        {recentCases.length === 0 ? (
          <div className="empty-state">
            <CheckCircle2 size={30} />
            <h3>No recent cases</h3>
            <p>
              Revenue-risk events will appear here when the backend processes
              them.
            </p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Case</th>
                  <th>Scenario</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Risk</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {recentCases.map((item, index) => {
                  const id =
                    item.id ||
                    item.case_id ||
                    item.caseId ||
                    index + 1;

                  const scenario =
                    item.scenario ||
                    item.event_type ||
                    item.type ||
                    "Revenue risk";

                  const customer =
                    item.customer ||
                    item.customer_id ||
                    "Unknown";

                  const amount =
                    item.amount ||
                    item.revenue_at_risk ||
                    0;

                  const risk =
                    item.risk_score ??
                    item.risk ??
                    0;

                  const status =
                    item.status ||
                    item.action ||
                    item.decision ||
                    "Pending";

                  return (
                    <tr key={id}>
                      <td>#{id}</td>
                      <td>{scenario}</td>
                      <td>{customer}</td>
                      <td>
                        ₹{Number(amount).toLocaleString("en-IN")}
                      </td>
                      <td>{risk}</td>
                      <td>
                        <span className="status-badge">
                          {status}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

export default Dashboard;