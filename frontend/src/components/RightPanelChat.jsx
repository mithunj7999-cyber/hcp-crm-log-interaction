import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendChatMessage } from '../store/hcpSlice';
import { Bot, Send, User } from 'lucide-react';

export default function RightPanelChat() {
  const dispatch = useDispatch();
  const chatMessages = useSelector((state) => state.hcp.chatMessages);
  const loadingChat = useSelector((state) => state.hcp.loadingChat);
  const [input, setInput] = useState('');
  
  const bottomRef = useRef(null);

  // Auto scroll to latest messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, loadingChat]);

  const handleSend = (e) => {
    e.preventDefault();
    if (!input.trim() || loadingChat) return;

    const messageText = input;
    setInput('');

    // Append human message to local history
    dispatch({
      type: 'hcp/addChatMessage',
      payload: { role: 'user', content: messageText }
    });

    // Strip out system instructions/non-standard fields from local history for the API
    const cleanHistory = chatMessages.map(m => ({
      role: m.role,
      content: m.content
    }));

    dispatch(sendChatMessage({ message: messageText, history: cleanHistory }));
  };

  return (
    <div className="panel" style={{ borderLeft: '1px solid var(--border-glass)' }}>
      <div className="panel-header">
        <Bot size={20} />
        <h2>AI Interaction Assistant</h2>
      </div>

      <div className="chat-container">
        <div className="chat-history">
          {chatMessages.map((m, idx) => (
            <div 
              key={idx} 
              className={`message-bubble ${m.role}`}
            >
              <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.25rem', opacity: 0.8 }}>
                {m.role === 'user' ? (
                  <>
                    <span style={{ fontSize: '0.7rem', fontWeight: '600' }}>REP</span>
                    <User size={12} />
                  </>
                ) : (
                  <>
                    <Bot size={12} />
                    <span style={{ fontSize: '0.7rem', fontWeight: '600' }}>AI ASSISTANT</span>
                  </>
                )}
              </div>
              <p style={{ whiteSpace: 'pre-line' }}>{m.content}</p>
            </div>
          ))}
          
          {loadingChat && (
            <div className="message-bubble assistant">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>

        <div className="chat-input-area">
          <form onSubmit={handleSend} className="chat-input-wrapper">
            <input
              type="text"
              placeholder="E.g., Met Dr. Sarah Chen today to discuss OncoBoost..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loadingChat}
            />
            <button 
              type="submit" 
              className="send-btn"
              disabled={loadingChat || !input.trim()}
            >
              <Send size={16} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
