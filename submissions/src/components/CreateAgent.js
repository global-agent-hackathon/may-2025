import React, { useState } from 'react';
import ReactDOM from 'react-dom';
import UserProfileCanvas from './UserProfileCanvas';
import DraggableAvatarCanvas from './DraggableAvatarCanvas';
import './CreateAgent.css';

const Modal = ({ children, onClose }) => {
  return ReactDOM.createPortal(
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>,
    document.body
  );
};

const CreateAgent = ({
  agentStep,
  setAgentStep,
  profileName,
  socialLinks,
  fadeOut,
  handleInputChange,
  handleLinksSubmit,
  handleProfileSave,
  setProfileData
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [linkedinName, setLinkedinName] = useState('');

  const handleLinkedInSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

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

      const data = await response.json();

      if (!response.ok) {
        // Handle specific error cases
        if (data.error === 'profile_not_accessible') {
          throw new Error('This LinkedIn profile is not accessible. Please make sure the profile is public or you have the correct permissions.');
        } else if (data.error === 'Invalid LinkedIn URL format') {
          throw new Error('Please enter a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username/)');
        } else if (data.error === 'linkedin_error') {
          throw new Error('There was an error accessing the LinkedIn profile. Please try again later.');
        } else {
          throw new Error(data.message || 'An error occurred while processing your request.');
        }
      }

      // Extract name from LinkedIn profile data
      const firstName = data.profile_data['firstName'] || '';
      const lastName = data.profile_data['lastName'] || '';
      const fullName = `${firstName} ${lastName}`.trim();
      
      if (!fullName) {
        throw new Error('Could not extract name from LinkedIn profile');
      }

      setLinkedinName(fullName);
      setProfileData(data.profile_data);
      setAgentStep('profile');
      
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <button 
        className="create-agent-button"
        onClick={() => setAgentStep('links')}
      >
        Create Your Agent
      </button>

      {agentStep === 'links' && (
        <Modal onClose={() => setAgentStep(null)}>
          <h2>Create Your Digital Twin</h2>
          <p className="modal-subtitle">Connect your social profiles to create your AI agent</p>
          <form onSubmit={handleLinkedInSubmit}>
            <div className="input-group">
              <label htmlFor="linkedin">LinkedIn</label>
              <input
                type="url"
                id="linkedin"
                name="linkedin"
                value={socialLinks.linkedin}
                onChange={handleInputChange}
                placeholder="https://linkedin.com/in/username"
                required
              />
            </div>
            <div className="input-group">
              <label htmlFor="twitter">Twitter/X</label>
              <input
                type="url"
                id="twitter"
                name="twitter"
                value={socialLinks.twitter || ""}
                onChange={handleInputChange}
                placeholder="https://twitter.com/username"
              />
            </div>
            <div className="input-group">
              <label htmlFor="instagram">Instagram</label>
              <input
                type="url"
                id="instagram"
                name="instagram"
                value={socialLinks.instagram || ""}
                onChange={handleInputChange}
                placeholder="https://instagram.com/username"
              />
            </div>
            <div className="input-group">
              <label htmlFor="github">GitHub</label>
              <input
                type="url"
                id="github"
                name="github"
                value={socialLinks.github || ""}
                onChange={handleInputChange}
                placeholder="https://github.com/username"
              />
            </div>
            {error && (
              <div className="error-message">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <circle cx="10" cy="10" r="10" fill="#FF4444"/>
                  <path d="M10 6V10M10 14H10.01" stroke="white" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <span>{error}</span>
              </div>
            )}
            <div className="button-group">
              <button type="button" className="cancel-button" onClick={() => setAgentStep(null)}>
                Cancel
              </button>
              <button 
                type="submit" 
                className="submit-button"
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Create Agent'}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {agentStep === 'profile' && (
        <Modal onClose={() => setAgentStep(null)}>
          <div className={fadeOut ? 'fade-out' : ''}>
            <UserProfileCanvas 
              name={linkedinName} 
              onSave={handleProfileSave} 
            />
          </div>
        </Modal>
      )}
    </>
  );
};

export default CreateAgent; 