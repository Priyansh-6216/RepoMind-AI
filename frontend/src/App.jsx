import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import RepoPage from './pages/RepoPage';
import ChatPage from './pages/ChatPage';

/**
 * RepoMind AI — Root Application Component
 */
export default function App() {
  const [theme, setTheme] = useState('dark');

  useEffect(() => {
    if (theme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar theme={theme} toggleTheme={toggleTheme} />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/repo/:id" element={<RepoPage />} />
            <Route path="/repo/:id/chat" element={<ChatPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
