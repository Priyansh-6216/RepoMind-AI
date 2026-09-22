import React from 'react';
import ReactMarkdown from 'react-markdown';
import { User, Brain } from 'lucide-react';
import { motion } from 'framer-motion';
import CodeCitation from './CodeCitation';

/**
 * Single chat message component — supports user and assistant roles.
 * Renders markdown for assistant messages and displays code citations.
 */
export default function ChatMessage({ message }) {
  const isUser = message.role === 'USER';

  return (
    <motion.div 
      className={`message ${isUser ? 'message-user' : 'message-assistant'}`}
      initial={{ opacity: 0, y: 15, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      <div className="message-avatar">
        {isUser ? <User size={18} /> : <Brain size={18} />}
      </div>

      <div>
        <div className="message-content">
          {isUser ? (
            <p>{message.content}</p>
          ) : (
            <ReactMarkdown
              components={{
                code({ node, inline, className, children, ...props }) {
                  if (inline) {
                    return <code {...props}>{children}</code>;
                  }
                  return (
                    <pre>
                      <code className={className} {...props}>
                        {children}
                      </code>
                    </pre>
                  );
                },
              }}
            >
              {message.content}
            </ReactMarkdown>
          )}
        </div>

        {/* Citations for assistant messages */}
        {!isUser && message.citations && message.citations.length > 0 && (
          <CodeCitation citations={message.citations} />
        )}
      </div>
    </motion.div>
  );
}
