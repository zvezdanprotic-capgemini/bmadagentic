import React, { useState } from 'react';

interface RegisterProps {
  onRegister: (username: string, password: string, name: string, email?: string) => Promise<void>;
  onToggleForm: () => void;
  isLoading: boolean;
  error: string | null;
}

export const Register: React.FC<RegisterProps> = ({ onRegister, onToggleForm, isLoading, error }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onRegister(username, password, name, email || undefined);
  };

  return (
    <div className="auth-container">
      <h2 className="auth-title">Create an Account</h2>
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
          <label htmlFor="name">Full Name</label>
          <input
            type="text"
            id="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            disabled={isLoading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="email">Email (optional)</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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
            minLength={6}
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
              Creating Account...
            </>
          ) : 'Register'}
        </button>
      </form>
      
      <div className="auth-toggle">
        Already have an account? {' '}
        <button onClick={onToggleForm} disabled={isLoading}>
          Login
        </button>
      </div>
    </div>
  );
};