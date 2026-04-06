import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const links = [
    { to: '/', label: 'Analyzer' },
    { to: '/dashboard', label: 'Dashboard' },
    { to: '/about', label: 'About' },
  ];

  return (
    <nav className="navbar-custom">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand-wrap">
          <div className="brand-icon">🛡️</div>
          <span className="brand-name">Text<span>Guard</span> AI</span>
        </Link>

        <ul className={`nav-links ${open ? 'open' : ''}`}>
          {links.map(link => (
            <li key={link.to}>
              <Link
                to={link.to}
                className={location.pathname === link.to ? 'active' : ''}
                onClick={() => setOpen(false)}
              >
                {link.label}
              </Link>
            </li>
          ))}
          <li>
            <span className="nav-badge">AI Powered</span>
          </li>
        </ul>

        <button className="navbar-toggler" onClick={() => setOpen(!open)}>
          {open ? '✕' : '☰'}
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
