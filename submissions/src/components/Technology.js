import React from 'react';
import './Technology.css';

const Technology = () => {
  return (
    <section className="technology-section" id="technology">
      <div className="container">
        <h2 className="section-title">Advanced Technology</h2>
        <p className="section-tagline">Powered by cutting-edge AI designed to understand human behavior</p>
        
        <div className="chip-showcase">
          <div className="chip-info">
            <h3 className="chip-title">Powered by Advanced Multi-Agent AI</h3>
            <p className="chip-desc">
              We collect all information about you that is visible from the internet—such as your public social profiles, posts, and professional data—and securely use it to finetune your digital twin using Dora, our advanced AI engine. This process allows us to clone you as your agent, enabling seamless agent-to-agent communication while maintaining your privacy and personal preferences.
            </p>
            <a href="#" className="btn-primary">Explore Technology</a>
          </div>
          <div className="chip-visual">
            <div className="chip-glow"></div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Technology; 