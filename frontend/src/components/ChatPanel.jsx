import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Plus, Brain } from 'lucide-react';
import ChatMessage from './ChatMessage';

/**
 * Full chat panel — message list, input, session sidebar.
 * Handles sending messages, displaying typing indicators, and suggestions.
 */
export default function ChatPanel({
  messages,
  sessions,
  activeSessionId,
  onSendMessage,
  onSelectSession,
  onNewSession,
  loading,
  repoName,
}) {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleSuggestionClick = (question) => {
    onSendMessage(question);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const suggestions = [
    'How is this project structured?',
    'What design patterns are used?',
    'How does authentication work?',
    'Explain the main entry point',
    'What are the key dependencies?',
  ];

  return (
    <div className="chat-layout">
      {/* Sidebar */}
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <span className="chat-sidebar-title">Chat History</span>
          <button
            className="btn btn-ghost btn-sm"
            onClick={onNewSession}
            title="New conversation"
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="session-list">
          {sessions.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.82rem', padding: '0.5rem' }}>
              No conversations yet
            </p>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
                onClick={() => onSelectSession(session.id)}
              >
                <MessageSquare size={14} style={{ marginRight: '8px', flexShrink: 0 }} />
                {session.title || 'Untitled'}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="chat-main">
        {messages.length === 0 && !loading ? (
          <div className="chat-empty">
            <div className="chat-empty-icon">
              <Brain size={28} />
            </div>
            <h3>Ask anything about {repoName || 'this repository'}</h3>
            <p>
              I've analyzed the codebase and can answer questions about architecture,
              specific functions, design patterns, and more.
            </p>
            <div className="chat-suggestions">
              {suggestions.map((q, i) => (
                <button
                  key={i}
                  className="chat-suggestion"
                  onClick={() => handleSuggestionClick(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((msg, index) => (
              <ChatMessage key={index} message={msg} />
            ))}

            {loading && (
              <div className="message message-assistant fade-in">
                <div className="message-avatar">
                  <Brain size={18} />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                    <div className="typing-dot" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input */}
        <div className="chat-input-area">
          <form className="chat-input-group" onSubmit={handleSubmit}>
            <textarea
              ref={inputRef}
              id="chat-input"
              className="chat-input"
              placeholder="Ask a question about the codebase..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
              rows={1}
            />
            <button
              id="chat-send-btn"
              type="submit"
              className="chat-send-btn"
              disabled={!input.trim() || loading}
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
