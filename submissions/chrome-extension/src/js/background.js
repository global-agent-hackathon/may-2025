// Default configuration
const DEFAULT_CONFIG = {
  serverUrl: 'http://localhost:3000',
  wsUrl: 'ws://localhost:3000/ws',
  categories: {
    hatred: true,
    misinformation: true,
    violence: true,
    fraud: false,
    educational: true,
    relevance: true,
    integrity: true,
    clarity: true
  },
  customPrompts: [],
  scoreThresholds: {
    hide: 3,   // Hide videos with score less than 3
    warning: 5 // Show warning on videos with score less than 5
  },
  autoActions: {
    hideVideos: true,
    showWarnings: true,
    useNotInterested: true
  },
  logActions: true
};

// Initialization
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.get(['config'], (result) => {
    if (!result.config) {
      chrome.storage.local.set({ config: DEFAULT_CONFIG });
      console.log('Initial configuration established');
    }
  });
  
  chrome.storage.local.set({ actionLog: [] });
  chrome.storage.local.set({ notInterestedVideos: [] });
  chrome.storage.local.set({ warningVideos: [] });
});

// Messaging
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'getConfig') {
    chrome.storage.local.get(['config'], (result) => {
      sendResponse(result.config || DEFAULT_CONFIG);
    });
    return true; // Indicates that the response is asynchronous
  }
  
  if (message.type === 'saveConfig') {
    chrome.storage.local.set({ config: message.config }, () => {
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (message.type === 'logAction') {
    logAction(message.action);
    sendResponse({ success: true });
    return true;
  }
  
  if (message.type === 'getActionLog') {
    chrome.storage.local.get(['actionLog'], (result) => {
      sendResponse(result.actionLog || []);
    });
    return true;
  }
  
  if (message.type === 'checkNotInterested') {
    chrome.storage.local.get(['notInterestedVideos'], (result) => {
      const videos = result.notInterestedVideos || [];
      sendResponse({ 
        isMarked: videos.includes(message.videoId),
        videoId: message.videoId
      });
    });
    return true;
  }
  
  if (message.type === 'addNotInterested') {
    chrome.storage.local.get(['notInterestedVideos'], (result) => {
      const videos = result.notInterestedVideos || [];
      if (!videos.includes(message.videoId)) {
        videos.push(message.videoId);
        chrome.storage.local.set({ notInterestedVideos: videos });
      }
      sendResponse({ success: true });
    });
    return true;
  }
  
  if (message.type === 'checkWarning') {
    chrome.storage.local.get(['warningVideos'], (result) => {
      const videos = result.warningVideos || [];
      sendResponse({ 
        isMarked: videos.includes(message.videoId),
        videoId: message.videoId
      });
    });
    return true;
  }
  
  if (message.type === 'addWarning') {
    chrome.storage.local.get(['warningVideos'], (result) => {
      const videos = result.warningVideos || [];
      if (!videos.includes(message.videoId)) {
        videos.push(message.videoId);
        chrome.storage.local.set({ warningVideos: videos });
      }
      sendResponse({ success: true });
    });
    return true;
  }
});

// Records actions performed by the extension
function logAction(action) {
  chrome.storage.local.get(['config', 'actionLog'], (result) => {
    if (!result.config?.logActions) return;
    
    const actionLog = result.actionLog || [];
    actionLog.unshift({
      ...action,
      timestamp: new Date().toISOString()
    });
    
    // Limit the log size to 100 entries
    if (actionLog.length > 100) {
      actionLog.pop();
    }
    
    chrome.storage.local.set({ actionLog });
  });
}
