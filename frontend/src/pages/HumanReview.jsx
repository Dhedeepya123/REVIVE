import { useEffect, useState } from "react";
import {
  Users,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  IndianRupee,
} from "lucide-react";

import {
  getHumanReviewCases,
  approveReview,
  rejectReview,
} from "../services/api";

function HumanReview() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [processingId, setProcessingId] = useState(null);

  useEffect(() => {
    let active = true;

    const loadInitialCases = async () => {
      try {
        const data = await getHumanReviewCases();

        if (!active) {
          return;
        }

        const items = Array.isArray(data)
          ? data
          : data?.cases ||
            data?.items ||
            data?.reviews ||
            [];

        setCases(items);
        setError("");
      } catch (error) {
        if (!active) {
          return;
        }

        console.error("Human review API error:", error);
        setError(
          "Unable to load human review cases from the backend."
        );
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    };

    loadInitialCases();

    return () => {
      active = false;
    };
  }, []);

  const reloadCases = async () => {
    try {
      const data = await getHumanReviewCases();

      const items = Array.isArray(data)
        ? data
        : data?.cases ||
          data?.items ||
          data?.reviews ||
          [];

      setCases(items);
      setError("");
    } catch (error) {
      console.error("Human review API error:", error);
      setError(
        "Unable to refresh human review cases."
      );
    }
  };

  const handleApprove = async (caseId) => {
    try {
      setProcessingId(caseId);
      setError("");

      await approveReview(caseId);
      await reloadCases();
    } catch (error) {
      console.error("Approve review error:", error);
      setError("Unable to approve this case.");
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (caseId) => {
    const reason = window.prompt(
      "Enter the reason for rejecting this recovery:"
    );

    if (reason === null) {
      return;
    }

    try {
      setProcessingId(caseId);
      setError("");

      await rejectReview(
        caseId,
        reason || "Rejected by reviewer"
      );

      await reloadCases();
    } catch (error) {
      console.error("Reject review error:", error);
      setError("Unable to reject this case.");
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Human-in-the-Loop</p>
            <h2>Human Review</h2>
            <p>
              Loading cases that require human attention...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Human-in-the-Loop</p>
          <h2>Human Review</h2>
          <p>
            Review cases that cannot be safely handled autonomously by
            REVIVE.
          </p>
        </div>

        <div className="page-header-icon">
          <Users size={22} />
        </div>
      </div>

      {error && (
        <div className="error-banner">
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}

      {cases.length === 0 ? (
        <section className="panel">
          <div className="empty-state">
            <CheckCircle2 size={32} />

            <h3>No cases require review</h3>

            <p>
              REVIVE has no pending human-review decisions at the moment.
            </p>
          </div>
        </section>
      ) : (
        <div className="review-list">
          {cases.map((item, index) => {
            const caseId =
              item.case_id ||
              item.caseId ||
              item.id ||
              index;

            const customer =
              item.customer ||
              item.customer_id ||
              "Unknown customer";

            const amount =
              item.amount ||
              item.revenue_at_risk ||
              item.value ||
              0;

            const scenario =
              item.scenario ||
              item.event_type ||
              item.type ||
              "Revenue risk";

            const riskScore =
              item.risk_score ??
              item.risk ??
              0;

            const reason =
              item.reason ||
              item.failure_reason ||
              item.explanation ||
              item.description ||
              "This case requires human review.";

            const recommendation =
              item.recommendation ||
              item.action ||
              item.decision ||
              "Review required";

            const status =
              item.status ||
              "Pending";

            return (
              <section
                className="panel review-card"
                key={caseId}
              >
                <div className="review-card-header">
                  <div>
                    <span className="case-id">
                      Case #{caseId}
                    </span>

                    <h3>{scenario}</h3>
                  </div>

                  <span className="review-status">
                    {status}
                  </span>
                </div>

                <div className="review-details">
                  <div className="review-detail">
                    <span>Customer</span>
                    <strong>{customer}</strong>
                  </div>

                  <div className="review-detail">
                    <span>Revenue at Risk</span>

                    <strong>
                      <IndianRupee size={15} />
                      {Number(amount).toLocaleString("en-IN")}
                    </strong>
                  </div>

                  <div className="review-detail">
                    <span>Risk Score</span>
                    <strong>{riskScore}</strong>
                  </div>
                </div>

                <div className="review-reason">
                  <span>
                    Why REVIVE escalated this case
                  </span>

                  <p>{reason}</p>
                </div>

                <div className="review-recommendation">
                  <span>AI Recommendation</span>
                  <strong>{recommendation}</strong>
                </div>

                <div className="review-actions">
                  <button
                    className="button button-success"
                    disabled={processingId === caseId}
                    onClick={() =>
                      handleApprove(caseId)
                    }
                  >
                    <CheckCircle2 size={17} />

                    {processingId === caseId
                      ? "Processing..."
                      : "Approve"}
                  </button>

                  <button
                    className="button button-danger"
                    disabled={processingId === caseId}
                    onClick={() =>
                      handleReject(caseId)
                    }
                  >
                    <XCircle size={17} />
                    Reject
                  </button>
                </div>
              </section>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default HumanReview;