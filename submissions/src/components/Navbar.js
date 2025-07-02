import React, { useState, useEffect } from 'react';
import './Navbar.css';
import logo from '../assets/logo.png';

const Navbar = () => {
  const [activeLink, setActiveLink] = useState('');

  useEffect(() => {
    const handleScroll = () => {
      const sections = document.querySelectorAll('section');
      sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 60) {
          setActiveLink(section.id);
        }
      });
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleClick = (e, id) => {
    e.preventDefault();
    const element = document.getElementById(id);
    if (element) {
      window.scrollTo({
        top: element.offsetTop - 50,
        behavior: 'smooth'
      });
    }
  };

  return (
    <div className="nav-wrapper">
      <nav className="nav">
        <a href="#" className="nav-logo">
          <img src={logo} alt="Likeminds Logo" />
        </a>
        <ul className="nav-menu">
          <li><a href="#your-agent" onClick={(e) => handleClick(e, 'your-agent')}>Your Agent</a></li>
          <li><a href="#features" onClick={(e) => handleClick(e, 'features')}>How It Works</a></li>
          <li><a href="#experience" onClick={(e) => handleClick(e, 'experience')}>Digital Twin</a></li>
          <li><a href="#technology" onClick={(e) => handleClick(e, 'technology')}>Technology</a></li>
        </ul>
        <div className="nav-indicator"></div>
      </nav>
    </div>
  );
};

export default Navbar; 