import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Brain, Github } from 'lucide-react';

/**
 * Top navigation bar with brand and navigation links.
 */
export default function Navbar() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <div className="brand-icon">
            <Brain size={18} color="white" />
          </div>
          <span>Repo<span className="brand-ai">Mind</span></span>
        </Link>

        <div className="navbar-links">
          <Link to="/" className={isActive('/') ? 'active' : ''}>
            Home
          </Link>
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Github size={16} />
            GitHub
          </a>
        </div>
      </div>
    </nav>
  );
}
