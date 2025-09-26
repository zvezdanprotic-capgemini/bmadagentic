import React, { useState, useRef, useEffect } from 'react';
import { FiSettings, FiChevronDown } from 'react-icons/fi';

interface HeaderProps {
  onConfigClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onConfigClick }) => {
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
                {/* Add more menu items here as needed */}
              </ul>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
