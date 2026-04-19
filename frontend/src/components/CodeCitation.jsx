import React from 'react';
import { FileCode, Hash } from 'lucide-react';

/**
 * Code citation list — shows source file references that informed an AI answer.
 */
export default function CodeCitation({ citations }) {
  if (!citations || citations.length === 0) return null;

  return (
    <div className="citations">
      <div className="citations-title">📎 Source Citations</div>
      <div className="citation-list">
        {citations.map((citation, index) => (
          <div key={index} className="citation-item">
            <FileCode size={14} style={{ color: 'var(--accent-blue)', flexShrink: 0 }} />
            <span className="citation-file">
              {citation.filePath || citation.file_path}
            </span>
            <span className="citation-name">
              {citation.chunkName || citation.chunk_name || ''}
            </span>
            <span className="citation-lines">
              L{citation.startLine || citation.start_line}-{citation.endLine || citation.end_line}
            </span>
            {(citation.relevanceScore || citation.relevance_score) && (
              <span className="citation-score">
                {Math.round((citation.relevanceScore || citation.relevance_score) * 100)}%
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
