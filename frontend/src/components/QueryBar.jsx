import React, { useState, useRef } from 'react';
import { Search, Send, X, AlertCircle, Loader } from 'lucide-react';
import * as api from '../services/api';

/**
 * QueryBar - Natural Language Query Interface
 * Allows investigators to ask questions about the criminal network
 * Examples:
 * - "Who connects Vikram to the money laundering account?"
 * - "What's the relationship between Mumbai and Delhi syndicates?"
 * - "Show me the path from Vikram Sharma to bank accounts"
 */
export default function QueryBar({ graphData, onHighlightPath }) {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [position, setPosition] = useState({ x: window.innerWidth - 420, y: 16 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  const barRef = useRef(null);

  const handleQuery = async () => {
    if (!query.trim()) return;

    try {
      setLoading(true);
      setError(null);
      setResult(null);

      // Call backend query endpoint
      const response = await api.queryNetwork(query);

      if (response.data) {
        setResult({
          query: response.data.query,
          message: response.data.message,
          timestamp: new Date().toLocaleTimeString()
        });

        // Extract matched entity IDs from the response message and highlights
        let highlightedIds = [];
        if (response.data.matches && Array.isArray(response.data.matches)) {
          highlightedIds = response.data.matches.map(m => m.id);
        }

        // If response includes path data, highlight it on graph
        if (onHighlightPath) {
          onHighlightPath({
            nodeIds: highlightedIds,
            path: response.data.path
          });
        }
      }
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Error processing query. Make sure data is loaded first.'
      );
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleQuery();
    }
  };

  const clearResult = () => {
    setResult(null);
    setError(null);
    setQuery('');
  };

  const handleMouseDown = (e) => {
    if (barRef.current && e.target.closest('input, button')) return;
    setIsDragging(true);
    setDragOffset({
      x: e.clientX - position.x,
      y: e.clientY - position.y
    });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;

    const newX = e.clientX - dragOffset.x;
    const newY = e.clientY - dragOffset.y;

    // Keep bar within screen bounds (with 10px margin)
    const constrainedX = Math.max(10, Math.min(newX, window.innerWidth - 410));
    const constrainedY = Math.max(10, Math.min(newY, window.innerHeight - 100));

    setPosition({
      x: constrainedX,
      y: constrainedY
    });
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  React.useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, dragOffset, position]);

  return (
    <div ref={barRef} style={{
      position: 'absolute',
      top: position.y,
      left: position.x,
      zIndex: 20,
      maxWidth: 400,
      background: 'rgba(19, 27, 44, 0.95)',
      backdropFilter: 'blur(12px)',
      border: '1px solid #2e3c54',
      borderRadius: 8,
      padding: 12,
      transition: isDragging ? 'none' : 'all 0.3s ease',
      cursor: isDragging ? 'grabbing' : 'grab',
      userSelect: 'none'
    }} onMouseDown={handleMouseDown}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        marginBottom: isExpanded || result || error ? 10 : 0,
        color: '#e2e8f0',
        fontSize: '0.85rem',
        fontWeight: 500
      }}>
        <Search size={16} color="#3b82f6" />
        <span>Natural Language Query</span>
      </div>

      {/* Query Input */}
      <div style={{
        display: 'flex',
        gap: 8,
        marginBottom: result || error ? 10 : 0
      }}>
        <input
          type="text"
          placeholder="Ask about connections... (e.g., 'Who connects Vikram to money laundering?')"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={handleKeyPress}
          onFocus={() => setIsExpanded(true)}
          disabled={loading}
          style={{
            flex: 1,
            background: '#0a0f18',
            border: '1px solid #2e3c54',
            color: '#e2e8f0',
            padding: '8px 10px',
            borderRadius: 4,
            fontSize: '0.85rem',
            outline: 'none',
            opacity: loading ? 0.6 : 1,
            cursor: loading ? 'not-allowed' : 'text'
          }}
        />
        <button
          onClick={handleQuery}
          disabled={loading || !query.trim()}
          style={{
            background: loading ? '#1e3a8a' : '#3b82f6',
            border: 'none',
            color: '#fff',
            padding: '8px 12px',
            borderRadius: 4,
            cursor: loading || !query.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
            fontSize: '0.85rem',
            opacity: loading || !query.trim() ? 0.6 : 1,
            transition: 'background 0.2s'
          }}
        >
          {loading ? (
            <>
              <Loader size={14} className="animate-spin" />
              Searching...
            </>
          ) : (
            <>
              <Send size={14} />
              Ask
            </>
          )}
        </button>
      </div>

      {/* Results */}
      {result && (
        <div style={{
          background: 'rgba(34, 197, 94, 0.1)',
          border: '1px solid #22c55e',
          borderRadius: 6,
          padding: 10,
          marginBottom: 10,
          fontSize: '0.85rem',
          color: '#e2e8f0'
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'start',
            marginBottom: 8
          }}>
            <div style={{ fontWeight: 500, color: '#22c55e' }}>Query Result</div>
            <button
              onClick={clearResult}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                color: '#94a3b8',
                padding: 0,
                display: 'flex',
                alignItems: 'center'
              }}
            >
              <X size={14} />
            </button>
          </div>
          <div style={{
            fontSize: '0.8rem',
            color: '#cbd5e1',
            lineHeight: 1.8,
            maxHeight: 200,
            overflowY: 'auto',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontFamily: 'monospace'
          }}>
            {result.message}
          </div>
          <div style={{
            fontSize: '0.75rem',
            color: '#64748b',
            marginTop: 8,
            textAlign: 'right'
          }}>
            {result.timestamp}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          border: '1px solid #ef4444',
          borderRadius: 6,
          padding: 10,
          marginBottom: 10,
          fontSize: '0.85rem',
          color: '#fca5a5',
          display: 'flex',
          gap: 8,
          alignItems: 'start'
        }}>
          <AlertCircle size={14} style={{ flexShrink: 0, marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <div style={{ fontWeight: 500, marginBottom: 4 }}>Error</div>
            <div style={{ fontSize: '0.8rem', lineHeight: 1.6, wordBreak: 'break-word' }}>{error}</div>
          </div>
          <button
            onClick={() => setError(null)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              color: '#fca5a5',
              padding: 0,
              display: 'flex',
              alignItems: 'center',
              flexShrink: 0
            }}
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Examples */}
      {isExpanded && !result && !error && (
        <div style={{
          borderTop: '1px solid #2e3c54',
          paddingTop: 10,
          fontSize: '0.75rem',
          color: '#64748b'
        }}>
          <div style={{ marginBottom: 6, fontWeight: 500, color: '#94a3b8' }}>Examples:</div>
          <div style={{ lineHeight: 1.6 }}>
            • "Who connects Vikram to money laundering?"<br/>
            • "Show path between Mumbai and Delhi syndicates"<br/>
            • "What accounts are linked to Ramesh?"<br/>
            • "Find intermediaries between two suspects"
          </div>
        </div>
      )}
    </div>
  );
}
