// TubeWarden - Content Script
// This script runs on YouTube pages to analyze displayed videos

// Global state
let config = null;
let wsConnection = null;
let videoScores = {}; // { videoId: { score: number, categories: {} } }
let videoElements = {}; // { videoId: HTMLElement }
let processedVideos = new Set(); // Set of IDs that have been processed
let processingQueue = new Set(); // Set of IDs in evaluation process
let videoObserver = null; // Observer to detect new videos
let retryTimeout = null; // Timeout to retry WebSocket connection

// Initialization
(async function init() {
  // Load configuration
  config = await getConfig();
  
  // Connect WebSocket
  connectWebSocket();
  
  // Setup observers
  setupVideoObserver();
  
  // Setup listeners for SPA navigation
  setupNavigationListeners();
  
  // First video detection
  detectVideos();
  
  console.log('TubeWarden started');
})();

// Get configuration from background script
async function getConfig() {
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type: 'getConfig' }, config => {
      resolve(config);
    });
  });
}

// Connect to WebSocket server
function connectWebSocket() {
  if (wsConnection) {
    wsConnection.close();
  }
  
  try {
    wsConnection = new WebSocket(config.wsUrl);
    
    wsConnection.onopen = () => {
      console.log('Connected to WebSocket server');
      clearTimeout(retryTimeout);
      
      // Request evaluation of already detected videos
      Object.keys(videoElements).forEach(videoId => {
        if (!videoScores[videoId] && !processingQueue.has(videoId)) {
          requestVideoEvaluation(videoId);
        }
      });
    };
    
    wsConnection.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        
        if (data.type === 'videoScore') {
          // We received a video evaluation
          processVideoScore(data.videoId, data.score, data.categories, data.content_summary, data.evaluation_summary);
        }
      } catch (error) {
        console.error('Error processing WebSocket message:', error);
      }
    };
    
    wsConnection.onerror = (error) => {
      console.error('Error in WebSocket connection:', error);
    };
    
    wsConnection.onclose = () => {
      console.log('WebSocket connection closed, retrying in 5 seconds');
      // Retry connection in 5 seconds
      clearTimeout(retryTimeout);
      retryTimeout = setTimeout(connectWebSocket, 5000);
    };
  } catch (error) {
    console.error('Error connecting WebSocket:', error);
    // Retry connection in 5 seconds
    clearTimeout(retryTimeout);
    retryTimeout = setTimeout(connectWebSocket, 5000);
  }
}

// Configure observer to detect new videos
function setupVideoObserver() {
  if (videoObserver) {
    videoObserver.disconnect();
  }
  
  videoObserver = new MutationObserver((mutations) => {
    // Check if there are relevant changes that indicate new videos
    let shouldDetect = false;
    
    for (const mutation of mutations) {
      if (mutation.type === 'childList' && 
          (mutation.addedNodes.length > 0 || mutation.removedNodes.length > 0)) {
        shouldDetect = true;
        break;
      }
    }
    
    if (shouldDetect) {
      // Debounce to avoid multiple detections in short time
      clearTimeout(window.agnoDetectTimeout);
      window.agnoDetectTimeout = setTimeout(detectVideos, 500);
    }
  });
  
  // Observe all main content of YouTube
  const contentArea = document.querySelector('#content');
  if (contentArea) {
    videoObserver.observe(contentArea, {
      childList: true,
      subtree: true
    });
  }
}

// Configure listeners to detect navigation changes in YouTube (SPA)
function setupNavigationListeners() {
  // Listen for changes in the URL
  let lastUrl = location.href;
  
  // Check URL changes periodically
  setInterval(() => {
    const currentUrl = location.href;
    if (currentUrl !== lastUrl) {
      lastUrl = currentUrl;
      console.log('Page change detected:', currentUrl);
      
      // Clear processed videos on page navigation to allow re-processing
      processedVideos.clear();
      
      // Give time for the page to load new content
      setTimeout(detectVideos, 1000);
    }
  }, 1000);
}

// Detect videos in the current page
function detectVideos() {
  // Selector for video thumbnails (works in main feed and subscriptions)
  const selectors = [
    'ytd-rich-item-renderer', // Main feed
    'ytd-grid-video-renderer', // Subscriptions page (grid view)
    'ytd-video-renderer',      // Search results
    'ytd-compact-video-renderer' // Playback sidebar
  ];
  
  const elements = document.querySelectorAll(selectors.join(','));
  console.log(`Detected ${elements.length} video elements`);
  
  // Track new videos found in this detection pass
  const newVideosFound = [];
  
  // Process only videos that aren't already in our tracking
  elements.forEach(element => {
    // Extract video ID first without processing
    const videoId = extractVideoId(element);
    
    // Skip if no valid ID
    if (!videoId) return;
    
    // Skip if already processed or in processing queue and the element is stored
    if ((processedVideos.has(videoId) || processingQueue.has(videoId)) && videoElements[videoId]) {
      return;
    }
    
    // Process the video element
    processVideoElement(element);
    newVideosFound.push(videoId);
  });
  
  if (newVideosFound.length > 0) {
    console.log(`Found ${newVideosFound.length} new videos to process`);
  }
}

// Extract video ID from element
function extractVideoId(element) {
  // Extract the video ID from the link
  let videoLink = element.querySelector('a#thumbnail');
  
  if (!videoLink) {
    // Try with other alternative selectors
    videoLink = element.querySelector('a.ytd-thumbnail');
  }
  
  if (!videoLink) {
    return null; // Could not find the video link
  }
  
  const href = videoLink.href;
  if (!href) return null;
  
  // Extract videoId from URL (common pattern: v=VIDEO_ID)
  const match = href.match(/[?&]v=([^&]+)/);
  if (!match) return null;
  
  return match[1];
}

// Process each video element
function processVideoElement(element) {
  const videoId = extractVideoId(element);
  if (!videoId) return;
  
  // Store reference to video element
  videoElements[videoId] = element;
  
  // If we already have the score, apply it
  if (videoScores[videoId]) {
    applyScoreToVideo(videoId, videoScores[videoId]);
    // Mark as processed since we already have the score
    processedVideos.add(videoId);
  } 
  // If in processing queue, show processing indicator
  else if (processingQueue.has(videoId)) {
    applyProcessingIndicator(videoId, element);
  }
  // If not in evaluation process, request it
  else if (wsConnection?.readyState === WebSocket.OPEN) {
    requestVideoEvaluation(videoId);
  }
}

// Apply processing indicator to video
function applyProcessingIndicator(videoId, element) {
  const videoElement = element || videoElements[videoId];
  if (!videoElement) return;
  
  // Remove any previous badge
  const existingBadgeWrapper = videoElement.querySelector('.agno-badge-wrapper');
  if (existingBadgeWrapper) {
    existingBadgeWrapper.remove();
  }
  
  // Create the floating container for the badge
  const badgeWrapper = document.createElement('div');
  badgeWrapper.className = 'agno-badge-wrapper';
  
  // Create the badge
  const processingBadge = document.createElement('div');
  processingBadge.className = 'agno-score-badge processing';
  
  // Badge content
  processingBadge.innerHTML = `
    <span class="agno-icon">⏳ TW</span>
  `;
  
  // Tooltip with explanation
  processingBadge.title = `Processing`;
  
  // Insert badge in the wrapper
  badgeWrapper.appendChild(processingBadge);
  
  // Insert wrapper in the thumbnail
  const thumbnailElement = 
    videoElement.querySelector('a#thumbnail') || videoElement.querySelector('a.ytd-thumbnail');
  
  if (thumbnailElement) {
    // Ensure relative container only if necessary
    const computed = window.getComputedStyle(thumbnailElement);
    if (computed.position === 'static') {
      thumbnailElement.style.position = 'relative';
    }
    
    thumbnailElement.appendChild(badgeWrapper);
  }
}

// Request video evaluation from server
function requestVideoEvaluation(videoId) {
  if (!videoId || processingQueue.has(videoId)) return;
  
  processingQueue.add(videoId);
  
  // Apply processing indicator right away
  if (videoElements[videoId]) {
    applyProcessingIndicator(videoId, videoElements[videoId]);
  }
  
  // Send REST request to server
  fetch(`${config.serverUrl}/api/videos/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      videoId,
      categories: getActiveCategories(),
      customPrompts: config.customPrompts
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Response error: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log(`Video evaluation ${videoId} sent to queue`);
    // The actual response will arrive via WebSocket
  })
  .catch(error => {
    console.error(`Error requesting evaluation for ${videoId}:`, error);
    // Remove from queue to allow future retries
    processingQueue.delete(videoId);
  });
}

// Get active categories according to configuration
function getActiveCategories() {
  const activeCategories = [];
  
  for (const [category, isActive] of Object.entries(config.categories)) {
    if (isActive) {
      activeCategories.push(category);
    }
  }
  
  return activeCategories;
}

// Process received score for a video
function processVideoScore(videoId, score, categories, content_summary, evaluation_summary) {
  // Save the score
  videoScores[videoId] = { score, categories, content_summary, evaluation_summary };
  
  // Remove from processing queue
  processingQueue.delete(videoId);
  
  // Mark as fully processed
  processedVideos.add(videoId);
  
  // If the video element is visible, apply the score
  if (videoElements[videoId]) {
    applyScoreToVideo(videoId, { score, categories, content_summary, evaluation_summary });
  }
  
  // Log the action
  logAction({
    type: 'videoScored',
    videoId,
    score,
    categories,
    content_summary,
    evaluation_summary
  });
}

// Apply score visually to the video
function applyScoreToVideo(videoId, scoreData) {
  const element = videoElements[videoId];
  if (!element) return;

  // Remove any previous badge
  const existingBadgeWrapper = element.querySelector('.agno-badge-wrapper');
  if (existingBadgeWrapper) {
    existingBadgeWrapper.remove();
  }

  const { score, categories, content_summary, evaluation_summary } = scoreData;

  // Create the floating container for the badge
  const badgeWrapper = document.createElement('div');
  badgeWrapper.className = 'agno-badge-wrapper';

  // Create the badge
  const scoreBadge = document.createElement('div');
  scoreBadge.className = 'agno-score-badge';

  // Determine color class
  let colorClass = 'neutral';
  if (score <= config.scoreThresholds.hide) {
    colorClass = 'bad';
  } else if (score <= config.scoreThresholds.warning) {
    colorClass = 'warning';
  } else {
    colorClass = 'good';
  }

  scoreBadge.classList.add(colorClass);

  // Badge content
  scoreBadge.innerHTML = `
    <span class="agno-score">${score.toFixed(1)}</span>
    ${getScoreIcon(score)}
  `;

  // Tooltip with details by category
  scoreBadge.title = `Score: ${score.toFixed(1)}\n${formatCategoryScores(categories)}`;

  // Insert badge in the wrapper
  badgeWrapper.appendChild(scoreBadge);

  // Insert wrapper in the thumbnail (without altering layout)
  const thumbnailElement =
    element.querySelector('a#thumbnail') || element.querySelector('a.ytd-thumbnail');

  if (thumbnailElement) {
    // Ensure relative container only if necessary
    const computed = window.getComputedStyle(thumbnailElement);
    if (computed.position === 'static') {
      thumbnailElement.style.position = 'relative';
    }

    thumbnailElement.appendChild(badgeWrapper);
  }

  if (content_summary || evaluation_summary) {
    const channelNameEl = element.querySelector('ytd-channel-name, .ytd-channel-name');

    if (channelNameEl && !channelNameEl.querySelector('.agno-summary-button')) {
      const summaryButton = document.createElement('button');
      summaryButton.textContent = 'Summary';
      summaryButton.className = 'agno-summary-button';
      summaryButton.onclick = (e) => {
        e.stopPropagation();
        e.preventDefault();
        showSummaryPopup(videoId, content_summary, evaluation_summary, summaryButton);
      };
      channelNameEl.appendChild(summaryButton);
    }
  }
  // Apply extra logic if necessary (hide, warning, etc.)
  applyAutoActions(videoId, element, score);
}

// Get icon according to score
function getScoreIcon(score) {
  if (score <= config.scoreThresholds.hide) {
    return '<span class="agno-icon">✘</span>';
  } else if (score <= config.scoreThresholds.warning) {
    return '<span class="agno-icon">⚠️</span>';
  } else {
    return '<span class="agno-icon">✓</span>';
  }
}

// Format category scores for tooltip
function formatCategoryScores(categories) {
  if (!categories) return '';
  
  return Object.entries(categories)
    .map(([key, value]) => `${formatCategoryName(key)}: ${value.toFixed(1)}`)
    .join('\n');
}

// Format category name for better readability
function formatCategoryName(name) {
  // Convert camelCase to readable format (e.g: intellectualHealth -> Intellectual Health)
  const formatted = name.replace(/([A-Z])/g, ' $1');
  return formatted.charAt(0).toUpperCase() + formatted.slice(1);
}

// Apply automatic actions according to score
function applyAutoActions(videoId, element, score) {
  // If automatic actions are disabled, exit
  if (!config.autoActions) return;
  
  // Hide videos with low score
  if (score <= config.scoreThresholds.hide) {

    if(config.autoActions.hideVideos) {
        // Add class to hide or cross out the video
        element.classList.add('agno-hidden-video');

        // Log action
        logAction({
          type: 'videoHidden',
          videoId,
          score
        });
    }
    if (config.autoActions.useNotInterested) {
       triggerNotInterestedAction(element, videoId);

       // Log action
        logAction({
          type: 'videoMarkedNotInterested',
          videoId,
          score
        });
    }
  }
  // Show warning on videos with medium score
  else if (config.autoActions.showWarnings && score <= config.scoreThresholds.warning) {
    // First check if this video already has a warning applied
    chrome.runtime.sendMessage({ type: 'checkWarning', videoId }, (response) => {
      if (response.isMarked) {
        console.log(`Video ${videoId} already has warning applied, skipping`);
        return;
      }
      
      // Apply warning only if not already applied
      element.classList.add('agno-warning-video');
      
      // Save this video as warned
      chrome.runtime.sendMessage({ type: 'addWarning', videoId });
      
      // Log action
      logAction({
        type: 'videoWarningApplied',
        videoId,
        score
      });
    });
  }
  
  // Mark as processed since we've applied actions
  processedVideos.add(videoId);
}

// Attempt to use YouTube's "Not interested" functionality
function triggerNotInterestedAction(element, videoId) {
  // First check if this video was already marked as not interested
  chrome.runtime.sendMessage({ type: 'checkNotInterested', videoId }, (response) => {
    if (response.isMarked) {
      console.log(`Video ${videoId} was already marked as "Not interested", skipping`);
      return;
    }
    
    // Continue only if not already marked
    // Try to find the video options menu
    const menuButton = element.querySelector('button.yt-icon-button[aria-label="Menú de acciones"], button.yt-icon-button[aria-label="Action menu"]');
  
    if (menuButton) {
      try {
        // Avoid infinite loop
        if (videoObserver) videoObserver.disconnect();
  
        // Click the menu button
        menuButton.click();
        
        // Wait for the menu to appear and look for the "Not interested" option
        setTimeout(() => {
          const notInterestedButton = Array.from(document.querySelectorAll('tp-yt-paper-item')).find(
            item => item.textContent.includes('Not interested') || item.textContent.includes('No me interesa')
          );
          
          if (notInterestedButton) {
            notInterestedButton.click();
            console.log(`Marked "Not interested" for video ${videoId}`);
            
            // Save this video as marked
            chrome.runtime.sendMessage({ type: 'addNotInterested', videoId });
            
            // Log action
            logAction({
              type: 'videoMarkedNotInterested',
              videoId
            });
          }
  
          // Run observer again after YouTube process
          setTimeout(() => {
            setupVideoObserver();
          }, 1000);
  
        }, 500);
      } catch (error) {
        console.error('Error trying to mark "Not interested":', error);
        setTimeout(() => {
          setupVideoObserver();
        }, 1000);
      }
    }
  });
}

// Log an action
function logAction(action) {
  chrome.runtime.sendMessage({
    type: 'logAction',
    action
  });
}

function showSummaryPopup(videoId, summaryTextFromWS, evaluationSummaryFromWS, anchorEl) {
  const scoreData = videoScores[videoId];
  if (!scoreData) return;

  // Permissive: use default text if summary is missing
  const summaryText = summaryTextFromWS || 'Summary not available';
  const evaluationSummary = evaluationSummaryFromWS || 'Evaluation summary not available';
  const categories = scoreData.categories || {};

  // Remove previous popup
  const existing = document.querySelector('.agno-summary-popup');
  if (existing) existing.remove();

  const popup = document.createElement('div');
  popup.className = 'agno-summary-popup';
  popup.innerHTML = `
    <div class="agno-summary-title">- Summary</div>
    <div class="agno-summary-text">${sanitizeHTML(summaryText)}</div>
    <div class="agno-summary-title">- Evaluation Summary</div>
    <div class="agno-summary-text">${sanitizeHTML(evaluationSummary)}</div>
    <div class="agno-summary-title">- Categories</div>

    <ul class="agno-category-list">
      ${Object.entries(categories)
        .map(([cat, val]) => `
          <li>
            <span class="agno-category-indicator ${getCategoryColorClass(val)}"></span>
            <span class="agno-category-label">${formatCategoryName(cat)}</span>
          </li>
        `)
        .join('')}
    </ul>
  `;


  // Position near the button
  const rect = anchorEl.getBoundingClientRect();
  popup.style.position = 'fixed';
  popup.style.top = `${rect.bottom + 5}px`;
  popup.style.left = `${rect.left}px`;
  
  // Add listener to maintain position when scrolling
  const updatePosition = () => {
    const newRect = anchorEl.getBoundingClientRect();
    popup.style.top = `${newRect.bottom + 5}px`;
    popup.style.left = `${newRect.left}px`;
  };
  
  window.addEventListener('scroll', updatePosition);

  document.body.appendChild(popup);

  // Close if clicked outside
  const closePopup = (e) => {
    if (!popup.contains(e.target)) {
      popup.remove();
      document.removeEventListener('click', closePopup);
      window.removeEventListener('scroll', updatePosition);
    }
  };
  setTimeout(() => {
    document.addEventListener('click', closePopup);
  }, 0);
}

function getCategoryColorClass(score) {
  if (score < 5) return 'red';
  if (score < 8) return 'orange';
  return 'green';
}

function sanitizeHTML(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}


// Reload configuration when it changes
chrome.runtime.onMessage.addListener((message) => {
  if (message.type === 'configUpdated') {
    getConfig().then(newConfig => {
      config = newConfig;
      console.log('Configuration updated');
      
      // Reapply all scores with the new configuration
      Object.keys(videoScores).forEach(videoId => {
        if (videoElements[videoId]) {
          applyScoreToVideo(videoId, videoScores[videoId]);
        }
      });
    });
  }
});