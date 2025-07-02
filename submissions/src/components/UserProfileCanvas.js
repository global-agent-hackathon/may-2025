import React, { useRef, useState, useEffect } from 'react';
import './UserProfileCanvas.css';
// Import all avatars
import avatarCat from '../assets/avatars/cat.png';
import avatarDog from '../assets/avatars/dog.png';
import avatarFox from '../assets/avatars/fox.png';
import avatarOwl from '../assets/avatars/owl.png';
import avatarBear from '../assets/avatars/bear.png';
import avatarBird from '../assets/avatars/bird.png';
import avatarDragon from '../assets/avatars/dragon.png';
import avatarLion from '../assets/avatars/lion.png';
import avatarTurtle from '../assets/avatars/turtle.png';
import avatarWolf from '../assets/avatars/wolf.png';
import avatarZebra from '../assets/avatars/zebra.png';

// Create an array of available avatars outside the component to avoid recreating it on each render
const avatarsList = [
  avatarCat,
  avatarDog,
  avatarFox,
  avatarOwl,
  avatarBear,
  avatarBird,
  avatarDragon,
  avatarLion,
  avatarTurtle,
  avatarWolf,
  avatarZebra
];

// Function to get a random avatar
const getRandomAvatar = () => {
  const randomIndex = Math.floor(Math.random() * avatarsList.length);
  return avatarsList[randomIndex];
};

const UserProfileCanvas = ({ name, onSave }) => {
  // Initialize with a random avatar directly instead of null
  const [avatar, setAvatar] = useState(getRandomAvatar());
  const [userName, setUserName] = useState(name || 'Your Name');
  const fileInputRef = useRef(null);

  // Ensure avatar is random every time the component is rendered with a new instance
  useEffect(() => {
    setAvatar(getRandomAvatar());
  }, []);

  // Generate a new random avatar if requested
  const generateNewRandomAvatar = () => {
    setAvatar(getRandomAvatar());
  };

  const handleAvatarClick = () => {
    fileInputRef.current.click();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        setAvatar(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    try {
      // First call the parent's onSave
      onSave({ name: userName, avatar });

      // Then send to Flask backend
      const response = await fetch('http://localhost:5000/api/social-profiles/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ name: userName, avatar })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Backend response:', data);
    } catch (error) {
      console.error('Error saving profile:', error);
      if (error.message.includes("This profile can't be accessed") || error.message.includes("request failed")) {
        throw new Error("This profile can't be accessed");
      }
    }
  };

  return (
    <div className="profile-canvas-container">
      <div className="avatar-wrapper">
        <img src={avatar} alt="avatar" className="avatar-img" />
        <div className="avatar-controls">
        <button className="edit-avatar-btn" onClick={handleAvatarClick}>
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="10" fill="#2979FF"/>
            <path d="M7.5 13.5H12.5M8.5 10.5L13.5 5.5M13.5 5.5L14.5 6.5M13.5 5.5L11.5 7.5M6.5 12.5L11.5 7.5" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
          <button className="randomize-avatar-btn" onClick={generateNewRandomAvatar} title="Get random avatar">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="10" cy="10" r="10" fill="#2979FF"/>
              <path d="M6 10H14M14 10L11 7M14 10L11 13" stroke="white" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </div>
        <input
          type="file"
          accept="image/*"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
      </div>
      <h2 className="profile-name">{userName}</h2>
      <form className="profile-form" onSubmit={handleSave}>
        <label htmlFor="profile-name-input">Name</label>
        <input
          id="profile-name-input"
          className="profile-name-input"
          type="text"
          value={userName}
          onChange={e => setUserName(e.target.value)}
        />
        <button className="profile-save-btn" type="submit">Save</button>
      </form>
    </div>
  );
};

export default UserProfileCanvas; 