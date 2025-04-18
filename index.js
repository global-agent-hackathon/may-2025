const express = require('express');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'frontend')));

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend', 'index.html'));
});

// API endpoint to handle prototype generation
app.post('/api/generate', (req, res) => {
  const { prompt, type } = req.body;
  
  // Updated command using the new flag-based syntax for the Python script
  const command = `python backend/generate.py --generate "${prompt}" "${type}"`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error: ${error.message}`);
      return res.status(500).json({ error: error.message });
    }
    
    if (stderr) {
      console.error(`stderr: ${stderr}`);
      return res.status(400).json({ error: stderr });
    }
    
    try {
      const result = JSON.parse(stdout);
      return res.json(result);
    } catch (e) {
      return res.status(500).json({ error: 'Failed to parse response', raw: stdout });
    }
  });
});

// Add the new API endpoint for enhancing prompts
app.post('/api/enhance', (req, res) => {
  const { prompt } = req.body;
  
  // Command for prompt enhancement using the new --enhance flag
  const command = `python backend/generate.py --enhance "${prompt}"`;
  
  exec(command, (error, stdout, stderr) => {
    if (error) {
      console.error(`Error enhancing prompt: ${error.message}`);
      return res.status(500).json({ error: error.message });
    }
    
    if (stderr) {
      console.error(`stderr from enhancement: ${stderr}`);
      // We don't return immediately on stderr since Python scripts might output non-critical messages there
    }
    
    // The stdout contains the enhanced prompt directly (not JSON)
    const enhancedPrompt = stdout.trim();
    
    return res.json({ enhancedPrompt });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
}); 