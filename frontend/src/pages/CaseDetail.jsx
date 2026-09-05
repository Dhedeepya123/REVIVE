import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CheckCircle2,
  Clock3,
  ShieldCheck,
  AlertTriangle,
  IndianRupee,
} from "lucide-react";

import { getCase, executeRecovery } from "../services/api";

function CaseDetail() {
  const { caseId } = useParams();

  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    const loadCase = async () => {
      try {
        const data = await getCase(caseId);

        setCaseData(data?.case || data);
        setError("");
      } catch (error) {
        console.error("Case API error:", error);
        setError("Unable to load this case from the backend.");
      } finally {
        setLoading(false);
      }
    };

    loadCase();
  }, [caseId]);

  const handleRecovery = async () => {
    try {
      setProcessing(true);

      const result = await executeRecovery(
        caseId,
        caseData?.action || caseData?.decision || "retry"
      );

      setCaseData((previous) => ({
        ...previous,
        ...(result?.case || result || {}),
      }));

      setError("");
    } catch (error) {
      console.error("Recovery execution error:", error);
      setError("Unable to execute the recovery action.");
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Case Intelligence</p>
            <h2>Case Detail</h2>
            <p>Loading case information...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error && !caseData) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Case Intelligence</p>
            <h2>Case Detail</h2>
            <p className="error-message">{error}</p>
          </div>
        </div>

        <Link to="/recovery" className="button">
          <ArrowLeft size={17} />
          Back to Recovery Feed
        </Link>
      </div>
    );
  }

  const amount =
    caseData?.amount ||
    caseData?.revenue_at_risk ||
    0;

  const riskScore =
    caseData?.risk_score ??
    caseData?.risk ??
    0;

  const scenario =
    caseData?.scenario ||
    caseData?.event_type ||
    "Revenue risk";

  const customer =
    caseData?.customer ||
    caseData?.customer_id ||
    "Unknown customer";

  const status =
    caseData?.status ||
    "Pending";

  const diagnosis =
    caseData?.diagnosis ||
    caseData?.ai_diagnosis ||
    caseData?.reason ||
    "Diagnosis not available.";

  const decision =
    caseData?.decision ||
    caseData?.action ||
    "No action selected.";

  const policyResult = caseData?.policy_result || caseData?.policy || null;  const policy = typeof policyResult === "object" && policyResult !== null    ? policyResult.decision || policyResult.action || "Policy evaluation available"    : policyResult || "Policy evaluation not available.";  const policyReason = typeof policyResult === "object" && policyResult !== null    ? policyResult.reason || ""    : "";

  const paymentStatus =
    caseData?.payment_status ||
    caseData?.paymentStatus ||
    "Unknown";

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/recovery" className="back-link">
            <ArrowLeft size={16} />
            Back to Recovery Feed
          </Link>

          <p className="eyebrow">Case Intelligence</p>

          <h2>
            Case #{caseId}
          </h2>

          <p>
            Detailed diagnosis, decision, policy and recovery information.
          </p>
        </div>

        <div className="page-header-icon">
          <ShieldCheck size={22} />
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
            <IndianRupee size={20} />
          </div>

          <div>
            <span className="stat-label">Revenue at Risk</span>
            <strong>
              ₹{Number(amount).toLocaleString("en-IN")}
            </strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <AlertTriangle size={20} />
          </div>

          <div>
            <span className="stat-label">Risk Score</span>
            <strong>{riskScore}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <CheckCircle2 size={20} />
          </div>

          <div>
            <span className="stat-label">Status</span>
            <strong>{status}</strong>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">
            <Clock3 size={20} />
          </div>

          <div>
            <span className="stat-label">Payment Status</span>
            <strong>{paymentStatus}</strong>
          </div>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>Case Information</h3>
              <p>Revenue event and customer information.</p>
            </div>
          </div>

          <div className="detail-grid">
            <div className="detail-item">
              <span>Scenario</span>
              <strong>{scenario}</strong>
            </div>

            <div className="detail-item">
              <span>Customer</span>
              <strong>{customer}</strong>
            </div>

            <div className="detail-item">
              <span>Amount</span>
              <strong>
                ₹{Number(amount).toLocaleString("en-IN")}
              </strong>
            </div>

            <div className="detail-item">
              <span>Status</span>
              <strong>{status}</strong>
            </div>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>AI Diagnosis</h3>
              <p>Why REVIVE believes revenue is at risk.</p>
            </div>
          </div>

          <div className="detail-text">
            {diagnosis}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>AI Decision</h3>
              <p>Recommended bounded intervention.</p>
            </div>
          </div>

          <div className="detail-highlight">
            {decision}
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h3>Policy Engine</h3>
              <p>Safety and authorization result.</p>
            </div>
          </div>

          <div className="detail-text">{policy}{policyReason && <div style={{marginTop:"8px"}}>{policyReason}</div>}</div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>Recovery Action</h3>
            <p>
              Execute the bounded intervention selected by REVIVE.
            </p>
          </div>
        </div>

        <button
          className="button button-success"
          disabled={processing}
          onClick={handleRecovery}
        >
          <CheckCircle2 size={17} />

          {processing
            ? "Executing..."
            : "Execute Recovery"}
        </button>
      </section>
    </div>
  );
}

export default CaseDetail;





