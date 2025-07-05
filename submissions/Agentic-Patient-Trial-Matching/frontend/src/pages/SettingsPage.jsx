// frontend/src/pages/SettingsPage.jsx
import React from 'react';
import {
  Typography,
  Box,
  Paper,
  FormGroup,
  FormControlLabel,
  Switch,
  Button,
  // Divider, // Not used in current layout
  List,
  ListItem,
  // ListItemText, // Not directly used for buttons
  // ListItemIcon, // Not directly used for buttons
  Alert,
  useTheme // Import useTheme to access theme palette
} from '@mui/material';
import SettingsIcon from '@mui/icons-material/SettingsApplications';
import Brightness4Icon from '@mui/icons-material/Brightness4';
import Brightness7Icon from '@mui/icons-material/Brightness7';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';
import { logger } from '../utils/logger';

function SettingsPage({
  currentThemeMode,
  onThemeChange,
  onClearFavoriteTrials,
  onClearSavedSearches,
  onClearRecentSearchHistory,
}) {
  const theme = useTheme(); // Access the current theme

  const handleClearFavorites = () => { /* ... remains same ... */
    if (window.confirm("Are you sure you want to clear all favorite trials? This cannot be undone for the current session.")) {
      onClearFavoriteTrials(); logger.info("Favorite trials cleared from settings.");
    }
  };
  const handleClearSaved = () => { /* ... remains same ... */
    if (window.confirm("Are you sure you want to clear all saved searches? This cannot be undone for the current session.")) {
      onClearSavedSearches(); logger.info("Saved searches cleared from settings.");
    }
  };
  const handleClearRecents = () => { /* ... remains same ... */
     if (window.confirm("Are you sure you want to clear recent search history (both IDs and full results)? This cannot be undone for the current session.")) {
      onClearRecentSearchHistory(); logger.info("Recent search history cleared from settings.");
    }
  };

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <SettingsIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        Settings
      </Typography>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, mb: 3, borderColor: 'divider' }}>
        <Typography variant="h6" component="h2" gutterBottom sx={{ color: 'text.primary' }}>
          Appearance
        </Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Switch
                checked={currentThemeMode === 'dark'}
                onChange={onThemeChange}
                // sx={{ // Example styling for the switch track/thumb if needed
                //   '& .MuiSwitch-switchBase.Mui-checked': {
                //     color: theme.palette.primary.main, // Or a specific color for dark mode
                //   },
                //   '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                //     backgroundColor: theme.palette.primary.light, // Or a specific color
                //   },
                // }}
              />
            }
            // Ensure label text has good contrast
            label={`Theme: ${currentThemeMode === 'dark' ? 'Dark Mode' : 'Light Mode'}`}
            sx={{ color: 'text.primary' }}
          />
        </FormGroup>
      </Paper>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, borderColor: 'divider' }}>
        <Typography variant="h6" component="h2" gutterBottom sx={{ color: 'text.primary' }}>
          Session Data Management
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{mb: 2}}>
          These actions will clear data stored in your current browser session.
          They will reset when you close your browser tab/window.
        </Typography>
        <List>
          {[
            { label: 'Clear Favorite Trials', handler: handleClearFavorites, key: 'fav' },
            { label: 'Clear Saved Searches', handler: handleClearSaved, key: 'saved' },
            { label: 'Clear Recent Search History', handler: handleClearRecents, key: 'recent' }
          ].map(item => (
            <ListItem disablePadding key={item.key} sx={{mb:1.5}}>
              <Button
                variant="outlined" // Outlined buttons can be tricky with dark themes
                // Consider "contained" for more pop on dark, or ensure outlined has good contrast
                // color="warning" // "warning" color might need adjustment in dark theme definition
                onClick={item.handler}
                fullWidth
                startIcon={<DeleteSweepIcon />}
                sx={{
                  // Ensure good contrast for outlined buttons in dark mode
                  borderColor: currentThemeMode === 'dark' ? 'rgba(255, 255, 255, 0.5)' : 'rgba(0, 0, 0, 0.23)',
                  color: currentThemeMode === 'dark' ? theme.palette.warning.light : theme.palette.warning.main, // Use theme colors
                  '&:hover': {
                    borderColor: currentThemeMode === 'dark' ? theme.palette.warning.main : theme.palette.warning.dark,
                    backgroundColor: currentThemeMode === 'dark' ? 'rgba(255, 167, 38, 0.08)' : 'rgba(255,152,0, 0.04)' // Adjust hover for warning
                  }
                }}
              >
                {item.label}
              </Button>
            </ListItem>
          ))}
        </List>
         <Alert
            severity="info"
            sx={{
              mt: 2,
              // Ensure alert has good contrast in dark mode
              backgroundColor: currentThemeMode === 'dark' ? theme.palette.info.dark : theme.palette.info.light, // Adjust background
              color: currentThemeMode === 'dark' ? theme.palette.getContrastText(theme.palette.info.dark) : theme.palette.getContrastText(theme.palette.info.light), // Ensure text is readable
              '& .MuiAlert-icon': { // Style icon color if needed
                color: currentThemeMode === 'dark' ? theme.palette.info.light : theme.palette.info.main,
              }
            }}
          >
            Note: After clearing recent search history, the display on the dashboard will update upon your next search or page navigation.
        </Alert>
      </Paper>
    </Box>
  );
}

export default SettingsPage;