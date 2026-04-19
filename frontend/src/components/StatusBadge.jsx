import React from 'react';

/**
 * Status badge showing repository/job state with color coding and pulse animation.
 */
export default function StatusBadge({ status }) {
  const statusMap = {
    PENDING: { label: 'Pending', className: 'badge-pending' },
    QUEUED: { label: 'Queued', className: 'badge-pending' },
    INDEXING: { label: 'Indexing', className: 'badge-indexing' },
    CLONING: { label: 'Cloning', className: 'badge-indexing' },
    PARSING: { label: 'Parsing', className: 'badge-indexing' },
    EMBEDDING: { label: 'Embedding', className: 'badge-indexing' },
    READY: { label: 'Ready', className: 'badge-ready' },
    COMPLETED: { label: 'Completed', className: 'badge-ready' },
    FAILED: { label: 'Failed', className: 'badge-failed' },
  };

  const config = statusMap[status] || { label: status, className: 'badge-pending' };

  return (
    <span className={`badge ${config.className}`}>
      <span className="badge-dot" />
      {config.label}
    </span>
  );
}
