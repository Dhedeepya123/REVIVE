import { useEffect, useState } from "react";
import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  UserRound,
  ShieldCheck,
  Clock3,
} from "lucide-react";

import { getAuditTrail } from "../services/api";

function AuditTrail() {
  const [auditEntries, setAuditEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadAuditTrail = async () => {
      try {
        setLoading(true);

        const data = await getAuditTrail();

        const entries = Array.isArray(data)
          ? data
          : data?.events || data?.audit ||
            data?.entries ||
            data?.items ||
            [];

        setAuditEntries(entries);
        setError("");
      } catch (err) {
        console.error("Audit trail API error:", err);
        setError("Unable to load audit trail from the backend.");
      } finally {
        setLoading(false);
      }
    };

    loadAuditTrail();
  }, []);

  const getStatusIcon = (status) => {
    const value = String(status || "").toLowerCase();

    if (
      value.includes("success") ||
      value.includes("approved") ||
      value.includes("recovered") ||
      value.includes("complete")
    ) {
      return <CheckCircle2 size={17} />;
    }

    if (
      value.includes("failed") ||
      value.includes("rejected") ||
      value.includes("blocked")
    ) {
      return <XCircle size={17} />;
    }

    if (value.includes("human")) {
      return <UserRound size={17} />;
    }

    return <Clock3 size={17} />;
  };

  if (loading) {
    return (
      <div className="page">
        <div className="page-header">
          <div>
            <p className="eyebrow">Governance & Compliance</p>
            <h2>Audit Trail</h2>
            <p>Loading audit events...</p>
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
            <p className="eyebrow">Governance & Compliance</p>
            <h2>Audit Trail</h2>
            <p className="error-message">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">Governance & Compliance</p>
          <h2>Audit Trail</h2>
          <p>
            Complete record of AI decisions, policy checks, recovery actions,
            and verification events.
          </p>
        </div>

        <div className="page-header-icon">
          <ClipboardList size={22} />
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <div>
            <h3>System Activity</h3>
            <p>
              Every important REVIVE action is recorded for traceability.
            </p>
          </div>

          <div className="audit-security">
            <ShieldCheck size={17} />
            <span>Audit logging active</span>
          </div>
        </div>

        {auditEntries.length === 0 ? (
          <div className="empty-state">
            <ClipboardList size={28} />
            <h3>No audit events yet</h3>
            <p>
              Audit events will appear here as REVIVE processes revenue-risk
              cases.
            </p>
          </div>
        ) : (
          <div className="audit-list">
            {auditEntries.map((entry, index) => {
              const id =
                entry.id ||
                entry.audit_id ||
                entry.event_id ||
                index;

              const status =
                entry.status ||
                entry.result ||
                entry.outcome ||
                "Recorded";

              const action =
                entry.action ||
                entry.event_type ||
                entry.event ||
                "System event";

              const description =
                entry.description ||
                entry.message ||
                entry.details ||
                "";

              const caseId =
                entry.case_id ||
                entry.caseId ||
                entry.reference ||
                "";

              const timestamp =
                entry.timestamp ||
                entry.created_at ||
                entry.time ||
                "";

              const actor =
                entry.actor ||
                entry.agent ||
                entry.source ||
                "REVIVE";

              return (
                <div className="audit-item" key={id}>
                  <div className="audit-icon">
                    {getStatusIcon(status)}
                  </div>

                  <div className="audit-content">
                    <div className="audit-title-row">
                      <strong>{action}</strong>

                      <span className="audit-status">
                        {status}
                      </span>
                    </div>

                    {description && (
                      <p>{description}</p>
                    )}

                    <div className="audit-meta">
                      <span>
                        <UserRound size={14} />
                        {actor}
                      </span>

                      {caseId && (
                        <span>
                          Case: {caseId}
                        </span>
                      )}

                      {timestamp && (
                        <span>
                          <Clock3 size={14} />
                          {timestamp}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}

export default AuditTrail;
