import React from 'react';
import './NetworkShowcase.css';
import heroImage from '../assets/hero.png';

const NetworkShowcase = () => {
  return (
    <section className="network-showcase">
      <div className="container">
        <div className="network-container">
          <div className="network-glow"></div>
          <img src={heroImage} alt="Network Connections" className="network-image" />
          <div className="network-reflection"></div>
        </div>
      </div>
    </section>
  );
};

export default NetworkShowcase; 