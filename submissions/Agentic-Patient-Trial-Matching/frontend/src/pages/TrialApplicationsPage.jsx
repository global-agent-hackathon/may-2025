// frontend/src/pages/TrialApplicationsPage.jsx
import React from 'react';
import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Link as MuiLink, // Renamed to avoid conflict with react-router-dom Link if used later
  Alert
} from '@mui/material';
import AssessmentIcon from '@mui/icons-material/Assessment'; // Main page icon
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';

// A simplified card for displaying an applied trial
const AppliedTrialCard = ({ trialApplication }) => {
  // Assuming trialApplication contains at least { id, title, status (of trial), phase, condition, detailsUrl, applicationStatus }
  return (
    <Grid item xs={12} md={6}>
      <Card variant="outlined" sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <CardContent sx={{ flexGrow: 1 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="h6" component="h3" fontWeight="medium">
              {trialApplication.title}
            </Typography>
            <Chip
              label={trialApplication.applicationStatus || "Applied"} // e.g., "Applied", "Under Review"
              color="success"
              size="small"
              icon={<CheckCircleOutlineIcon fontSize="small" />}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Trial ID: {trialApplication.id}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Phase: {trialApplication.phase || "N/A"}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
            Condition: {trialApplication.condition || "N/A"}
          </Typography>
          {trialApplication.detailsUrl && (
            <MuiLink
              href={trialApplication.detailsUrl}
              target="_blank"
              rel="noopener noreferrer"
              variant="body2"
              sx={{ display: 'flex', alignItems: 'center' }}
            >
              View Full Trial Details <OpenInNewIcon fontSize="inherit" sx={{ ml: 0.5 }} />
            </MuiLink>
          )}
        </CardContent>
      </Card>
    </Grid>
  );
};

function TrialApplicationsPage({ appliedTrialsList }) {
  if (!appliedTrialsList || appliedTrialsList.length === 0) {
    return (
      <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
        <AssessmentIcon sx={{ fontSize: 60, color: 'action.disabled' }} />
        <Typography variant="h5" component="h2" gutterBottom>
          No Trial Applications Submitted Yet
        </Typography>
        <Typography variant="body1" color="text.secondary">
          You can "apply" to trials from the search results page (Dashboard).
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <AssessmentIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        Your Trial Applications
      </Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        This is a simulation. Applying here does not submit any real applications.
        Application statuses are for demonstration only.
      </Alert>
      <Grid container spacing={3}>
        {appliedTrialsList.map((application) => (
          <Grid item xs={12} md={6} key={application.id}> {/* Grid item with sizing */}
            <AppliedTrialCard trialApplication={application} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default TrialApplicationsPage;