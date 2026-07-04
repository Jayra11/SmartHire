import React from 'react';

interface NavigationProps {
  activeTab: 'upload' | 'dashboard';
  setActiveTab: (tab: 'upload' | 'dashboard') => void;
}

const Navigation: React.FC<NavigationProps> = ({ activeTab, setActiveTab }) => {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <a href="/" className="logo">
          <span>🚀</span>
          Jetski SmartHire
        </a>
        <ul className="nav-links">
          <li>
            <button
              className={activeTab === 'upload' ? 'active' : ''}
              onClick={() => setActiveTab('upload')}
            >
              Screen Resume
            </button>
          </li>
          <li>
            <button
              className={activeTab === 'dashboard' ? 'active' : ''}
              onClick={() => setActiveTab('dashboard')}
            >
              Dashboard
            </button>
          </li>
        </ul>
      </div>
    </nav>
  );
};

export default Navigation;
