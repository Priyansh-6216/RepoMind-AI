import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  MessageSquare, Trash2, ExternalLink, RefreshCw,
  Code2, Database, Clock, ArrowLeft,
} from 'lucide-react';
import StatusBadge from '../components/StatusBadge';
import InsightCard from '../components/InsightCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ReactMarkdown from 'react-markdown';
import {
  getRepo, getRepoStatus, deleteRepo,
  getArchitectureInsight, getOnboardingInsight, traceFlow,
} from '../api/client';

/**
 * Repository detail page — status tracker, insights, navigation to chat.
 */
export default function RepoPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [repo, setRepo] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [insightLoading, setInsightLoading] = useState(null);
  const [insightModal, setInsightModal] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    fetchData();
  }, [id]);

  // Poll status while indexing
  useEffect(() => {
    if (!status || ['READY', 'FAILED', 'COMPLETED'].includes(status.repoStatus)) return;

    const interval = setInterval(() => {
      fetchStatus();
    }, 3000);

    return () => clearInterval(interval);
  }, [status]);

  const fetchData = async () => {
    try {
      const [repoRes, statusRes] = await Promise.all([
        getRepo(id),
        getRepoStatus(id),
      ]);
      setRepo(repoRes.data);
      setStatus(statusRes.data);
    } catch (err) {
      console.error('Failed to fetch repo:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchStatus = async () => {
    try {
      const { data } = await getRepoStatus(id);
      setStatus(data);
    } catch (err) {
      console.error('Status poll failed:', err);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Delete this repository and all its data?')) return;
    setDeleting(true);
    try {
      await deleteRepo(id);
      navigate('/');
    } catch (err) {
      console.error('Delete failed:', err);
      setDeleting(false);
    }
  };

  const handleGenerateInsight = async (type) => {
    setInsightLoading(type);
    try {
      let response;
      if (type === 'architecture') response = await getArchitectureInsight(id);
      else if (type === 'onboarding') response = await getOnboardingInsight(id);
      else if (type === 'flow') response = await traceFlow(id, 'main');

      setInsightModal(response.data);
    } catch (err) {
      console.error('Insight generation failed:', err);
    } finally {
      setInsightLoading(null);
    }
  };

  if (loading) return <LoadingSpinner size="lg" text="Loading repository..." />;
  if (!repo) return <div className="empty-state"><h3>Repository not found</h3></div>;

  const isReady = status?.repoStatus === 'READY';
  const isIndexing = ['PENDING', 'INDEXING', 'CLONING', 'PARSING', 'EMBEDDING', 'QUEUED'].includes(status?.repoStatus);

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="repo-header">
        <div className="repo-header-info">
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => navigate('/')}
            style={{ marginBottom: '0.75rem' }}
          >
            <ArrowLeft size={16} /> Back
          </button>
          <h1>{repo.name}</h1>
          <div className="repo-owner" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <span>{repo.owner}</span>
            <StatusBadge status={status?.repoStatus || repo.status} />
          </div>
        </div>

        <div className="repo-header-actions">
          {isReady && (
            <button
              className="btn btn-primary"
              onClick={() => navigate(`/repo/${id}/chat`)}
            >
              <MessageSquare size={18} />
              Chat with Code
            </button>
          )}
          <a
            href={repo.url}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-secondary"
          >
            <ExternalLink size={16} />
            GitHub
          </a>
          <button
            className="btn btn-danger"
            onClick={handleDelete}
            disabled={deleting}
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>

      {/* Status Card */}
      <div className="glass-card repo-status-card">
        <div className="repo-status-content">
          <div className="repo-status-info">
            <div className="repo-status-label">Indexing Status</div>
            <div className="repo-status-stage">
              {status?.jobStatus || status?.repoStatus || 'Unknown'}
            </div>
            {isIndexing && (
              <div className="progress-bar" style={{ maxWidth: '400px' }}>
                <div
                  className="progress-fill"
                  style={{ width: `${status?.progress || 0}%` }}
                />
              </div>
            )}
            {status?.errorMessage && (
              <p style={{
                color: 'var(--accent-red)',
                fontSize: '0.85rem',
                marginTop: '0.75rem',
              }}>
                {status.errorMessage}
              </p>
            )}
          </div>

          <div style={{ display: 'flex', gap: '2.5rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent-blue)' }}>
                {status?.fileCount || 0}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Files</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent-purple)' }}>
                {status?.chunkCount || 0}
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Chunks</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--accent-green)' }}>
                {status?.progress || 0}%
              </div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Progress</div>
            </div>
          </div>
        </div>
      </div>

      {/* Insights */}
      {isReady && (
        <>
          <div className="section-header" style={{ marginTop: '2rem' }}>
            <div>
              <h2 className="section-title">AI Insights</h2>
              <p className="section-subtitle">Generate intelligent analysis of the codebase</p>
            </div>
          </div>

          <div className="insights-grid">
            <InsightCard
              type="architecture"
              onGenerate={handleGenerateInsight}
              loading={insightLoading === 'architecture'}
            />
            <InsightCard
              type="onboarding"
              onGenerate={handleGenerateInsight}
              loading={insightLoading === 'onboarding'}
            />
            <InsightCard
              type="flow"
              onGenerate={handleGenerateInsight}
              loading={insightLoading === 'flow'}
            />
          </div>
        </>
      )}

      {/* Insight Modal */}
      {insightModal && (
        <div className="insight-modal-overlay" onClick={() => setInsightModal(null)}>
          <div className="insight-modal" onClick={(e) => e.stopPropagation()}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h2>{insightModal.title}</h2>
              <button
                className="btn btn-ghost btn-sm"
                onClick={() => setInsightModal(null)}
              >
                ✕
              </button>
            </div>
            <div className="insight-modal-content">
              <ReactMarkdown>{insightModal.content}</ReactMarkdown>
            </div>
          </div>
        </div>
      )}
    </motion.div>
  );
}
