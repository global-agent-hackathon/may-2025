// frontend/src/pages/FavoriteTrialsDisplayPage.jsx
import React from 'react';
import { Typography, Box, Paper, Grid } from '@mui/material';
import FavoriteIcon from '@mui/icons-material/Favorite';
import DynamicTrialCard from '../components/DynamicTrialCard'; // Adjust path if necessary

function FavoriteTrialsDisplayPage({ favoriteTrialsList, onToggleFavorite }) {
  if (!favoriteTrialsList || favoriteTrialsList.length === 0) {
    return (
      <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
        <FavoriteIcon sx={{ fontSize: 60, color: 'action.disabled' }} />
        <Typography variant="h5" component="h2" gutterBottom>
          No Favorite Trials Yet
        </Typography>
        <Typography variant="body1" color="text.secondary">
          You can add trials to your favorites from the search results.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom sx={{ mb: 3 }}>
        Your Favorite Trials ({favoriteTrialsList.length})
      </Typography>
      <Grid container spacing={2.5}>
        {favoriteTrialsList.map((trial) => (
          // Pass favoriteTrialsList and onToggleFavorite so the card can manage its favorite status
          <Grid item xs={12} sm={6} md={6} key={trial.id}> {/* Grid item with sizing */}
            <DynamicTrialCard
              trial={trial}
              favoriteTrialsList={favoriteTrialsList}
              onToggleFavorite={onToggleFavorite}
              // No onApplyToTrial or appliedTrialsList needed here unless you want that feature on this page
            />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default FavoriteTrialsDisplayPage;