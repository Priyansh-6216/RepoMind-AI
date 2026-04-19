import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import ChatPanel from '../components/ChatPanel';
import LoadingSpinner from '../components/LoadingSpinner';
import {
  getRepo, sendChatMessage, getChatSessions, getSessionMessages,
} from '../api/client';

/**
 * Chat page — full-screen chat interface with session management.
 */
export default function ChatPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [repo, setRepo] = useState(null);
  const [messages, setMessages] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pageLoading, setPageLoading] = useState(true);

  useEffect(() => {
    init();
  }, [id]);

  const init = async () => {
    try {
      const [repoRes, sessionsRes] = await Promise.all([
        getRepo(id),
        getChatSessions(id),
      ]);
      setRepo(repoRes.data);
      setSessions(sessionsRes.data);

      // Load most recent session if exists
      if (sessionsRes.data.length > 0) {
        const latestSession = sessionsRes.data[0];
        await loadSession(latestSession.id);
      }
    } catch (err) {
      console.error('Failed to init chat page:', err);
    } finally {
      setPageLoading(false);
    }
  };

  const loadSession = async (sessionId) => {
    try {
      const { data } = await getSessionMessages(id, sessionId);
      setMessages(data);
      setActiveSessionId(sessionId);
    } catch (err) {
      console.error('Failed to load session:', err);
    }
  };

  const handleSendMessage = async (question) => {
    // Add user message to UI immediately
    setMessages((prev) => [
      ...prev,
      { role: 'USER', content: question },
    ]);
    setLoading(true);

    try {
      const { data } = await sendChatMessage(id, question, activeSessionId);

      // Add assistant message
      setMessages((prev) => [
        ...prev,
        {
          role: 'ASSISTANT',
          content: data.answer,
          citations: data.citations,
        },
      ]);

      // Update session ID if new session was created
      if (data.sessionId && data.sessionId !== activeSessionId) {
        setActiveSessionId(data.sessionId);
        // Refresh sessions list
        const { data: sessionsData } = await getChatSessions(id);
        setSessions(sessionsData);
      }
    } catch (err) {
      console.error('Chat failed:', err);
      setMessages((prev) => [
        ...prev,
        {
          role: 'ASSISTANT',
          content: 'Sorry, I encountered an error processing your question. Please try again.',
          citations: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectSession = (sessionId) => {
    loadSession(sessionId);
  };

  const handleNewSession = () => {
    setActiveSessionId(null);
    setMessages([]);
  };

  if (pageLoading) return <LoadingSpinner size="lg" text="Loading chat..." />;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3 }}
    >
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        marginBottom: '1rem',
      }}>
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => navigate(`/repo/${id}`)}
        >
          <ArrowLeft size={16} /> Back to {repo?.name}
        </button>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
          Chat with <span style={{ color: 'var(--accent-blue)' }}>{repo?.name}</span>
        </h2>
      </div>

      <ChatPanel
        messages={messages}
        sessions={sessions}
        activeSessionId={activeSessionId}
        onSendMessage={handleSendMessage}
        onSelectSession={handleSelectSession}
        onNewSession={handleNewSession}
        loading={loading}
        repoName={repo?.name}
      />
    </motion.div>
  );
}
