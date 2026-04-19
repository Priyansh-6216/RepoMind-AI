import React from 'react';
import { Layers, BookOpen, GitPullRequest, Loader } from 'lucide-react';

/**
 * Insight generation cards — architecture, onboarding, flow tracing.
 */
export default function InsightCard({ type, onGenerate, loading }) {
  const configs = {
    architecture: {
      icon: <Layers size={22} />,
      iconClass: 'architecture',
      title: 'Architecture Overview',
      description: 'Analyze project structure, design patterns, and component relationships across the codebase.',
    },
    onboarding: {
      icon: <BookOpen size={22} />,
      iconClass: 'onboarding',
      title: 'Onboarding Guide',
      description: 'Generate a developer onboarding guide with key directories, setup steps, and important concepts.',
    },
    flow: {
      icon: <GitPullRequest size={22} />,
      iconClass: 'flow',
      title: 'Flow Tracing',
      description: 'Trace specific flows like authentication, payments, or data processing through the codebase.',
    },
  };

  const config = configs[type] || configs.architecture;

  return (
    <div
      className="glass-card insight-card"
      onClick={() => !loading && onGenerate(type)}
      style={{ cursor: loading ? 'wait' : 'pointer' }}
    >
      <div className={`insight-card-icon ${config.iconClass}`}>
        {loading ? <Loader size={22} className="spinner" /> : config.icon}
      </div>
      <h3>{config.title}</h3>
      <p>{config.description}</p>
    </div>
  );
}
