import React, { useState } from 'react';
import { Shield, Lock, User, Activity, Eye, EyeOff } from 'lucide-react';
import * as api from '../services/api';

export default function Login({ onLoginSuccess }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!username || !password) {
      setErrorMsg('Please enter both username and password.');
      return;
    }

    try {
      setLoading(true);
      setErrorMsg('');
      const res = await api.login(username, password);

      if (res.data && res.data.access_token) {
        sessionStorage.setItem('token', res.data.access_token);
        onLoginSuccess();
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const inputStyle = {
    width: '100%',
    padding: '12px 12px 12px 40px',
    background: '#1b263b',
    border: '1px solid #2e3c54',
    borderRadius: '8px',
    color: '#e2e8f0',
    fontSize: '0.95rem',
    outline: 'none',
    transition: 'border-color 0.2s, box-shadow 0.2s'
  };

  const inputFocusHandler = (e) => {
    e.target.style.borderColor = '#3b82f6';
    e.target.style.boxShadow = '0 0 0 3px rgba(59, 130, 246, 0.15)';
  };

  const inputBlurHandler = (e) => {
    e.target.style.borderColor = '#2e3c54';
    e.target.style.boxShadow = 'none';
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: '#0b1120'
    }}>
      <div style={{
        background: '#131b2c',
        border: '1px solid #2e3c54',
        borderRadius: '16px',
        padding: '48px 40px',
        width: '100%',
        maxWidth: '420px',
        boxShadow: '0 25px 80px rgba(0, 0, 0, 0.8), 0 0 40px rgba(59, 130, 246, 0.05)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center'
      }}>
        {/* Shield Icon with subtle glow */}
        <div style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'rgba(0, 240, 255, 0.08)',
          border: '1px solid rgba(0, 240, 255, 0.2)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '20px'
        }}>
          <Shield color="#00f0ff" size={36} />
        </div>

        <h2 style={{ color: '#e2e8f0', margin: '0 0 6px 0', fontSize: '1.4rem', textAlign: 'center', fontWeight: 600 }}>
          Restricted Access
        </h2>
        <p style={{ color: '#64748b', margin: '0 0 8px 0', fontSize: '0.85rem', textAlign: 'center' }}>
          Criminal Network Intelligence System
        </p>
        <p style={{ color: '#475569', margin: '0 0 32px 0', fontSize: '0.75rem', textAlign: 'center', letterSpacing: '0.5px' }}>
          OAuth2 Secured • JWT Authentication
        </p>

        <form onSubmit={handleLogin} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {/* Username */}
          <div style={{ position: 'relative' }}>
            <User size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px', zIndex: 1 }} />
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onFocus={inputFocusHandler}
              onBlur={inputBlurHandler}
              style={inputStyle}
              autoComplete="username"
            />
          </div>

          {/* Password with toggle */}
          <div style={{ position: 'relative' }}>
            <Lock size={18} color="#64748b" style={{ position: 'absolute', left: '12px', top: '13px', zIndex: 1 }} />
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onFocus={inputFocusHandler}
              onBlur={inputBlurHandler}
              style={{ ...inputStyle, paddingRight: '40px' }}
              autoComplete="current-password"
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              style={{
                position: 'absolute',
                right: '10px',
                top: '11px',
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                padding: '2px',
                zIndex: 1
              }}
              tabIndex={-1}
            >
              {showPassword
                ? <EyeOff size={18} color="#64748b" />
                : <Eye size={18} color="#64748b" />
              }
            </button>
          </div>

          {/* Error Message */}
          {errorMsg && (
            <div style={{
              padding: '10px 14px',
              background: 'rgba(239, 68, 68, 0.08)',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              borderRadius: '8px',
              color: '#ef4444',
              fontSize: '0.85rem',
              textAlign: 'center'
            }}>
              {errorMsg}
            </div>
          )}

          {/* Login Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              marginTop: '8px',
              width: '100%',
              background: loading ? '#2563eb' : '#3b82f6',
              border: 'none',
              color: '#fff',
              padding: '13px',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.8 : 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              fontSize: '1rem',
              fontWeight: 600,
              transition: 'all 0.2s',
              letterSpacing: '0.3px'
            }}
          >
            {loading
              ? <><Activity size={18} className="animate-spin" /> Authenticating...</>
              : 'Secure Login'
            }
          </button>
        </form>

        {/* Footer */}
        <div style={{
          marginTop: '28px',
          paddingTop: '20px',
          borderTop: '1px solid #1e293b',
          width: '100%',
          textAlign: 'center'
        }}>
          <p style={{ color: '#475569', fontSize: '0.7rem', letterSpacing: '0.3px' }}>
            🔒 Encrypted with SHA-256 • Bcrypt Password Hashing
          </p>
        </div>
      </div>
    </div>
  );
}
