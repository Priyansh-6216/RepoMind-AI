import React from 'react';
import { motion } from 'framer-motion';

export default function SkeletonLoader({ count = 3 }) {
  return (
    <div className="repo-grid">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          className="glass-card"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3 }}
          style={{ minHeight: '180px', display: 'flex', flexDirection: 'column' }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <div style={{ width: '60%', height: '24px', background: 'var(--bg-tertiary)', borderRadius: '4px', animation: 'pulse 1.5s infinite ease-in-out' }} />
            <div style={{ width: '25%', height: '24px', background: 'var(--bg-tertiary)', borderRadius: '12px', animation: 'pulse 1.5s infinite ease-in-out' }} />
          </div>
          <div style={{ width: '80%', height: '14px', background: 'var(--bg-tertiary)', borderRadius: '4px', marginBottom: '0.5rem', animation: 'pulse 1.5s infinite ease-in-out', animationDelay: '0.2s' }} />
          <div style={{ width: '40%', height: '14px', background: 'var(--bg-tertiary)', borderRadius: '4px', animation: 'pulse 1.5s infinite ease-in-out', animationDelay: '0.4s' }} />
          <div style={{ marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border-default)', display: 'flex', gap: '1rem' }}>
            <div style={{ width: '60px', height: '16px', background: 'var(--bg-tertiary)', borderRadius: '4px', animation: 'pulse 1.5s infinite ease-in-out' }} />
            <div style={{ width: '60px', height: '16px', background: 'var(--bg-tertiary)', borderRadius: '4px', animation: 'pulse 1.5s infinite ease-in-out' }} />
          </div>
        </motion.div>
      ))}
      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes pulse {
          0% { opacity: 0.5; }
          50% { opacity: 1; }
          100% { opacity: 0.5; }
        }
      `}} />
    </div>
  );
}
