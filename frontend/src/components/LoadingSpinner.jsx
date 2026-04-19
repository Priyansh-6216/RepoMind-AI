import React from 'react';

/**
 * Loading spinner component with configurable size.
 */
export default function LoadingSpinner({ size = 'default', text = '' }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '1rem',
      padding: '2rem',
    }}>
      <div className={`spinner ${size === 'lg' ? 'spinner-lg' : ''}`} />
      {text && (
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
          {text}
        </p>
      )}
    </div>
  );
}
