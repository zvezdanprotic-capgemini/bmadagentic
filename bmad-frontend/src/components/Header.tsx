import React, { useState, useRef, useEffect } from 'react';
import { FiSettings, FiChevronDown, FiLogOut, FiUser } from 'react-icons/fi';
import type { User } from '../types';

interface HeaderProps {
  onConfigClick: () => void;
  user: User | null;
  onLogout: () => void;
}

const Header: React.FC<HeaderProps> = ({ onConfigClick, user, onLogout }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Close the menu when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        menuRef.current && 
        buttonRef.current &&
        !menuRef.current.contains(event.target as Node) && 
        !buttonRef.current.contains(event.target as Node)
      ) {
        setIsMenuOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleFigmaClick = () => {
    setIsMenuOpen(false);
    onConfigClick();
  };

  return (
    <header className="app-header">
      <h1 className="app-title">BMAD Agentic Framework</h1>
      <div className="header-actions">
        {user && (
          <div className="user-info">
            <span className="user-name">
              <FiUser className="user-icon" />
              {user.name}
            </span>
          </div>
        )}
        <div className="config-menu-container">
          <button 
            ref={buttonRef}
            onClick={() => setIsMenuOpen(!isMenuOpen)} 
            className="config-button" 
            aria-label="Configuration"
            aria-expanded={isMenuOpen}
            aria-haspopup="true"
          >
            <FiSettings />
            <FiChevronDown className="config-chevron" />
          </button>
          
          {isMenuOpen && (
            <div ref={menuRef} className="config-dropdown">
              <ul>
                <li><button onClick={handleFigmaClick}>Figma Credentials</button></li>
                {user && (
                  <li>
                    <button onClick={() => { onLogout(); setIsMenuOpen(false); }}>
                      <FiLogOut className="logout-icon" /> Logout
                    </button>
                  </li>
                )}
              </ul>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
