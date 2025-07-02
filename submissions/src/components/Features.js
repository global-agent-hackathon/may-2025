import React from 'react';
import './Features.css';

const Features = () => {
  const features = [
    {
      number: '01',
      title: 'Create Your Agent',
      description: 'Link your public profiles. We instantly build your personal agent. No private data needed.'
    },
    {
      number: '02',
      title: 'Set Your Goal',
      description: 'Tell your agent what you want. It starts searching millions of connections immediately.'
    },
    {
      number: '03',
      title: 'Connect Through Millions',
      description: 'Your agent talks to other agents, finds the best matches, and opens new opportunities for you.'
    },
    {
      number: '04',
      title: 'Grow Your Network Map',
      description: 'See your real-time connection map. Drag, explore, and unlock your global network.'
    }
  ];

  return (
    <section className="callouts-section" id="features">
      <div className="container">
        <h2 className="section-title">How Likeminds Works</h2>
        <p className="section-tagline">A seamless process designed to extend your reach and save you time</p>
        
        <div className="callouts">
          {features.map((feature, index) => (
            <div className="callout" key={index}>
              <div className="callout-number">{feature.number}</div>
              <h3 className="callout-title">{feature.title}</h3>
              <p className="callout-desc">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features; 