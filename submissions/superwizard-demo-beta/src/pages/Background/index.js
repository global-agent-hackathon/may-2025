// console.log('This is the background page.');
// console.log('Put the background scripts here.');

// Set up side panel behavior when extension is installed or updated
chrome.runtime.onInstalled.addListener(() => {
  // Configure the side panel to open when the extension action is clicked
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
});

// Handle extension icon click
chrome.action.onClicked.addListener((tab) => {
  // Open the side panel for the current window
  chrome.sidePanel.open({ windowId: tab.windowId });
});
