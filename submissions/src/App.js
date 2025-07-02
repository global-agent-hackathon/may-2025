import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import NetworkShowcase from './components/NetworkShowcase';
import Features from './components/Features';
import Experience from './components/Experience';
import Technology from './components/Technology';
import Specifications from './components/Specifications';
import Footer from './components/Footer';
import DraggableAvatarCanvas from './components/DraggableAvatarCanvas';
import './App.css';

function App() {
  // step: null | 'links' | 'profile' | 'canvas'
  const [step, setStep] = useState(null);
  const [profileName, setProfileName] = useState('');
  const [avatar, setAvatar] = useState(null);
  const [profileData, setProfileData] = useState(null);
  const [socialLinks, setSocialLinks] = useState({
    instagram: '',
    twitter: '',
    linkedin: '',
    facebook: '',
    tiktok: ''
  });
  const [fadeOut, setFadeOut] = useState(false);

  // Handlers to pass down
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setSocialLinks(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLinksSubmit = async (e) => {
    e.preventDefault();
    let name = '';
    if (socialLinks.linkedin) {
      try {
        const response = await fetch('http://localhost:5000/api/process-linkedin', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            linkedin_url: socialLinks.linkedin
          })
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch LinkedIn data');
        }
        
        const data = await response.json();
        setProfileData(data.profile_data);
        name = `${data.profile_data.firstName} ${data.profile_data.lastName}`;
      } catch (error) {
        console.error('Error fetching LinkedIn data:', error);
        const match = socialLinks.linkedin.match(/linkedin.com\/in\/([^\/]+)/);
        if (match) name = match[1].replace(/-/g, ' ');
      }
    } else if (socialLinks.instagram) {
      const match = socialLinks.instagram.match(/instagram.com\/([^\/]+)/);
      if (match) name = match[1];
    }
    setProfileName(name ? name.charAt(0).toUpperCase() + name.slice(1) : 'Your Name');
    setStep('profile');
  };

  const handleProfileSave = (profile) => {
    setAvatar(profile.avatar);
    setProfileName(profile.name);
    setFadeOut(true);
    setTimeout(() => {
      setStep('canvas');
      setFadeOut(false);
    }, 400);
  };

  // Only show the canvas if in that step
  if (step === 'canvas') {
    return <div className="fade-in"><DraggableAvatarCanvas avatar={avatar} name={profileName} profileData={profileData} /></div>;
  }

  return (
    <div className="App">
      <Navbar />
      <Hero
        agentStep={step}
        setAgentStep={setStep}
        profileName={profileName}
        setProfileName={setProfileName}
        avatar={avatar}
        setAvatar={setAvatar}
        socialLinks={socialLinks}
        setSocialLinks={setSocialLinks}
        fadeOut={fadeOut}
        handleInputChange={handleInputChange}
        handleLinksSubmit={handleLinksSubmit}
        handleProfileSave={handleProfileSave}
        setProfileData={setProfileData}
      />
      <NetworkShowcase />
      <Features />
      <Experience />
      <Technology />
      <Specifications />
      <Footer />
    </div>
  );
}

export default App;
