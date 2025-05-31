// frontend/src/components/StaticTrialCard.jsx
import React from 'react';
import { Grid, Paper, Box, Typography } from '@mui/material';

// This is the simple static TrialCard for "Favorite Trials" demo
const StaticTrialCard = ({ trial }) => (
  <Grid item xs={12} md={6}>
    <Paper elevation={2} sx={{ p: 2, borderRadius: 2, height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        {trial.statusIcon}
        <Typography variant="caption" sx={{ fontWeight: 'medium', color: trial.statusColor }}>
          {trial.status}
        </Typography>
      </Box>
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ flexGrow: 1 }}>
        {trial.title}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{fontSize: '0.8rem'}}>
        SPONSOR
      </Typography>
      <Typography variant="body2"  color="text.primary" gutterBottom sx={{fontSize: '0.8rem', mb:1}}>
        {trial.sponsor}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{fontSize: '0.8rem'}}>
        CONDITION
      </Typography>
      <Typography variant="body2" color="text.primary" sx={{fontSize: '0.8rem'}}>
        {trial.condition}
      </Typography>
    </Paper>
  </Grid>
);

export default StaticTrialCard;