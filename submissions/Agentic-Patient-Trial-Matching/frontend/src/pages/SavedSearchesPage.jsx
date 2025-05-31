// frontend/src/pages/SavedSearchesPage.jsx
import React from 'react';
import {
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip
} from '@mui/material';
import BookmarkAddedIcon from '@mui/icons-material/BookmarkAdded'; // Main page icon
import SearchIcon from '@mui/icons-material/Search'; // Icon for re-running search
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'; // Icon for removing a saved search

function SavedSearchesPage({ savedSearchesList, onExecuteSavedSearch, onRemoveSavedSearch }) {
  if (!savedSearchesList || savedSearchesList.length === 0) {
    return (
      <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, textAlign: 'center' }}>
        <BookmarkAddedIcon sx={{ fontSize: {xs: 50, sm:60}, color: 'action.disabled' }} />
        <Typography variant="h5" component="h2" gutterBottom>
          No Saved Searches Yet
        </Typography>
        <Typography variant="body1" color="text.secondary">
          You can save your Patient ID searches from the "Find Clinical Trials" section on your Dashboard.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <BookmarkAddedIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        Saved Searches
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 2 }}>
        Click on a saved Patient ID to re-run the search on your Dashboard.
      </Typography>
      <Paper variant="outlined" sx={{ borderColor: 'divider' }}>
        <List disablePadding>
          {savedSearchesList.map((searchTerm, index) => (
            <ListItem
              key={`${searchTerm}-${index}`} // Use index for key if terms might not be unique (though our logic prevents duplicates)
              secondaryAction={
                <Tooltip title="Remove this saved search">
                  <IconButton
                    edge="end"
                    aria-label="remove saved search"
                    onClick={(e) => {
                      e.stopPropagation(); // Prevent ListItemButton's onClick from firing
                      if (window.confirm(`Are you sure you want to remove the saved search for Patient ID: "${searchTerm}"?`)) {
                        onRemoveSavedSearch(searchTerm);
                      }
                    }}
                  >
                    <DeleteOutlineIcon />
                  </IconButton>
                </Tooltip>
              }
              divider={index < savedSearchesList.length - 1} // Add divider between items
            >
              <ListItemButton onClick={() => onExecuteSavedSearch(searchTerm)}>
                <ListItemIcon>
                  <SearchIcon />
                </ListItemIcon>
                <ListItemText
                  primary={`Patient ID: ${searchTerm}`}
                  primaryTypographyProps={{ fontWeight: 'medium' }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

export default SavedSearchesPage;