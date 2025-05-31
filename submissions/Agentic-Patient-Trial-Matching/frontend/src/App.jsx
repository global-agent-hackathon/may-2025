// frontend/src/App.jsx
import React, { useState, useMemo, useEffect } from 'react';
import './App.css';
import ClinicalTrialMatcher from './ClinicalTrialMatcher.jsx';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Box from '@mui/material/Box';
import useMediaQuery from '@mui/material/useMediaQuery';
import { logger } from './utils/logger';

function App() {
  const prefersDarkModeSystem = useMediaQuery('(prefers-color-scheme: dark)');
  // Initialize mode from sessionStorage or system preference
  const [mode, setMode] = useState(() => {
    const storedMode = sessionStorage.getItem('themeMode');
    return storedMode ? storedMode : (prefersDarkModeSystem ? 'dark' : 'light');
  });


  useEffect(() => {
    logger.info(`Application initialized with ${mode} mode`);
    const logLevel = import.meta.env.MODE === 'development' ? 'DEBUG' : 'INFO';
    logger.setLogLevel(logLevel);
    logger.debug('Log level configured:', logLevel);
    sessionStorage.setItem('themeMode', mode); // Save theme mode on change
  }, [mode]);

  const theme = useMemo( /* ... theme creation logic remains the same ... */
    () => {
      logger.debug(`Creating theme with mode: ${mode}`);
      return createTheme({
        palette: {
          mode,
          primary: {
            main: mode === 'dark' ? '#90caf9' : '#1976d2',
            // You might add light/dark variants if primary is used in buttons/alerts that need contrast
          },
          // Define other colors like warning, info, success properly for dark mode
          warning: {
            main: '#ffa726', // Default MUI orange
            light: mode === 'dark' ? '#ffb74d' : '#ffe0b2', // Lighter for dark mode text/borders
            dark: mode === 'dark' ? '#f57c00' : '#e65100',
            contrastText: mode === 'dark' ? 'rgba(0,0,0,0.87)' : '#fff',
          },
          info: {
            main: '#29b6f6', // Default MUI light blue
            light: mode === 'dark' ? '#4fc3f7' : '#b3e5fc',
            dark: mode === 'dark' ? '#0288d1' : '#01579b',
            contrastText: mode === 'dark' ? 'rgba(0,0,0,0.87)' : '#fff',
          },
          text: {
              primary: mode === 'dark' ? '#e0e0e0' : 'rgba(0, 0, 0, 0.87)',
              secondary: mode === 'dark' ? '#bdbdbd' : 'rgba(0, 0, 0, 0.6)',
          },
          background: {
            default: mode === 'dark' ? '#121212' : '#f5f5f5',
            paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          },
          divider: mode === 'dark' ? 'rgba(255, 255, 255, 0.12)' : 'rgba(0, 0, 0, 0.12)',
        },
        shape: { borderRadius: 12, },
      });
    },
    [mode],
  );

  const handleThemeChange = () => {
    setMode((prevMode) => {
      const newMode = prevMode === 'light' ? 'dark' : 'light';
      logger.info(`Theme changed to ${newMode} mode`);
      return newMode;
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', width: '100%', }} >
        <Box component="main" sx={{ flexGrow: 1, display: 'flex', width: '100%', }} >
          <Box sx={{ width: '100%', }} >
            {/* Pass mode and handleThemeChange down */}
            <ClinicalTrialMatcher
              currentThemeMode={mode}
              onThemeChange={handleThemeChange}
            />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;