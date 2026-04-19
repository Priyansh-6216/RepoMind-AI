/**
 * RepoMind AI — API Client
 * Axios wrapper for backend communication.
 */

import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 120000, // 2 min timeout for LLM calls
});

// ── Repository APIs ──────────────────────────────────────────

export const importRepo = (url) =>
  api.post('/repos/import', { url });

export const listRepos = () =>
  api.get('/repos');

export const getRepo = (id) =>
  api.get(`/repos/${id}`);

export const getRepoStatus = (id) =>
  api.get(`/repos/${id}/status`);

export const deleteRepo = (id) =>
  api.delete(`/repos/${id}`);

// ── Chat APIs ────────────────────────────────────────────────

export const sendChatMessage = (repoId, question, sessionId = null) =>
  api.post(`/repos/${repoId}/chat`, { question, sessionId });

export const getChatSessions = (repoId) =>
  api.get(`/repos/${repoId}/chat/sessions`);

export const getSessionMessages = (repoId, sessionId) =>
  api.get(`/repos/${repoId}/chat/sessions/${sessionId}`);

// ── Insight APIs ─────────────────────────────────────────────

export const getArchitectureInsight = (repoId) =>
  api.post(`/repos/${repoId}/insights/architecture`);

export const getOnboardingInsight = (repoId) =>
  api.post(`/repos/${repoId}/insights/onboarding`);

export const traceFlow = (repoId, flowName) =>
  api.post(`/repos/${repoId}/insights/flow`, { flowName });

export default api;
