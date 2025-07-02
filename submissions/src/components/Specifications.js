import React from 'react';
import './Specifications.css';

const Specifications = () => {
  const techStack = [
    { name: 'Agno', logo: '/logos/agno.png' },
    { name: 'React', logo: '/logos/reactjs.png' },
    { name: 'Flask', logo: '/logos/flask.svg' },
    { name: 'OpenAI', logo: '/logos/openai.svg' },
    { name: 'Gemini', logo: '/logos/gemini.svg' },
    { name: 'Vercel', logo: '/logos/vercel.svg' }
  ];

  return (
    <section className="specs-section" id="specifications">
      <div className="container">
        <h2 className="section-title">Our Tech Stack</h2>
        <p className="section-tagline">Powered by cutting-edge technologies</p>
        
        <div className="tech-ribbon">
          {techStack.map((tech, index) => (
            <div className="tech-item" key={index}>
              <img 
                src={tech.logo} 
                alt={tech.name} 
                className="tech-logo"
                title={tech.name}
              />
              </div>
            ))}
        </div>
      </div>
    </section>
  );
};

export default Specifications; 