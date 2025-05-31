import React, { useState, useMemo, useEffect } from 'react';
import './App.css';
import ClinicalTrialMatcher from './ClinicalTrialMatcher.jsx';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import { motion } from 'framer-motion';
import useMediaQuery from '@mui/material/useMediaQuery';
import { logger } from './utils/logger';

function App() {
  const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
  const [mode, setMode] = useState(prefersDarkMode ? 'dark' : 'light');

  useEffect(() => {
    logger.info(`Application initialized with ${mode} mode`);
    // Set initial log level based on environment
    const logLevel = import.meta.env.MODE === 'development' ? 'DEBUG' : 'INFO';
    logger.setLogLevel(logLevel);
    logger.debug('Log level configured:', logLevel);
  }, []);

  const theme = useMemo(
    () => {
      logger.debug(`Creating theme with mode: ${mode}`);
      return createTheme({
        palette: {
          mode,
          primary: {
            main: mode === 'dark' ? '#90caf9' : '#1976d2',
          },
          background: {
            default: mode === 'dark' ? '#121212' : '#f5f5f5',
            paper: mode === 'dark' ? '#1e1e1e' : '#ffffff',
          },
        },
        shape: {
          borderRadius: 12,
        },
        components: {
          MuiAppBar: {
            styleOverrides: {
              root: {
                backgroundColor: mode === 'dark' ? '#1e1e1e' : '#ffffff',
                color: mode === 'dark' ? '#ffffff' : '#000000',
                boxShadow: mode === 'dark' 
                  ? '0 1px 3px rgba(255, 255, 255, 0.1)'
                  : '0 1px 3px rgba(0, 0, 0, 0.1)',
              },
            },
          },
        },
      });
    },
    [mode],
  );

  const handleThemeChange = () => {
    const newMode = mode === 'light' ? 'dark' : 'light';
    logger.info(`Theme changed to ${newMode} mode`);
    setMode(newMode);
  };

  const MotionContainer = motion(Container);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box 
        sx={{ 
          display: 'flex',
          flexDirection: 'column',
          minHeight: '100vh',
          width: '100vw',
          margin: 0,
          padding: 0,
          overflow: 'hidden'
        }}
      >
        <AppBar position="sticky" elevation={0}>
          <Toolbar>
            <Typography 
              variant="h6" 
              component="div" 
              sx={{ 
                flexGrow: 1,
                background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 'bold'
              }}
            >
              AI Clinical Trial Matching
            </Typography>
            <IconButton 
              onClick={handleThemeChange}
              color="inherit"
              aria-label={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
            >
              {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
            </IconButton>
          </Toolbar>
        </AppBar>
        
        <Box
          sx={{
            flex: 1,
            display: 'flex',
            width: '100%',
            justifyContent: 'center',
            alignItems: 'flex-start',
            padding: 3
          }}
        >
          <Box
            sx={{
              width: '100%',
              maxWidth: 800,
              margin: '0 auto'
            }}
          >
            <ClinicalTrialMatcher />
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;