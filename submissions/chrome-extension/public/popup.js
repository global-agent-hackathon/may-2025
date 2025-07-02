// Popup script for TubeWarden

// References to UI elements
const tabs = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const saveConfigBtn = document.getElementById('save-config');
const resetConfigBtn = document.getElementById('reset-config');
const clearLogBtn = document.getElementById('clear-log');
const enableLoggingCheckbox = document.getElementById('enable-logging');
const logEntriesContainer = document.querySelector('.log-entries');
const connectionStatus = document.getElementById('connection-status');

// Config form fields
const serverUrlInput = document.getElementById('serverUrl');
const wsUrlInput = document.getElementById('wsUrl');
const categoryCheckboxes = document.querySelectorAll('.category-item input[type="checkbox"]');
const thresholdHideInput = document.getElementById('threshold-hide');
const thresholdWarningInput = document.getElementById('threshold-warning');
const actionHideCheckbox = document.getElementById('action-hide');
const actionWarningCheckbox = document.getElementById('action-warning');
const actionNotInterestedCheckbox = document.getElementById('action-notinterested');
const customPromptsTextarea = document.getElementById('custom-prompts');

// Current configuration
let currentConfig = null;

// WebSocket connection state (simulated in the popup)
let wsConnectionInterval = null;

// Initialization
document.addEventListener('DOMContentLoaded', async () => {
  // Load configuration
  await loadConfig();
  
  // Set up tabs
  setupTabs();
  
  // Load action log
  loadActionLog();
  
  // Check connection status
  checkConnectionStatus();
  
  // Set up event listeners
  setupEventListeners();
});

// Load configuration from background script
async function loadConfig() {
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type: 'getConfig' }, config => {
      currentConfig = config;
      updateFormWithConfig(config);
      resolve(config);
    });
  });
}

// Update form with loaded configuration
function updateFormWithConfig(config) {
  // URLs
  serverUrlInput.value = config.serverUrl || 'http://localhost:3000/v1/api';
  wsUrlInput.value = config.wsUrl || 'ws://localhost:3000/ws';
  
  // Categories
  if (config.categories) {
    for (const [category, isEnabled] of Object.entries(config.categories)) {
      const checkbox = document.getElementById(`cat-${category}`);
      if (checkbox) {
        checkbox.checked = isEnabled;
      }
    }
  }
  
  // Thresholds
  thresholdHideInput.value = config.scoreThresholds?.hide || 3;
  thresholdWarningInput.value = config.scoreThresholds?.warning || 5;
  
  // Automatic actions
  actionHideCheckbox.checked = config.autoActions?.hideVideos || false;
  actionWarningCheckbox.checked = config.autoActions?.showWarnings || false;
  actionNotInterestedCheckbox.checked = config.autoActions?.useNotInterested || false;
  
  // Custom prompts
  customPromptsTextarea.value = (config.customPrompts || []).join('\n');
  
  // Logs
  enableLoggingCheckbox.checked = config.logActions || true;
}

// Save configuration
async function saveConfig() {
  // Gather form data
  const newConfig = {
    serverUrl: serverUrlInput.value.trim(),
    wsUrl: wsUrlInput.value.trim(),
    categories: {},
    scoreThresholds: {
      hide: parseFloat(thresholdHideInput.value) || 3,
      warning: parseFloat(thresholdWarningInput.value) || 5
    },
    autoActions: {
      hideVideos: actionHideCheckbox.checked,
      showWarnings: actionWarningCheckbox.checked,
      useNotInterested: actionNotInterestedCheckbox.checked
    },
    customPrompts: customPromptsTextarea.value
      .split('\n')
      .map(line => line.trim())
      .filter(line => line.length > 0),
    logActions: enableLoggingCheckbox.checked
  };
  
  // Collect categories
  categoryCheckboxes.forEach(checkbox => {
    const category = checkbox.id.replace('cat-', '');
    newConfig.categories[category] = checkbox.checked;
  });
  
  // Save to storage
  return new Promise(resolve => {
    chrome.runtime.sendMessage({ type: 'saveConfig', config: newConfig }, response => {
      if (response.success) {
        // Update current configuration
        currentConfig = newConfig;
        
        // Notify content scripts
        chrome.tabs.query({ url: "*://www.youtube.com/*" }, tabs => {
          tabs.forEach(tab => {
            chrome.tabs.sendMessage(tab.id, { type: 'configUpdated' });
          });
        });
        
        showToast('Configuration saved successfully');
      } else {
        showToast('Error saving configuration', true);
      }
      
      resolve(response.success);
    });
  });
}

// Load action log
async function loadActionLog() {
  chrome.runtime.sendMessage({ type: 'getActionLog' }, actionLog => {
    updateActionLogUI(actionLog);
  });
}

// Update UI with action log
function updateActionLogUI(actionLog) {
  // Clear container
  logEntriesContainer.innerHTML = '';
  
  if (!actionLog || actionLog.length === 0) {
    logEntriesContainer.innerHTML = '<div class="empty-log">No actions logged</div>';
    return;
  }
  
  // Add entries
  actionLog.forEach(entry => {
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${entry.type}`;
    
    // Format date
    const date = new Date(entry.timestamp);
    const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
    
    // Content according to action type
    let actionText = '';
    
    switch (entry.type) {
      case 'videoScored':
        actionText = `Video evaluated: ${entry.videoId} - Score: ${entry.score.toFixed(1)}`;
        break;
      case 'videoHidden':
        actionText = `Video hidden: ${entry.videoId} - Score: ${entry.score.toFixed(1)}`;
        break;
      case 'videoWarningApplied':
        actionText = `Warning applied: ${entry.videoId} - Score: ${entry.score.toFixed(1)}`;
        break;
      case 'videoMarkedNotInterested':
        actionText = `Marked as "Not interested": ${entry.videoId}`;
        break;
      default:
        actionText = `Action: ${entry.type} - Video: ${entry.videoId}`;
    }
    
    logEntry.innerHTML = `
      <div class="timestamp">${formattedDate}</div>
      <div class="action">${actionText}</div>
    `;
    
    logEntriesContainer.appendChild(logEntry);
  });
}

// Clear action log
function clearActionLog() {
  chrome.storage.local.set({ actionLog: [] }, () => {
    updateActionLogUI([]);
    showToast('Action log cleared');
  });
}

// Set up tabs
function setupTabs() {
  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      // Deactivate all tabs
      tabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      
      // Activate selected tab
      tab.classList.add('active');
      const tabId = `${tab.dataset.tab}-tab`;
      document.getElementById(tabId).classList.add('active');
    });
  });
}

// Check connection status with WebSocket server
function checkConnectionStatus() {
  // Simulate periodic connection state verification
  clearInterval(wsConnectionInterval);
  
  wsConnectionInterval = setInterval(() => {
    // In a real case, this information would come from the content script
    // Here we simply alternate for demonstration
    chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
      if (tabs.length > 0 && tabs[0].url.includes('youtube.com')) {
        const randomConnected = Math.random() > 0.3; // 70% chance of being connected
        updateConnectionStatus(randomConnected);
      } else {
        updateConnectionStatus(false);
      }
    });
  }, 3000);
  
  // Initial check
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (tabs.length > 0 && tabs[0].url.includes('youtube.com')) {
      updateConnectionStatus(true);
    } else {
      updateConnectionStatus(false);
    }
  });
}

// Update connection status indicator
function updateConnectionStatus(isConnected) {
  connectionStatus.textContent = isConnected ? 'Connected' : 'Disconnected';
  connectionStatus.className = isConnected ? 'connected' : '';
}

// Set up event listeners
function setupEventListeners() {
  // Save configuration
  saveConfigBtn.addEventListener('click', saveConfig);
  
  // Reset default values
  resetConfigBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to reset the configuration to default values?')) {
      chrome.runtime.sendMessage({ type: 'resetConfig' }, () => {
        loadConfig();
        showToast('Configuration reset');
      });
    }
  });
  
  // Clear log
  clearLogBtn.addEventListener('click', () => {
    if (confirm('Are you sure you want to clear the action log?')) {
      clearActionLog();
    }
  });
  
  // Log toggle
  enableLoggingCheckbox.addEventListener('change', async () => {
    const newConfig = {...currentConfig, logActions: enableLoggingCheckbox.checked};
    chrome.runtime.sendMessage({ type: 'saveConfig', config: newConfig }, response => {
      if (response.success) {
        currentConfig = newConfig;
      }
    });
  });
}

// Show toast notification
function showToast(message, isError = false) {
  // Remove previous toast if it exists
  const existingToast = document.querySelector('.toast');
  if (existingToast) {
    existingToast.remove();
  }
  
  // Create new toast
  const toast = document.createElement('div');
  toast.className = `toast ${isError ? 'error' : 'success'}`;
  toast.textContent = message;
  
  // Add to DOM
  document.body.appendChild(toast);
  
  // Animation
  setTimeout(() => {
    toast.classList.add('show');
  }, 10);
  
  // Auto-close
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// Cleanup on close - using 'beforeunload' instead of deprecated 'unload'
window.addEventListener('beforeunload', () => {
  clearInterval(wsConnectionInterval);
});