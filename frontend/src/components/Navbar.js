import React, { useState, useEffect } from 'react';
import './Navbar.css'; // Or wherever you keep your CSS for the nav

function Navbar() {
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const theme = localStorage.getItem('theme');
    return theme ? theme === 'dark' : true;
  });

  useEffect(() => {
    if (isDarkMode) {
      document.body.classList.remove('light-mode');
      document.body.classList.add('dark-mode');
      localStorage.setItem('theme', 'dark');
    } else {
      document.body.classList.remove('dark-mode');
      document.body.classList.add('light-mode');
      localStorage.setItem('theme', 'light');
    }
  }, [isDarkMode]);

  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  return (
    <nav className="navbar-container">
      <div className="navbar-left">
        <h2>AutoTrade v0.1</h2>
      </div>
      <div className="navbar-right">
        <button onClick={toggleTheme} className="theme-toggle-btn" aria-label="Toggle theme">
          {isDarkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-toggle-on" viewBox="0 0 16 16">
              <path d="M5 3a5 5 0 0 0 0 10h6a5 5 0 0 0 0-10zm6 9a4 4 0 1 1 0-8 4 4 0 0 1 0 8"/>
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" fill="currentColor" class="bi bi-toggle-off" viewBox="0 0 16 16">
              <path d="M11 4a4 4 0 0 1 0 8H8a5 5 0 0 0 2-4 5 5 0 0 0-2-4zm-6 8a4 4 0 1 1 0-8 4 4 0 0 1 0 8M0 8a5 5 0 0 0 5 5h6a5 5 0 0 0 0-10H5a5 5 0 0 0-5 5"/>
            </svg>
          )}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
