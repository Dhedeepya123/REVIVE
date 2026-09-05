import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8010",
  headers: {
    "Content-Type": "application/json",
  },
});

export const getDashboard = async () => {
  const response = await api.get("/api/dashboard");
  return response.data;
};

export const getRecoveryCases = async () => {
  const response = await api.get("/api/cases");
  return response.data;
};

export const getCase = async (caseId) => {
  const response = await api.get(`/api/cases/${caseId}`);
  return response.data;
};

export const getAnalytics = async () => {
  const response = await api.get("/api/dashboard/analytics");
  return response.data;
};

export const getAuditTrail = async () => {
  const response = await api.get("/api/audit");
  return response.data;
};

export const getHumanReviewCases = async () => {
  const response = await api.get("/api/review");
  return response.data;
};

export const executeRecovery = async (caseId, action) => {
  const response = await api.post(`/api/recovery/${caseId}`, {
    action,
  });
  return response.data;
};

export const approveReview = async (caseId) => {
  const response = await api.post(`/api/review/${caseId}/approve`);
  return response.data;
};

export const rejectReview = async (caseId, reason) => {
  const response = await api.post(`/api/review/${caseId}/reject`, {
    reason,
  });
  return response.data;
};

export const healthCheck = async () => {
  const response = await api.get("/health");
  return response.data;
};

export default api;