/**
 * Vilcos Template Watcher
 *
 * This script watches the templates directory for changes and triggers 
 * Vite's build process as needed, rather than manually copying files.
 */

const chokidar = require('chokidar');
const debounce = require('lodash.debounce');
const { exec } = require('child_process');
const path = require('path');

// Configuration
const CONFIG = {
  // Directory to watch
  templatesDir: path.join(__dirname, 'templates'),
  
  // Files to ignore
  ignorePatterns: [
    /(^|[\/\\])\../,  // dotfiles
    /node_modules/,   // node_modules directory
    /\.git/,          // git directory
    /\.(md|json|lock)$/i,  // markdown, json, and lock files
    /package(-lock)?\.json/  // package.json files
  ],
  
  // Watch options
  watchOptions: {
    persistent: true,
    usePolling: true,
    interval: 100,
    awaitWriteFinish: {
      stabilityThreshold: 300,
      pollInterval: 100
    }
  }
};

// Install missing dependencies if needed
try {
  require.resolve('chokidar');
  require.resolve('lodash.debounce');
} catch (e) {
  console.log('Installing required dependencies...');
  try {
    exec('npm install --save-dev chokidar lodash.debounce', (error) => {
      if (error) {
        console.error('Failed to install dependencies:', error.message);
        process.exit(1);
      }
    });
  } catch (err) {
    console.error('Failed to install dependencies:', err.message);
    process.exit(1);
  }
}

// Initialize watcher with proper options
const watcher = chokidar.watch(CONFIG.templatesDir, {
  ...CONFIG.watchOptions,
  ignored: CONFIG.ignorePatterns
});

// Debounced function to trigger Vite build
const triggerBuild = debounce(() => {
  console.log('Changes detected, triggering build...');
  exec('npm run build', (error, stdout, stderr) => {
    if (error) {
      console.error(`Build error: ${error.message}`);
      return;
    }
    if (stderr) {
      console.error(`Build warnings: ${stderr}`);
    }
    console.log(`Build completed: ${stdout}`);
  });
}, 1000);

// Set up event listeners
watcher
  .on('add', triggerBuild)
  .on('change', triggerBuild)
  .on('unlink', triggerBuild);

console.log(`Watching for changes in: ${CONFIG.templatesDir}`);
console.log('Press Ctrl+C to stop');

// Handle process termination
process.on('SIGINT', () => {
  console.log('\nStopping watcher...');
  watcher.close().then(() => {
    console.log('Watcher stopped');
    process.exit(0);
  }).catch(err => {
    console.error('Error stopping watcher:', err);
    process.exit(1);
  });
}); 