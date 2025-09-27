import React, { useState } from 'react';

interface LoginProps {
  onLogin: (username: string, password: string) => Promise<void>;
  onToggleForm: () => void;
  isLoading: boolean;
  error: string | null;
}

export const Login: React.FC<LoginProps> = ({ onLogin, onToggleForm, isLoading, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onLogin(username, password);
  };

  return (
    <div className="auth-container">
      <h2 className="auth-title">Login to BMAD</h2>
      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        
        {error && <div className="auth-error">{error}</div>}
        
        <button 
          type="submit" 
          className="auth-button"
          disabled={isLoading}
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              Logging in...
            </>
          ) : 'Login'}
        </button>
      </form>
      <div className="auth-toggle">
        Don't have an account? 
        <button onClick={onToggleForm} disabled={isLoading}>
          Register
        </button>
      </div>
    </div>
  );
};

export default Login;