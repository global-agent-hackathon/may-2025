import React, { useRef, useState, useEffect, useLayoutEffect } from 'react';
import './DraggableAvatarCanvas.css';
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
import linkedinLogo from '../assets/platform/linkedin.png';
import xLogo from '../assets/platform/X.png';
import insLogo from '../assets/platform/insta_icon.ico';
import ChatEdit from './ChatEdit'; // Import the new component

// Define an icon for generic expanded nodes if specific ones aren't available
// import defaultNodeIcon from '../assets/avatars/node_icon.png'; // Removed for now

// Create an array of available avatars
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

const LOADING_ANIMATION_CONFIG = {
  numAvatars: 5, // Reduced to ensure we don't run out of unique avatars
  orbitRadius: 120,
  connectionSpeed: 0.02,
  avatarSize: 40,
  connectionColor: 'rgba(0, 122, 255, 0.3)',
  connectionWidth: 2,
  pulseColor: 'rgba(0, 122, 255, 0.15)',
  minScale: 0.9,
  maxScale: 1.1,
  zoomDuration: 1000,
  rotationSpeed: 0.001
};

// Function to get a random avatar from the list
const getRandomAvatar = () => {
  const randomIndex = Math.floor(Math.random() * avatarsList.length);
  return avatarsList[randomIndex];
};

// Function to get random unique avatars
const getRandomUniqueAvatars = (count) => {
  const shuffled = [...avatarsList].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
};

const DOT_SPACING = 36; // px - increased for more minimalist look
const DOT_RADIUS = 2; // px - slightly smaller dots
const DOT_COLOR = 'rgba(0, 122, 255, 0.08)'; // Apple blue with lower opacity
const AVATAR_SIZE = 120; // px
const CONNECTION_LINE_COLOR = 'rgba(0, 122, 255, 0.30)'; // Apple blue
const CONNECTION_LINE_WIDTH = 2; // Thinner lines for minimalist look
const Y_OFFSET = 100; // px, vertical offset for connection lines
const LOADING_MESSAGES = [
  "Searching through our multi-agent network...",
  "Analyzing potential connections...",
  "Simulating agent interactions...",
  "Evaluating profile matches...",
  "Generating personalized recommendations..."
];

const EXPANDED_NODE_AVATAR_SIZE = 40; // px, size of the avatar for expanded nodes
const EXPANDED_NODE_ORBIT_RADIUS = 90; // px, distance from parent node to expanded nodes
const EXPANDED_CONNECTION_LINE_COLOR = 'rgba(0, 122, 255, 0.25)';
const EXPANDED_CONNECTION_LINE_WIDTH = 1.5;
const EXPANDED_NODE_FONT_SIZE = 10; // px, font size for text below expanded node

// Define specific icons for each node type
const NODE_ICONS = {
  'Professional Background': '💼', // Briefcase for professional background
  'Achievement': '🏆',           // Trophy for achievements
  'Expertise': '🧠',            // Brain for expertise
  'Timeline': '📅',             // Calendar for timeline
  'default': '📝'               // Default icon
};

// Define the EMOJI_LIST as before but with these specific icons removed
const EMOJI_LIST = ['🚀','📊','💬','🧩','📈','💼','📌','📝','🎯','🪄','🤖','🏁','🗂️','🔍','🏢','🤝','🧭','⚡','🧾','🔧','🗣️','📣','🌐','🕹️','📚','💡','💳','🪙','📦','📠','📁','📤','📥','🗃️','🖋️','🧮','💹'];

function getGridDots(width, height) {
  const dots = [];
  for (let x = DOT_SPACING / 2; x < width; x += DOT_SPACING) {
    for (let y = DOT_SPACING / 2; y < height; y += DOT_SPACING) {
      dots.push({ x, y });
    }
  }
  return dots;
}

// Helper to get platform logo and alt text
const getPlatformLogo = (platform) => {
  if (!platform) return null;
  
  // Make sure we're only checking strings
  const platformStr = String(platform).toLowerCase();
  
  if (platformStr.includes('linkedin')) return { logo: linkedinLogo, alt: 'LinkedIn' };
  if (platformStr.includes('twitter') || platformStr.includes('x')) return { logo: xLogo, alt: 'Twitter/X' };
  if (platformStr.includes('instagram')) return { logo: insLogo, alt: 'Instagram' };
  
  return null;
};

const DraggableAvatarCanvas = ({ avatar, name, profileData }) => {
  // Use a random avatar if none is provided
  const [userAvatar, setUserAvatar] = useState(avatar || getRandomAvatar());
  
  // Ensure user avatar is set when component mounts or avatar prop changes
  useEffect(() => {
    if (!avatar) {
      setUserAvatar(getRandomAvatar());
    } else {
      setUserAvatar(avatar);
    }
  }, [avatar]);

  const canvasRef = useRef(null);
  const [avatarLifted, setAvatarLifted] = useState(false);
  const [showChat, setShowChat] = useState(false);
  const [showChatBox, setShowChatBox] = useState(true);
  const [showProfileInfo, setShowProfileInfo] = useState(false);
  const [showUserProfileInfo, setShowUserProfileInfo] = useState(false);
  const [chat, setChat] = useState([
    { from: 'agent', text: '' }
  ]);
  const [input, setInput] = useState('');
  const [canvasSize, setCanvasSize] = useState({ width: window.innerWidth, height: window.innerHeight });
  const [isLoading, setIsLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [serverStatus, setServerStatus] = useState('checking');
  const [retryCount, setRetryCount] = useState(0);
  const [searchResults, setSearchResults] = useState([]);                                        
  const [loadingMessageIndex, setLoadingMessageIndex] = useState(0);
  const [showLoadingScreen, setShowLoadingScreen] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [rotation, setRotation] = useState(0);
  const animationFrameRef = useRef(null);
  const lastTimeRef = useRef(0);
  const MAX_RETRIES = 3;
  const RETRY_DELAY = 2000; // 2 seconds
  const [selectedProfile, setSelectedProfile] = useState(null);
  const [loadingAnimationState, setLoadingAnimationState] = useState({
    phase: 0,
    connections: [],
    pulseRadius: 0,
    pulseOpacity: 0,
    scale: 1,
    rotation: 0,
    zoomDirection: 1,
    avatarScales: Array(LOADING_ANIMATION_CONFIG.numAvatars).fill(1),
    selectedAvatars: getRandomUniqueAvatars(LOADING_ANIMATION_CONFIG.numAvatars)
  });
  // Add new state for edit dialog
  const [showEditDialog, setShowEditDialog] = useState(false);
  const [messageToEdit, setMessageToEdit] = useState(''); // Renamed for clarity

  // State for expanded nodes: { [profileId: string]: { isLoading: boolean, error: string | null, nodes: Array<NodeInfo> } }
  // NodeInfo: { id: string, text: string, source: string, avatar?: string, position?: {x, y}, emoji?: string }
  const [expandedNodesData, setExpandedNodesData] = useState({});

  // Add new state for displaying expanded node details
  const [selectedExpandedNodeInfo, setSelectedExpandedNodeInfo] = useState(null);
  const [showExpandedNodeDetailModal, setShowExpandedNodeDetailModal] = useState(false);

  // Add state for expand loading stage
  const [expandLoadingStage, setExpandLoadingStage] = useState(null);
  const [expandingProfileId, setExpandingProfileId] = useState(null);

  // Animation loop
  useLayoutEffect(() => {
    const animate = (timestamp) => {
      if (!lastTimeRef.current) lastTimeRef.current = timestamp;
      const deltaTime = timestamp - lastTimeRef.current;
      
      if (deltaTime > 16) { // ~60fps
        // Remove the continuous rotation by setting increment to 0
        setRotation(prev => prev); // Keep the same rotation value
        lastTimeRef.current = timestamp;
      }
      
      animationFrameRef.current = requestAnimationFrame(animate);
    };

    // Start animation
    animationFrameRef.current = requestAnimationFrame(animate);

    // Cleanup
    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, []);

  // Check server status on component mount
  useEffect(() => {
    checkServerHealth();
  }, []);

  // Update loading messages
  useEffect(() => {
    if (showLoadingScreen) {
      const interval = setInterval(() => {
        setLoadingMessageIndex(prev => (prev + 1) % LOADING_MESSAGES.length);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [showLoadingScreen]);

  // Update loading progress
  useEffect(() => {
    if (showLoadingScreen && loadingProgress < 100) {
      const interval = setInterval(() => {
        setLoadingProgress(prev => Math.min(prev + 1, 100));
      }, 50);
      return () => clearInterval(interval);
    }
  }, [showLoadingScreen, loadingProgress]);

  // Assign a unique animal avatar to each search result if not present, and never repeat the user's avatar
  useEffect(() => {
    setSearchResults(prevResults => {
      if (!prevResults || prevResults.length === 0) return prevResults;
      
      // Exclude the user's avatar from the pool
      const filteredAvatars = avatarsList.filter(a => a !== userAvatar);
      
      // Shuffle avatars for this batch
      const shuffledAvatars = [...filteredAvatars].sort(() => 0.5 - Math.random());
      
      return prevResults.map((result, idx) => {
        // Make sure we preserve any existing data in the profile object
        return {
          ...result,
          profile: {
            ...result.profile,
            // Always assign a random animal avatar, overriding any existing avatar
            avatar: shuffledAvatars[idx % shuffledAvatars.length]
          }
        };
      });
    });
  }, [searchResults.length, userAvatar]);

  const checkServerHealth = async () => {
    try {
      const response = await fetch('http://localhost:5000/api/health');
      const data = await response.json();
      setServerStatus(data.status === 'healthy' ? 'healthy' : 'unhealthy');
    } catch (error) {
      setServerStatus('unavailable');
      console.error('Server health check failed:', error);
    }
  };

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const fetchWithRetry = async (url, options, retries = MAX_RETRIES) => {
    try {
      // Check server status before making request
      if (serverStatus !== 'healthy') {
        await checkServerHealth();
        if (serverStatus !== 'healthy') {
          throw new Error('Server is not available');
        }
      }

      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      if (retries > 0) {
        setStatusMessage(`Connection error. Retrying in ${RETRY_DELAY/1000} seconds... (${retries} attempts left)`);
        await sleep(RETRY_DELAY);
        return fetchWithRetry(url, options, retries - 1);
      }
      throw error;
    }
  };

  // Center the avatar on mount and update grid on resize
  useEffect(() => {
    const updateCanvasSize = () => {
      const canvas = canvasRef.current;
      if (canvas) {
        const rect = canvas.getBoundingClientRect();
        setCanvasSize({ width: rect.width, height: rect.height });
      }
    };
    updateCanvasSize();
    window.addEventListener('resize', updateCanvasSize);
    return () => window.removeEventListener('resize', updateCanvasSize);
  }, []);

  // Animate avatar up and show chat
  useEffect(() => {
    setTimeout(() => setAvatarLifted(true), 400);
    setTimeout(() => setShowChat(true), 900);
  }, []);

  // Update the agent intro message if name changes
  useEffect(() => {
    setChat(prev => {
      const intro = { from: 'agent', text: `Hi, I'm ${name || 'your agent'}, another you. What can I help you network today?` };
      if (prev.length === 0) return [intro];
      if (prev[0].from === 'agent') {
        return [intro, ...prev.slice(1)];
      }
      return [intro, ...prev];
    });
  }, [name]);

  const handleAvatarClick = () => {
    setShowProfileInfo(true);
    setShowUserProfileInfo(true);
  };

  const handleInputChange = (e) => setInput(e.target.value);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    
    if (serverStatus !== 'healthy') {
      setChat(prev => [...prev, { 
        from: 'agent', 
        text: "The server is not available. Please make sure the backend server is running and try again." 
      }]);
      setStatusMessage('Server unavailable');
      return;
    }
    
    setChat(prev => [...prev, { from: 'user', text: input }]);
    setIsLoading(true);
    setRetryCount(0);
    setShowLoadingScreen(true);
    setLoadingProgress(0);
    
    try {
      const data = await fetchWithRetry('http://localhost:5000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          query: input,
          user_profile: profileData || {}
        })
      });
      
      if (data.success) {
        setSearchResults(data.profiles || []);
        
        let messageParts = []; 
        if (data.profiles && data.profiles.length > 0) {
          messageParts.push("I found these profiles:\n"); 
          data.profiles.forEach((profile, index) => {
            // Start with a newline and bullet point
            messageParts.push(`\n• ${profile.profile.name}`); 
            
            // Add platform icon if available
            const platformInfo = getPlatformLogo(profile.profile.platform);
            if (platformInfo && platformInfo.logo) {
              messageParts.push(" ");
              messageParts.push({ type: 'image', src: platformInfo.logo, alt: platformInfo.alt, style: { width: '16px', height: '16px' } });
            }
          });
          messageParts.push('\n'); 
        } else {
          messageParts.push("No matching profiles found. Try adjusting your search criteria.");
        }
        setChat(prev => [...prev, { from: 'agent', text: messageParts }]);
        setStatusMessage('');
      } else {
        let errorMessage = data.message || "Sorry, I couldn't process your request.";
        setChat(prev => [...prev, { from: 'agent', text: errorMessage }]);
        setStatusMessage('Search failed. Please try again.');
      }
    } catch (error) {
      console.error('Error in handleSend:', error);
      const errorMessage = retryCount < MAX_RETRIES 
        ? "Connection error. Retrying..."
        : serverStatus === 'unavailable'
          ? "The server is not available. Please make sure the backend server is running and try again."
          : "Unable to connect to the server. Please check your internet connection and try again later.";
      
      setChat(prev => [...prev, { from: 'agent', text: errorMessage }]);
      
      if (retryCount < MAX_RETRIES) {
        setRetryCount(prev => prev + 1);
        setStatusMessage(`Retrying in ${RETRY_DELAY/1000} seconds... (${MAX_RETRIES - retryCount} attempts left)`);
      } else {
        setStatusMessage('Connection failed. Please try again later.');
      }
    } finally {
      setIsLoading(false);
      setInput('');
      setShowLoadingScreen(false);
      setLoadingProgress(0);
    }
  };

  const dots = getGridDots(canvasSize.width, canvasSize.height);

  // Add a vertical offset (e.g., 80px or 100px)
  const verticalOffset = 180; // Increased to move avatar further below center
  const centerY = canvasSize.height / 2 + verticalOffset - (avatarLifted ? 100 : 0);
  const orbitRadius = 180; // Distance from center to orbiting avatars

  // Calculate positions for search result avatars in a circle (now with rotation)
  const orbitCenterX = canvasSize.width / 2;
  const orbitCenterY = centerY - Y_OFFSET;
  const resultAvatars = searchResults.map((result, index) => {
    const angle = rotation + (2 * Math.PI * index) / searchResults.length;
    const x = orbitCenterX + orbitRadius * Math.cos(angle);
    const y = orbitCenterY + orbitRadius * Math.sin(angle);
    return {
      ...result,
      position: { x, y }
    };
  });

  // Loading animation effect
  useEffect(() => {
    if (!showLoadingScreen) return;

    let animationFrameId;
    let startTime = Date.now();
    const animationDuration = 3000; // 3 seconds per phase

    const animate = () => {
      const currentTime = Date.now();
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / animationDuration, 1);

      if (progress >= 1) {
        // Move to next phase with zoom transition
        setLoadingAnimationState(prev => ({
          ...prev,
          phase: (prev.phase + 1) % 3,
          pulseRadius: 0,
          pulseOpacity: 0,
          zoomDirection: -prev.zoomDirection, // Reverse zoom direction
          scale: prev.zoomDirection === 1 ? LOADING_ANIMATION_CONFIG.maxScale : LOADING_ANIMATION_CONFIG.minScale
        }));
        startTime = currentTime;
      } else {
        // Update animation state based on current phase
        setLoadingAnimationState(prev => {
          const newState = { ...prev };
          
          // Update rotation
          newState.rotation = prev.rotation; // Keep rotation fixed instead of incrementing
          
          // Update scale with smooth transition
          const targetScale = prev.zoomDirection === 1 ? 
            LOADING_ANIMATION_CONFIG.maxScale : 
            LOADING_ANIMATION_CONFIG.minScale;
          newState.scale = 1 + (targetScale - 1) * progress;
          
          // Update individual avatar scales with wave effect
          newState.avatarScales = prev.avatarScales.map((scale, index) => {
            const waveOffset = (index / LOADING_ANIMATION_CONFIG.numAvatars) * Math.PI * 2;
            const wave = Math.sin(progress * Math.PI * 2 + waveOffset);
            return 1 + wave * 0.2; // Scale between 0.8 and 1.2
          });
          
          switch (prev.phase) {
            case 0: // Initial phase - avatars moving into position
              newState.connections = [];
              break;
            
            case 1: // Forming connections
              const numConnections = Math.floor(progress * (LOADING_ANIMATION_CONFIG.numAvatars * 2));
              newState.connections = Array.from({ length: numConnections }, (_, i) => ({
                from: i % LOADING_ANIMATION_CONFIG.numAvatars,
                to: (i + 1) % LOADING_ANIMATION_CONFIG.numAvatars,
                progress: Math.min(1, (progress * 2) - (i / numConnections))
              }));
              break;
            
            case 2: // Pulsing network
              newState.pulseRadius = progress * LOADING_ANIMATION_CONFIG.orbitRadius * 1.5;
              newState.pulseOpacity = Math.sin(progress * Math.PI) * 0.5;
              break;

            default:
              newState.phase = 0;
              newState.connections = [];
              newState.pulseRadius = 0;
              newState.pulseOpacity = 0;
              break;
          }
          
          return newState;
        });
      }

      animationFrameId = requestAnimationFrame(animate);
    };

    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, [showLoadingScreen]);

  // Hide chatbox when loading finishes
  useEffect(() => {
    if (!showLoadingScreen) {
      setShowChatBox(false);
    }
  }, [showLoadingScreen]);

  // Add a function to handle the edit dialog open
  const handleEditClick = (message) => {
    setMessageToEdit(message);
    setShowEditDialog(true);
  };

  const handleCloseEditDialog = () => {
    setShowEditDialog(false);
  };

  const handleSaveEditMessage = (newMessage) => {
    if (selectedProfile && selectedProfile.analysis) {
      setSelectedProfile({
        ...selectedProfile,
        analysis: {
          ...selectedProfile.analysis,
          opening_message: newMessage
        }
      });
    }
    setShowEditDialog(false);
  };

  // Function to handle "Expand" click
  const handleExpandClick = async (profileToExpand) => {
    if (!profileToExpand || !profileToExpand.profile) return;

    setShowProfileInfo(false);
    setShowUserProfileInfo(false);

    const profileId = profileToExpand.profile.profile_url || profileToExpand.profile.name;

    if (expandedNodesData[profileId] && expandedNodesData[profileId].nodes && expandedNodesData[profileId].nodes.length > 0) {
      // If nodes exist, toggle visibility by removing them (to collapse) or re-fetching if desired
      // For now, this will effectively collapse. To re-fetch, one might clear just the nodes array.
      setExpandedNodesData(prev => {
        const newData = {...prev};
        if (newData[profileId]) { // Check if profileId entry exists
          // Toggle: if nodes are present, remove them to collapse
          // If you want to allow re-expanding and re-fetching fresh data, you might do this:
          // delete newData[profileId]; 
          // Or to just clear nodes for re-fetch on next click while keeping loading state managed:
          newData[profileId].nodes = []; // Clears nodes, next click will re-fetch
        }
        return newData;
      });
      // If we just cleared nodes to allow re-fetch on *next* click, we might want to return here
      // or proceed to fetch if the intent is immediate re-fetch on collapse->expand action.
      // The current logic below will proceed to fetch if nodes were cleared.
      // If the intent is just to collapse, we should return after clearing.
      // Based on user asking for circles, let's assume collapse and then re-expand fetches.
      // So, if we found nodes and cleared them, the next click will trigger the fetch part.
      // Let's refine: if nodes exist, just remove them (collapse). Don't re-fetch immediately.
      if (expandedNodesData[profileId]?.nodes?.length > 0) {
         setExpandedNodesData(prev => {
            const newData = {...prev };
            delete newData[profileId]; // This will collapse the node
            return newData;
        });
        return; // Collapsed, so stop here.
      }
    }

    setExpandingProfileId(profileId);
    setExpandLoadingStage("Initializing expansion");
    setExpandedNodesData(prev => ({
      ...prev,
      [profileId]: { isLoading: true, error: null, nodes: [] }
    }));

    try {
      setExpandLoadingStage("Expanding your search...");
      const response = await fetch('http://localhost:5000/api/expand-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profileId: profileId, profileData: profileToExpand.profile })
      });
      setExpandLoadingStage("Processing profile data");
      if (!response.ok) throw new Error(`API error: ${response.status}`);
      const data = await response.json();
      setExpandLoadingStage("Generating nodes");
      
      // Use specific icons based on node source instead of random emojis
      const newNodesWithIcons = (data.nodes || []).map(n => ({
        ...n,
        emoji: NODE_ICONS[n.source] || NODE_ICONS['default']
      }));
      
      setTimeout(() => {
        setExpandedNodesData(prev => ({
          ...prev,
          [profileId]: { isLoading: false, error: null, nodes: newNodesWithIcons }
        }));
        setExpandLoadingStage(null);
        setExpandingProfileId(null);
      }, 500);

    } catch (error) {
      console.error("Failed to expand profile:", error);
      setExpandLoadingStage("Error: " + error.message);
      setTimeout(() => {
        setExpandedNodesData(prev => ({
          ...prev,
          [profileId]: { isLoading: false, error: error.message, nodes: [] }
        }));
        setExpandLoadingStage(null);
        setExpandingProfileId(null);
      }, 2000);
    }
  };

  // Add this helper function to highlight important terms in the text
  const highlightImportantTerms = (text) => {
    if (!text) return '';
    
    // Simply return the text without any highlighting
    return text;
  };

  return (
    <div className="draggable-canvas" ref={canvasRef}>
      <svg className="canvas-dots-bg" width={canvasSize.width} height={canvasSize.height} style={{position:'absolute',top:0,left:0,zIndex:1}}>
        {dots.map((dot, i) => (
          <circle key={i} cx={dot.x} cy={dot.y} r={DOT_RADIUS} fill={DOT_COLOR} />
        ))}
        
        {/* Draw connection lines */}
        {resultAvatars.map((result, index) => {
          const userAvatarCenterX = canvasSize.width / 2;
          const userAvatarCenterY = centerY - Y_OFFSET;
          const resultAvatarCenterX = result.position.x;
          const resultAvatarCenterY = result.position.y;

          return (
            <line
              key={`line-${index}`}
              x1={userAvatarCenterX}
              y1={userAvatarCenterY}
              x2={resultAvatarCenterX}
              y2={resultAvatarCenterY}
              stroke={CONNECTION_LINE_COLOR}
              strokeWidth={CONNECTION_LINE_WIDTH}
              strokeDasharray="4,4"
            />
          );
        })}

        {/* Orbiting avatars as SVG images */}
        {resultAvatars.map((result, i) => (
          <g key={`network-avatar-${i}`} transform={`translate(${result.position.x}, ${result.position.y})`}>
            <image
              href={result.profile.avatar}
              x={-AVATAR_SIZE / 2}
              y={-AVATAR_SIZE / 2}
              width={AVATAR_SIZE}
              height={AVATAR_SIZE}
              style={{
                filter: 'drop-shadow(0 0 10px rgba(0, 122, 255, 0.3))'
              }}
            />
            {/* Name below avatar */}
            <text
              x={0}
              y={AVATAR_SIZE / 2 + 24}
              textAnchor="middle"
              fontSize="16"
              fill="#007aff"
              style={{
                fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", sans-serif',
                fontWeight: 500,
                letterSpacing: 0.2,
                pointerEvents: 'none',
                userSelect: 'none',
                textShadow: '0 1px 4px #fff'
              }}
            >
              {result.profile.name}
            </text>
            <circle
              cx={0}
              cy={0}
              r={AVATAR_SIZE / 2}
              fill="transparent"
              style={{ cursor: 'pointer', pointerEvents: 'all' }}
              onClick={() => {
                setShowProfileInfo(true);
                setSelectedProfile(result);
                setShowUserProfileInfo(false);
              }}
            />
          </g>
        ))}

        {/* Render Expanded Nodes and their Connections */}
        {(() => {
          console.log('[DraggableAvatarCanvas] Current expandedNodesData before mapping:', JSON.stringify(expandedNodesData, null, 2)); // DEBUG
          if (Object.keys(expandedNodesData).length === 0) return null; // Don't render if empty

          return Object.entries(expandedNodesData).map(([parentId, data]) => {
            console.log(`[DraggableAvatarCanvas] Processing parentId: ${parentId}`, data); // DEBUG
            if (!data || !data.nodes || data.nodes.length === 0) {
                console.log(`[DraggableAvatarCanvas] No nodes to render for parentId: ${parentId}`); // DEBUG
                return null;
            }
            const parentProfile = resultAvatars.find(p => (p.profile.profile_url || p.profile.name) === parentId);
            if (!parentProfile) {
                console.log(`[DraggableAvatarCanvas] Parent profile not found for parentId: ${parentId}`); // DEBUG
                return null;
            }
            const parentPosition = parentProfile.position;
            const parentRadius = AVATAR_SIZE / 2;
            const mainGraphCenterX = canvasSize.width / 2;
            const mainGraphCenterY = centerY - Y_OFFSET;
            const SPREAD_ANGLE_RADIANS = Math.PI / 2; // 90-degree spread

            return data.nodes.map((node, index) => {
              console.log('[DraggableAvatarCanvas] Rendering expanded SVG node:', node.id, 'Emoji:', node.emoji); // DEBUG
              const directionX = parentPosition.x - mainGraphCenterX;
              const directionY = parentPosition.y - mainGraphCenterY;
              const baseAngle = Math.atan2(directionY, directionX);
              let placementAngle;
              if (data.nodes.length === 1) {
                placementAngle = baseAngle;
              } else {
                placementAngle = baseAngle - (SPREAD_ANGLE_RADIANS / 2) + (index / (data.nodes.length - 1)) * SPREAD_ANGLE_RADIANS;
              }
              const distance = EXPANDED_NODE_ORBIT_RADIUS + parentRadius;
              const childX = parentPosition.x + distance * Math.cos(placementAngle);
              const childY = parentPosition.y + distance * Math.sin(placementAngle);
              node.position = { x: childX, y: childY };

              return (
                <React.Fragment key={`expanded-node-group-${node.id}`}>
                  <line
                    key={`expanded-line-${node.id}`}
                    x1={parentPosition.x}
                    y1={parentPosition.y}
                    x2={childX}
                    y2={childY}
                    stroke={EXPANDED_CONNECTION_LINE_COLOR}
                    strokeWidth={EXPANDED_CONNECTION_LINE_WIDTH}
                    strokeDasharray="3,3"
                  />
                  <g 
                    transform={`translate(${childX}, ${childY})`}
                  >
                    <circle
                      cx="0"
                      cy="0"
                      r={EXPANDED_NODE_AVATAR_SIZE / 2}
                      fill="#fff"
                      stroke="#007aff"
                      strokeWidth="2"
                      onClick={() => {
                        console.log('[DraggableAvatarCanvas] Emoji circle clicked:', node); // DEBUG
                        setSelectedExpandedNodeInfo(node);
                        setShowExpandedNodeDetailModal(true);
                      }}
                      style={{
                        cursor: 'pointer',
                        pointerEvents: 'all',
                        filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))'
                      }}
                    />
                    <text
                      x="0"
                      y="0"
                      textAnchor="middle"
                      dominantBaseline="central"
                      fontSize={EXPANDED_NODE_AVATAR_SIZE * 0.55}
                      fontFamily="-apple-system, BlinkMacSystemFont, 'Segoe UI Emoji', 'Noto Color Emoji', 'Twemoji Mozilla', 'Apple Color Emoji', 'Segoe UI Symbol'"
                      style={{ pointerEvents: 'none' }}
                    >
                      {node.emoji || '❓'}
                    </text>
                  </g>
                </React.Fragment>
              );
            });
          });
        })()}
      </svg>
      
      {/* User's avatar */}
      <img
        src={userAvatar}
        alt="avatar"
        className={`draggable-avatar${avatarLifted ? ' lifted' : ''}`}
        style={{ 
          left: canvasSize.width / 2 - AVATAR_SIZE / 2, 
          top: centerY - AVATAR_SIZE / 2, 
          transition: avatarLifted ? 'top 0.5s cubic-bezier(.4,1.6,.4,1)' : 'top 0.4s' 
        }}
        onClick={handleAvatarClick}
        draggable={false}
      />
      
      {/* Add loading stage indicator */}
      {expandLoadingStage && (
        <div style={{
          position: 'absolute',
          top: '20px',
          left: '50%',
          transform: 'translateX(-50%)',
          backgroundColor: 'rgba(0, 122, 255, 0.9)',
          color: 'white',
          padding: '10px 20px',
          borderRadius: '20px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1000,
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
          fontWeight: 500,
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <div style={{
            width: '20px',
            height: '20px',
            borderRadius: '50%',
            borderTop: '3px solid white',
            borderRight: '3px solid transparent',
            borderBottom: '3px solid white',
            borderLeft: '3px solid transparent',
            animation: 'spin 1s linear infinite'
          }}></div>
          <style>{`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}</style>
          {expandLoadingStage}
        </div>
      )}
      
      {/* Profile info modal for user or selected profile */}
      {showProfileInfo && (
        <div className="profile-info-modal" onClick={() => { setShowProfileInfo(false); setShowUserProfileInfo(false); }}>
          <div className="profile-info-content" onClick={e => e.stopPropagation()}>
            <button 
              className="close-profile-button"
              onClick={() => { setShowProfileInfo(false); setShowUserProfileInfo(false); }}
            >
              ×
            </button>
            {/* If user avatar was clicked, show user info; else show selected profile info */}
            {showUserProfileInfo ? (
              <div className="profile-header">
                <img 
                  src={userAvatar} 
                  alt="profile" 
                  className="profile-avatar"
                />
                <div className="profile-basic-info">
                  <h3>{name || (profileData && profileData.name) || 'You'}</h3>
                  <p className="profile-headline">{(profileData && profileData.headline) || ''}</p>
                </div>
              </div>
            ) : (
              selectedProfile && (
                <div className="profile-header">
                  <img 
                    src={selectedProfile.profile.avatar || 'default-avatar.png'} 
                    alt="profile" 
                    className="profile-avatar"
                  />
                  <div className="profile-basic-info">
                    <h3>{selectedProfile.profile.name}</h3>
                    <p className="profile-headline">{selectedProfile.profile.headline}</p>
                    {/* Container for platform icon and expand button */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '8px' }}>
                      {/* Platform icon and link */}
                      {selectedProfile.profile.profile_url && selectedProfile.profile.platform && (() => {
                        const platform = getPlatformLogo(selectedProfile.profile.platform);
                        return platform ? (
                          <a
                            href={selectedProfile.profile.profile_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ display: 'inline-block', marginRight: 8 }} 
                          >
                            <img
                              src={platform.logo}
                              alt={platform.alt}
                              style={{ width: 28, height: 28, verticalAlign: 'middle', borderRadius: 4, boxShadow: '0 1px 4px rgba(0,0,0,0.08)' }}
                            />
                          </a>
                        ) : (
                           <div style={{ width: 28, height: 28, marginRight: 8 }}></div> // Placeholder for spacing if no icon
                        );
                      })()}
                      
                      {/* Expand button */}
                      {selectedProfile.profile.profile_url && selectedProfile.profile.platform && (
                        <button
                          onClick={() => handleExpandClick(selectedProfile)} // Updated onClick
                          style={{
                            background: 'none',
                            border: '1px solid #007aff',
                            color: '#007aff',
                            padding: '4px 10px',
                            borderRadius: '16px',
                            cursor: 'pointer',
                            fontSize: '14px',
                            fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Text", sans-serif',
                            fontWeight: 500,
                            letterSpacing: '0.1px',
                            // Removed marginLeft, verticalAlign, and marginTop as flexbox handles alignment
                            transition: 'background-color 0.2s ease, color 0.2s ease'
                          }}
                          onMouseOver={(e) => {
                            e.currentTarget.style.backgroundColor = '#007aff';
                            e.currentTarget.style.color = '#fff';
                          }}
                          onMouseOut={(e) => {
                            e.currentTarget.style.backgroundColor = 'transparent';
                            e.currentTarget.style.color = '#007aff';
                          }}
                        >
                          Expand
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              )
            )}
            {/* Analysis section for selected profile only */}
            {!showUserProfileInfo && selectedProfile && selectedProfile.analysis && (
              <div className="analysis-section">
                <h4>Analysis</h4>
                {selectedProfile.analysis.match_reasons && selectedProfile.analysis.match_reasons.length > 0 && (
                  <div className="analysis-subsection">
                    <h5>🎯 Match Reasons</h5>
                    <ul>
                      {selectedProfile.analysis.match_reasons.map((reason, idx) => (
                        <li key={idx}>{reason}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedProfile.analysis.commonalities && selectedProfile.analysis.commonalities.length > 0 && (
                  <div className="analysis-subsection">
                    <h5>🤝 Commonalities</h5>
                    <ul>
                      {selectedProfile.analysis.commonalities.map((common, idx) => (
                        <li key={idx}>{common}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedProfile.analysis.value_propositions && selectedProfile.analysis.value_propositions.length > 0 && (
                  <div className="analysis-subsection">
                    <h5>💡 Value Propositions</h5>
                    <ul>
                      {selectedProfile.analysis.value_propositions.map((value, idx) => (
                        <li key={idx}>{value}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {selectedProfile.analysis.opening_message && (
                  <div className="analysis-subsection">
                    {/* Create a new flex container for title and buttons */}
                    <div className="subsection-header">
                      <h5>✉️ Suggested Opening Message</h5>
                      <div className="message-actions-container">
                        <div className="message-actions">
                          <button 
                            className="edit-message-btn" 
                            onClick={() => handleEditClick(selectedProfile.analysis.opening_message)}
                            title="Edit message"
                          >
                            Edit
                          </button>
                          <button 
                            className="copy-message-btn" 
                            onClick={(event) => {
                              navigator.clipboard.writeText(selectedProfile.analysis.opening_message);
                              const btn = event.target;
                              const originalText = btn.textContent;
                              btn.textContent = 'Copied!';
                              setTimeout(() => {
                                btn.textContent = originalText;
                              }, 2000);
                            }}
                            title="Copy to clipboard"
                          >
                            Copy
                          </button>
                        </div>
                      </div>
                    </div>
                    
                    <div className="opening-message-container">
                      <p 
                        className="opening-message" 
                        dangerouslySetInnerHTML={{ __html: highlightImportantTerms(selectedProfile.analysis.opening_message) }}
                      ></p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Expanded Node Detail Modal */}
      {showExpandedNodeDetailModal && selectedExpandedNodeInfo && (
        <div 
          className="expanded-node-detail-modal-overlay" 
          onClick={() => setShowExpandedNodeDetailModal(false)}
        >
          <div 
            className="expanded-node-detail-modal-content" 
            onClick={e => e.stopPropagation()}
          >
            <button 
              className="expanded-node-detail-close-btn"
              onClick={() => setShowExpandedNodeDetailModal(false)}
            >
              &times;
            </button>
            
            {/* Category/Source Type as a heading */}
            {selectedExpandedNodeInfo.source && !selectedExpandedNodeInfo.source.startsWith('http') && (
              <h4 className="node-category-heading">{selectedExpandedNodeInfo.source}</h4>
            )}
            
            <div className="expanded-node-emoji-display">{selectedExpandedNodeInfo.emoji}</div>
            
            {/* Details Section */}
            <div className="info-section">
              <h5 className="info-section-title details-title">Details</h5>
              {(() => {
                const detailsText = selectedExpandedNodeInfo.text;
                // Attempt to parse structured details if source is Achievement or Timeline
                if (['Achievement', 'Timeline'].includes(selectedExpandedNodeInfo.source)) {
                  const parts = {};
                  const roleMatch = detailsText.match(/Role:(.*?)(Period:|Description:|Impact:|$)/is);
                  const periodMatch = detailsText.match(/Period:(.*?)(Role:|Description:|Impact:|$)/is);
                  const descriptionMatch = detailsText.match(/Description:(.*?)(Role:|Period:|Impact:|$)/is);
                  const impactMatch = detailsText.match(/Impact:(.*?)(Role:|Period:|Description:|$)/is);

                  if (roleMatch && roleMatch[1]) parts.Role = roleMatch[1].trim();
                  if (periodMatch && periodMatch[1]) parts.Period = periodMatch[1].trim();
                  if (descriptionMatch && descriptionMatch[1]) parts.Description = descriptionMatch[1].trim();
                  if (impactMatch && impactMatch[1]) parts.Impact = impactMatch[1].trim();

                  if (Object.keys(parts).length > 0) {
                    return (
                      <dl className="structured-details-list">
                        {parts.Role && (
                          <>
                            <dt>Role</dt>
                            <dd dangerouslySetInnerHTML={{ __html: highlightImportantTerms(parts.Role) }}></dd>
                          </>
                        )}
                        {parts.Period && (
                          <>
                            <dt>Period</dt>
                            <dd dangerouslySetInnerHTML={{ __html: highlightImportantTerms(parts.Period) }}></dd>
                          </>
                        )}
                        {parts.Description && (
                          <>
                            <dt>Description</dt>
                            <dd dangerouslySetInnerHTML={{ __html: highlightImportantTerms(parts.Description) }}></dd>
                          </>
                        )}
                        {parts.Impact && (
                          <>
                            <dt>Impact</dt>
                            <dd dangerouslySetInnerHTML={{ __html: highlightImportantTerms(parts.Impact) }}></dd>
                          </>
                        )}
                      </dl>
                    );
                  }
                }
                // Fallback for non-structured text or if parsing fails
                return (
                  <ul className="bullet-point-list">
                    {detailsText.split(/\. |\.\n/).filter(point => point.trim().length > 0).map((point, index) => (
                      <li key={index} className="info-section-text">
                        {point.trim().endsWith('.') ? point.trim() : `${point.trim()}.`}
                      </li>
                    ))}
                  </ul>
                );
              })()}
            </div>

            {/* Extract URLs from text and display them as sources */}
            {(() => {
              if (!selectedExpandedNodeInfo || !selectedExpandedNodeInfo.text) return null;
              
              // Regular expression to find URLs in text
              const urlRegex = /(https?:\/\/[^\s]+)/g;
              const matches = selectedExpandedNodeInfo.text.match(urlRegex);
              
              if (matches && matches.length > 0) {
                return (
                  <div className="info-section">
                    <h5 className="info-section-title source-title">Sources</h5>
                    <ul className="source-links-list">
                      {matches.map((url, index) => (
                        <li key={index}>
                          <a href={url} target="_blank" rel="noopener noreferrer" className="source-link">
                            {url}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              }
              
              // If there's a source that looks like a URL but doesn't start with http/https, display it anyway
              if (selectedExpandedNodeInfo.source && selectedExpandedNodeInfo.source.includes('.com')) {
                return (
                  <div className="info-section">
                    <h5 className="info-section-title source-title">Source</h5>
                    <p className="info-section-text source-text">
                      {selectedExpandedNodeInfo.source}
                    </p>
                  </div>
                );
              }
              
              return null;
            })()}
          </div>
        </div>
      )}

      {/* Use the new ChatEdit component */}
      <ChatEdit 
        show={showEditDialog}
        initialMessage={messageToEdit}
        onClose={handleCloseEditDialog}
        onSave={handleSaveEditMessage}
      />

      {showLoadingScreen && (
        <div className="loading-screen">
          <div className="loading-content">
            <svg 
              className="loading-animation" 
              width={300} 
              height={300} 
              style={{
                position: 'relative',
                margin: '0 auto',
                transform: `scale(${loadingAnimationState.scale})`,
                transition: 'transform 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)'
              }}
            >
              <defs>
                <filter id="glow">
                  <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                  <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                  </feMerge>
                </filter>
              </defs>

              {/* Center point with glow effect */}
              <circle
                cx="150"
                cy="150"
                r={LOADING_ANIMATION_CONFIG.avatarSize / 2}
                fill="#007aff"
                opacity="0.8"
                filter="url(#glow)"
              />

              {/* Orbiting avatars with rotation and scaling */}
              {Array.from({ length: LOADING_ANIMATION_CONFIG.numAvatars }).map((_, i) => {
                const angle = (i * 2 * Math.PI) / LOADING_ANIMATION_CONFIG.numAvatars + loadingAnimationState.rotation;
                const x = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.cos(angle);
                const y = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.sin(angle);
                const scale = loadingAnimationState.avatarScales[i];
                const avatarImage = loadingAnimationState.selectedAvatars[i];
                
                return (
                  <g 
                    key={`loading-avatar-${i}`}
                    transform={`translate(${x}, ${y}) scale(${scale})`}
                  >
                    <image
                      href={avatarImage}
                      x={-LOADING_ANIMATION_CONFIG.avatarSize / 2}
                      y={-LOADING_ANIMATION_CONFIG.avatarSize / 2}
                      width={LOADING_ANIMATION_CONFIG.avatarSize}
                      height={LOADING_ANIMATION_CONFIG.avatarSize}
                      style={{
                        filter: 'drop-shadow(0 0 8px rgba(0, 122, 255, 0.5))'
                      }}
                    />
                  </g>
                );
              })}

              {/* Connection lines */}
              {loadingAnimationState.connections.map((conn, idx) => {
                const fromAngle = (conn.from * 2 * Math.PI) / LOADING_ANIMATION_CONFIG.numAvatars + loadingAnimationState.rotation;
                const toAngle = (conn.to * 2 * Math.PI) / LOADING_ANIMATION_CONFIG.numAvatars + loadingAnimationState.rotation;
                
                const fromX = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.cos(fromAngle);
                const fromY = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.sin(fromAngle);
                const toX = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.cos(toAngle);
                const toY = 150 + LOADING_ANIMATION_CONFIG.orbitRadius * Math.sin(toAngle);
                
                const currentX = fromX + (toX - fromX) * conn.progress;
                const currentY = fromY + (toY - fromY) * conn.progress;
                
                return (
                  <line
                    key={`connection-${idx}`}
                    x1={fromX}
                    y1={fromY}
                    x2={currentX}
                    y2={currentY}
                    stroke={LOADING_ANIMATION_CONFIG.connectionColor}
                    strokeWidth={LOADING_ANIMATION_CONFIG.connectionWidth}
                    strokeDasharray="4,4"
                    style={{
                      transition: 'all 0.3s cubic-bezier(0.2, 0.8, 0.2, 1)'
                    }}
                  />
                );
              })}

              {/* Pulsing circle with glow */}
              {loadingAnimationState.phase === 2 && (
                <circle
                  cx="150"
                  cy="150"
                  r={loadingAnimationState.pulseRadius}
                  fill="none"
                  stroke="#007aff"
                  strokeWidth="1.5"
                  opacity={loadingAnimationState.pulseOpacity}
                  filter="url(#glow)"
                />
              )}
            </svg>

            <h2>Building Your Network</h2>
            <p className="loading-message">{LOADING_MESSAGES[loadingMessageIndex]}</p>
            <div className="loading-progress">
              <div 
                className="progress-bar" 
                style={{ width: `${loadingProgress}%` }}
              ></div>
            </div>
          </div>
        </div>
      )}

      {showChat && !showLoadingScreen && showChatBox && (
        <div className="agent-chat-box">
          <div 
            style={{
              padding: '16px 20px',
              borderBottom: '1px solid rgba(0,0,0,0.05)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              position: 'relative'
            }}
          >
            <img 
              src={userAvatar} 
              alt="avatar" 
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                marginRight: '10px'
              }}
            />
            <h3 style={{ 
              margin: 0, 
              fontSize: '16px', 
              fontWeight: '600', 
              color: '#1d1d1f'
            }}>
              {name || 'Your Agent'}
            </h3>
            <button
              className="close-chatbox-btn"
              style={{
                position: 'absolute', 
                top: 10, 
                right: 10, 
                background: 'rgba(0,0,0,0.05)', 
                border: 'none',
                width: '28px',
                height: '28px',
                borderRadius: '14px',
                fontSize: 18, 
                cursor: 'pointer', 
                color: '#6e6e73',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 20
              }}
              onClick={() => setShowChatBox(false)}
              aria-label="Close chat"
            >
              ×
            </button>
          </div>
          <div className="agent-chat-messages">
            {chat.map((msg, idx) => (
              <div key={idx} className={`agent-chat-msg ${msg.from}`}>
                {Array.isArray(msg.text) ? (
                  msg.text.map((part, partIdx) => {
                    if (typeof part === 'string') {
                      return part.split('\n').map((item, key, arr) => (
                        <React.Fragment key={`${idx}-part-${partIdx}-str-${key}`}>
                          {item}
                          {key < arr.length - 1 && <br />}
                        </React.Fragment>
                      ));
                    } else if (part.type === 'image' && part.src) {
                      return (
                        <img
                          key={`${idx}-part-${partIdx}-img`}
                          src={part.src}
                          alt={part.alt}
                          style={{ 
                            width: '16px', 
                            height: '16px', 
                            verticalAlign: 'middle', 
                            marginLeft: '4px', 
                            marginRight: '2px',
                            objectFit: 'contain',
                            borderRadius: '4px',
                            display: 'inline-block'
                          }}
                        />
                      );
                    }
                    return null;
                  })
                ) : typeof msg.text === 'string' ? (
                  msg.text.split('\n').map((item, key, arr) => (
                    <React.Fragment key={`${idx}-str-${key}`}>
                      {item}
                      {key < arr.length - 1 && <br />}
                    </React.Fragment>
                  ))
                ) : (
                  msg.text 
                )}
              </div>
            ))}
            {isLoading && (
              <div className="agent-chat-msg agent loading">
                <div className="loading-dots">
                  <span>.</span>
                  <span>.</span>
                  <span>.</span>
                </div>
                {statusMessage}
              </div>
            )}
            {serverStatus !== 'healthy' && (
              <div className="agent-chat-msg agent warning">
                Server status: {serverStatus === 'unavailable' ? 'Not running' : 'Unhealthy'}
              </div>
            )}
          </div>
          <div className="input-container" style={{
            backgroundColor: '#f5f5f7',
            padding: '10px 0'
          }}>
            <form className="agent-chat-input-row" onSubmit={handleSend}>
              <input
                className="agent-chat-input"
                type="text"
                value={input}
                onChange={handleInputChange}
                placeholder={isLoading ? "Processing..." : "Type your request here..."}
                disabled={isLoading || serverStatus !== 'healthy'}
                autoFocus
                style={{ paddingLeft: '4px', textAlign: 'left' }}
              />
              <button 
                className="agent-chat-send" 
                type="submit"
                disabled={isLoading || serverStatus !== 'healthy'}
              >
                {isLoading ? "..." : "Send"}
              </button>
            </form>
          </div>
        </div>
      )}

      {!showChatBox && (
        <button
          className="reopen-chatbox-btn"
          onClick={() => setShowChatBox(true)}
          aria-label="Open chat"
        >
          💬
        </button>
      )}
    </div>
  );
};

export default DraggableAvatarCanvas; 