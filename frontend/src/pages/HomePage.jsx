import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Sparkles, Code2, MessageSquareText, FileSearch, Database, Cpu } from 'lucide-react';
import RepoImportForm from '../components/RepoImportForm';
import StatusBadge from '../components/StatusBadge';
import { importRepo, listRepos } from '../api/client';

/**
 * Home page — hero section, repo import form, and repository grid.
 */
export default function HomePage() {
  const [repos, setRepos] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRepos();
  }, []);

  const fetchRepos = async () => {
    try {
      const { data } = await listRepos();
      setRepos(data);
    } catch (err) {
      console.error('Failed to fetch repos:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (url) => {
    const { data } = await importRepo(url);
    navigate(`/repo/${data.id}`);
  };

  const features = [
    { icon: <Code2 size={20} />, title: 'AST Parsing', desc: 'Intelligent code chunking by function & class' },
    { icon: <Database size={20} />, title: 'Vector Search', desc: 'Semantic similarity with pgvector embeddings' },
    { icon: <MessageSquareText size={20} />, title: 'Grounded Q&A', desc: 'AI answers backed by source citations' },
    { icon: <FileSearch size={20} />, title: 'Flow Tracing', desc: 'Trace auth, payment & custom flows' },
    { icon: <Cpu size={20} />, title: 'Local LLM', desc: 'Powered by Ollama — free, private, fast' },
    { icon: <Sparkles size={20} />, title: 'Auto Insights', desc: 'Architecture overviews & onboarding guides' },
  ];

  return (
    <div>
      {/* Hero */}
      <motion.section
        className="hero"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div className="hero-badge">
          <Sparkles size={14} />
          AI-Powered Code Intelligence
        </div>

        <h1>
          Understand Any Repo<br />
          <span className="gradient-text">With AI</span>
        </h1>

        <p>
          Import a GitHub repository and ask questions about its architecture,
          functions, and flows. Powered by RAG with semantic code search.
        </p>

        <RepoImportForm onImport={handleImport} />
      </motion.section>

      {/* Features */}
      <motion.section
        style={{ marginTop: '4rem', marginBottom: '3rem' }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3, duration: 0.6 }}
      >
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
          gap: '1rem',
        }}>
          {features.map((feat, i) => (
            <motion.div
              key={i}
              className="glass-card"
              style={{ padding: '1.25rem', textAlign: 'center' }}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * i + 0.4, duration: 0.4 }}
              whileHover={{ scale: 1.02 }}
            >
              <div style={{
                width: 40, height: 40,
                borderRadius: 'var(--radius-md)',
                background: 'rgba(59, 130, 246, 0.1)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 0.75rem',
                color: 'var(--accent-blue)',
              }}>
                {feat.icon}
              </div>
              <h4 style={{ fontSize: '0.9rem', marginBottom: '0.3rem' }}>{feat.title}</h4>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{feat.desc}</p>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Repository List */}
      {repos.length > 0 && (
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
        >
          <div className="section-header">
            <div>
              <h2 className="section-title">Your Repositories</h2>
              <p className="section-subtitle">{repos.length} repositories analyzed</p>
            </div>
          </div>

          <div className="repo-grid">
            {repos.map((repo) => (
              <motion.div
                key={repo.id}
                className="glass-card repo-card"
                onClick={() => navigate(`/repo/${repo.id}`)}
                whileHover={{ scale: 1.01 }}
                transition={{ duration: 0.2 }}
              >
                <div className="repo-card-header">
                  <div>
                    <div className="repo-card-title">{repo.name}</div>
                    <div className="repo-card-owner">{repo.owner}</div>
                  </div>
                  <StatusBadge status={repo.status} />
                </div>

                {repo.description && (
                  <p style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-secondary)',
                    lineHeight: 1.5,
                  }}>
                    {repo.description}
                  </p>
                )}

                <div className="repo-card-stats">
                  <div className="repo-stat">
                    <Code2 size={14} />
                    <span className="repo-stat-value">{repo.fileCount || 0}</span> files
                  </div>
                  <div className="repo-stat">
                    <Database size={14} />
                    <span className="repo-stat-value">{repo.chunkCount || 0}</span> chunks
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>
      )}
    </div>
  );
}
