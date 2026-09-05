import { useEffect, useState } from "react";
import {
  BarChart3,
  TrendingUp,
  IndianRupee,
  Target,
  Activity,
} from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import { getAnalytics } from "../services/api";

function Analytics() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAnalytics = async () => {
      try {
        setLoading(true);
        const data = await getAnalytics();
        setAnalytics(data);
        setError("");
      } catch (err) {
        console.error("Analytics API error:", err);
        setError("Unable to load analytics from the backend.");
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Performance Intelligence</p>
            <h2>Analytics</h2>
            <p>Loading recovery analytics...</p>
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
            <p className="eyebrow">Performance Intelligence</p>
            <h2>Analytics</h2>
            <p className="error-message">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  const summary = analytics?.summary || {};

  const recoveryByScenario = analytics?.scenario_breakdown || [];

  const recoveryTrend = analytics?.trend || [];

  const totalCases = Number(summary.total_cases || 0);
  const recoveredCases = Number(summary.recovered_cases || 0);

  const totalRecovered = Number(summary.revenue_recovered || 0);

  const recoveryRate =
    totalCases > 0
      ? ((recoveredCases / totalCases) * 100).toFixed(2)
      : "0.00";

  const revenueAtRisk = Number(summary.revenue_at_risk || 0);

  const casesProcessed = totalCases;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Performance Intelligence</p>
          <h2>Analytics</h2>
          <p>
            Measure revenue recovery performance and identify where REVIVE
            creates the most impact.
          </p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <IndianRupee size={20} />
          </div>
          <div>
            <span className="stat-label">Revenue Recovered</span>
            <strong>?{totalRecovered.toLocaleString("en-IN")}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Target size={20} />
          </div>
          <div>
            <span className="stat-label">Recovery Rate</span>
            <strong>{recoveryRate}%</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <TrendingUp size={20} />
          </div>
          <div>
            <span className="stat-label">Revenue at Risk</span>
            <strong>
              ?{revenueAtRisk.toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Activity size={20} />
          </div>
          <div>
            <span className="stat-label">Cases Processed</span>
            <strong>{casesProcessed.toLocaleString("en-IN")}</strong>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>Recovery Trend</h3>
              <p>Revenue recovered over time</p>
            </div>
            <BarChart3 size={20} />
          </div>

          <div className="chart-container">
            {recoveryTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={recoveryTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip
                    formatter={(value) =>
                      `?${Number(value).toLocaleString("en-IN")}`
                    }
                  />
                  <Bar dataKey="recovered" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                No recovery trend data available yet.
              </div>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>Recovery by Scenario</h3>
              <p>Which revenue-loss scenarios are being recovered?</p>
            </div>
          </div>

          <div className="chart-container">
            {recoveryByScenario.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={recoveryByScenario}
                    dataKey="revenue_recovered"
                    nameKey="scenario"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {recoveryByScenario.map((entry, index) => (
                      <Cell key={`cell-${index}`} />
                    ))}
                  </Pie>

                  <Tooltip
                    formatter={(value) =>
                      `?${Number(value).toLocaleString("en-IN")}`
                    }
                  />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="empty-state">
                No scenario analytics available yet.
              </div>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Analytics;
