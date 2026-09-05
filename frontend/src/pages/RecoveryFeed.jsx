import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  IndianRupee,
} from "lucide-react";

import { getRecoveryCases } from "../services/api";

function RecoveryFeed() {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadCases = async () => {
      try {
        const data = await getRecoveryCases();

        const items = Array.isArray(data)
          ? data
          : data?.cases ||
            data?.items ||
            [];

        setCases(items);
        setError("");
      } catch (error) {
        console.error("Recovery feed API error:", error);
        setError("Unable to load recovery cases from the backend.");
      } finally {
        setLoading(false);
      }
    };

    loadCases();
  }, []);

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Autonomous Recovery</p>
            <h2>Recovery Feed</h2>
            <p>Loading revenue-risk cases...</p>
          </div>
        </div>
      </div>
    );
  }

  const activeCases = cases.filter((item) => {
    const status = String(item.status || "").toLowerCase();

    return (
      !status.includes("recovered") &&
      !status.includes("success") &&
      !status.includes("complete")
    );
  });

  const recoveredRevenue = cases
    .filter((item) => {
      const status = String(item.status || "").toLowerCase();

      return (
        status.includes("recovered") ||
        status.includes("success") ||
        status.includes("complete")
      );
    })
    .reduce(
      (total, item) =>
        total +
        Number(
          item.amount ||
            item.recovered_amount ||
            item.revenue_recovered ||
            0
        ),
      0
    );

  const riskRevenue = activeCases.reduce(
    (total, item) =>
      total +
      Number(
        item.amount ||
          item.revenue_at_risk ||
          0
      ),
    0
  );

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Autonomous Recovery</p>
          <h2>Recovery Feed</h2>
          <p>
            Live view of revenue-risk events moving through the REVIVE
            recovery pipeline.
          </p>
        </div>

        <div className="page-header-icon">
          <Activity size={22} />
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>

          <div>
            <span className="stat-label">Active Cases</span>
            <strong>{activeCases.length}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <IndianRupee size={20} />
          </div>

          <div>
            <span className="stat-label">Revenue at Risk</span>
            <strong>
              ₹{riskRevenue.toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <CheckCircle2 size={20} />
          </div>

          <div>
            <span className="stat-label">Revenue Recovered</span>
            <strong>
              ₹{recoveredRevenue.toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Clock3 size={20} />
          </div>

          <div>
            <span className="stat-label">Total Cases</span>
            <strong>{cases.length}</strong>
          </div>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Revenue Risk Cases</h3>
            <p>
              Failed payments, abandoned checkouts, subscription failures,
              overdue receivables and repeated failures.
            </p>
          </div>
        </div>

        {cases.length === 0 ? (
          <div className="empty-state">
            <Activity size={30} />
            <h3>No recovery cases</h3>
            <p>
              Cases will appear here when revenue-risk events are ingested.
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
                  <th>Risk Score</th>
                  <th>Action</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>
                {cases.map((item, index) => {
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

                  const action =
                    item.action ||
                    item.decision ||
                    "Pending";

                  const status =
                    item.status ||
                    "Pending";

                  return (
                    <tr key={id} onClick={() => navigate(`/cases/${id}`)} style={{ cursor: "pointer" }}>
                      <td>#{id}</td>

                      <td>{scenario}</td>

                      <td>{customer}</td>

                      <td>
                        ₹{Number(amount).toLocaleString("en-IN")}
                      </td>

                      <td>{risk}</td>

                      <td>{action}</td>

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

export default RecoveryFeed;

