import React from 'react';
import CreateAgent from './CreateAgent';
import './Hero.css';

const Hero = (props) => {
  return (
    <section className="hero-section" id="your-agent">
      <div className="hero-background"></div>
      <div className="container">
        <div className="hero-content">
          <div className="hero">
            <div className="hero-text-reveal">
              <h1 className="hero-main-title">Your Mind, Everywhere.</h1>
            </div>
            
            <p className="hero-tagline hero-subtitle">
              Create your personal agent. Talk to millions. Unlock your true network.
            </p>
            
            <div className="buttons">
              <CreateAgent {...props} />
              <a href="#" className="btn-secondary">Learn More</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero; 