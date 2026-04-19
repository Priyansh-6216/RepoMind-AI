import React, { useState } from 'react';
import { GitBranch, ArrowRight, Loader } from 'lucide-react';

/**
 * Repository URL import form with validation and loading state.
 */
export default function RepoImportForm({ onImport }) {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Basic validation
    const githubRegex = /^https:\/\/github\.com\/[\w.-]+\/[\w.-]+\/?$/;
    if (!githubRegex.test(url)) {
      setError('Please enter a valid GitHub URL (e.g., https://github.com/owner/repo)');
      return;
    }

    setLoading(true);
    try {
      await onImport(url);
      setUrl('');
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to import repository');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="import-form" onSubmit={handleSubmit}>
      <div className="input-group">
        <div style={{ position: 'relative', flex: 1 }}>
          <GitBranch size={18} className="input-icon" />
          <input
            id="repo-url-input"
            type="text"
            className="input input-mono"
            placeholder="https://github.com/owner/repository"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
          />
        </div>
        <button
          id="import-repo-btn"
          type="submit"
          className="btn btn-primary btn-lg"
          disabled={loading || !url.trim()}
        >
          {loading ? (
            <>
              <Loader size={18} className="spinner" />
              Importing...
            </>
          ) : (
            <>
              Analyze
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </div>
      {error && (
        <p style={{ color: 'var(--accent-red)', fontSize: '0.82rem', marginTop: '0.75rem' }}>
          {error}
        </p>
      )}
    </form>
  );
}
