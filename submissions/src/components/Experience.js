import React, { useEffect } from 'react';
import './Experience.css';

const Experience = () => {
  useEffect(() => {
    const handleScroll = () => {
      const parallaxBg = document.querySelector('.parallax-bg');
      if (parallaxBg) {
        let scrollPosition = window.pageYOffset;
        parallaxBg.style.transform = 'translateY(' + scrollPosition * 0.4 + 'px)';
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <section className="parallax-section" id="experience">
      <div className="parallax-bg"></div>
      <div className="parallax-content">
        <h2 className="parallax-title">Meet Your Digital Twin</h2>
        <p className="parallax-desc">
          Experience the power of AI that truly understands you, learns from you, 
          and represents you in the digital world.
        </p>
        <a href="#" className="btn-primary">Learn How It Works</a>
      </div>
    </section>
  );
};

export default Experience; 