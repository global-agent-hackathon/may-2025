// frontend/src/components/DynamicTrialCard.jsx
import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  Chip,
  Link,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Button,
  Collapse,
  IconButton,
  CardActions // Used for the "Apply" button layout
} from '@mui/material';

// --- MUI Icons ---
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder'; // For "Add to favorites"
import FavoriteIcon from '@mui/icons-material/Favorite'; // For "Remove from favorites"
import CheckCircleIcon from '@mui/icons-material/CheckCircle'; // For "Completed" or "Applied" status
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn'; // For "Apply to Trial" button
import PersonSearchIcon from '@mui/icons-material/PersonSearch'; // For "Recruiting" status
import UpdateIcon from '@mui/icons-material/Update'; // For "Active, not recruiting" status
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'; // For "Unknown" status
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined'; // For other statuses
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline'; // For Match Rationale items
import WarningAmberIcon from '@mui/icons-material/WarningAmber'; // For Flags/Issues items
import LocationOnIcon from '@mui/icons-material/LocationOn'; // For Locations
import ContactPhoneIcon from '@mui/icons-material/ContactPhone'; // For Contact Info
import OpenInNewIcon from '@mui/icons-material/OpenInNew'; // For "View Full Details" link
import ExpandLessIcon from '@mui/icons-material/ExpandLess'; // For Collapse button
import ExpandMoreIcon from '@mui/icons-material/ExpandMore'; // For Collapse button

/**
 * DynamicTrialCard Component
 * Displays detailed information about a single clinical trial.
 * Allows users to favorite, apply (simulated), and view match rationale/flags.
 * This component renders the content within a Paper element and expects its parent
 * to handle Grid item layout and sizing (MUI Grid v2).
 *
 * @param {object} props - Component props.
 * @param {object} props.trial - The trial data object. Expected to have:
 *   id, title, status, phase, condition, locations (array), contactInfo, detailsUrl,
 *   matchRationale (array), flags (array).
 * @param {array} [props.favoriteTrialsList=[]] - List of currently favorited trial IDs.
 * @param {function} [props.onToggleFavorite] - Callback function when the favorite icon is clicked.
 * @param {function} [props.onApplyToTrial] - Callback function when the "Apply" button is clicked.
 * @param {array} [props.appliedTrialsList=[]] - List of trial IDs the user has "applied" to.
 */
const DynamicTrialCard = ({
  trial,
  favoriteTrialsList = [],
  onToggleFavorite,
  onApplyToTrial,
  appliedTrialsList = []
}) => {
  const [expanded, setExpanded] = useState(false); // State for expanding match details

  // Determine if the current trial is in the user's favorites
  const isFavorite = favoriteTrialsList.some(favTrial => favTrial.id === trial.id);
  // Determine if the user has already "applied" to this trial
  const hasApplied = appliedTrialsList.some(app => app.id === trial.id);

  // Handler to toggle favorite status
  const handleToggleFavorite = () => {
    if (onToggleFavorite) {
      onToggleFavorite(trial);
    }
  };

  // Handler for the "Apply to Trial" button
  const handleApply = () => {
    if (onApplyToTrial && !hasApplied) {
      onApplyToTrial(trial);
    }
  };

  // Determines the chip color and icon based on trial status
  const getStatusChipProps = (status) => {
    if (!status) return { label: 'Unknown', color: 'default', icon: <HelpOutlineIcon fontSize="small" sx={{ mr: 0.5 }} /> };
    const lowerStatus = status.toLowerCase();
    if (lowerStatus.includes('recruiting')) {
      return { label: status, color: 'success', icon: <PersonSearchIcon fontSize="small" sx={{ mr: 0.5 }} /> };
    } else if (lowerStatus.includes('completed')) {
      return { label: status, color: 'info', icon: <CheckCircleIcon fontSize="small" sx={{ mr: 0.5 }} /> };
    } else if (lowerStatus.includes('active') && lowerStatus.includes('not recruiting')) {
      return { label: status, color: 'warning', icon: <UpdateIcon fontSize="small" sx={{ mr: 0.5 }} /> };
    }
    return { label: status, color: 'default', icon: <InfoOutlinedIcon fontSize="small" sx={{ mr: 0.5 }} /> };
  };

  const statusProps = getStatusChipProps(trial.status);

  // The component now returns the Paper directly.
  // The parent component using this card will wrap it in a <Grid item xs={...} ...> for layout.
  return (
    <Paper
      elevation={2}
      sx={{
        p: 2,
        borderRadius: 2,
        height: '100%', // Ensures Paper takes full height of its Grid item container
        display: 'flex',
        flexDirection: 'column',
        position: 'relative' // For absolute positioning of the favorite icon
      }}
    >
      {/* Favorite Toggle Button (absolute positioned) */}
      {onToggleFavorite && (
        <IconButton
          onClick={handleToggleFavorite}
          size="small"
          sx={{ position: 'absolute', top: 8, right: 8, zIndex: 1 }}
          aria-label={isFavorite ? "Remove from favorites" : "Add to favorites"}
        >
          {isFavorite ? <FavoriteIcon color="error" /> : <FavoriteBorderIcon />}
        </IconButton>
      )}

      {/* Trial Status and Phase */}
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, pr: onToggleFavorite ? 4 : 0 /* Make space for fav icon */ }}>
        <Chip
          icon={statusProps.icon}
          label={statusProps.label}
          color={statusProps.color} // No 'as any' needed
          size="small"
        />
        {trial.phase && <Chip label={trial.phase} variant="outlined" size="small" />}
      </Box>

      {/* Trial Title and ID */}
      <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
        {trial.title} ({trial.id})
      </Typography>

      {/* Trial Condition */}
      <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.8rem', mb: 0.5 }}>
        CONDITION
      </Typography>
      <Typography variant="body2" color="text.primary" sx={{ fontSize: '0.8rem', mb: 1.5 }}>
        {trial.condition}
      </Typography>

      {/* Trial Locations (if available) */}
      {trial.locations && trial.locations.length > 0 && (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary', fontSize: '0.8rem' }}>
          <LocationOnIcon fontSize="small" sx={{ mr: 0.5 }} /> Locations: {trial.locations.join(', ')}
        </Box>
      )}

      {/* Contact Info (if available) */}
      {trial.contactInfo && (
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1, color: 'text.secondary', fontSize: '0.8rem' }}>
          <ContactPhoneIcon fontSize="small" sx={{ mr: 0.5 }} /> Contact: {trial.contactInfo}
        </Box>
      )}

      {/* Link to Full Details (if available) */}
      {trial.detailsUrl && (
        <Link
          href={trial.detailsUrl}
          target="_blank"
          rel="noopener noreferrer"
          variant="body2"
          sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}
        >
          View Full Details <OpenInNewIcon fontSize="inherit" sx={{ ml: 0.5 }} />
        </Link>
      )}

      {/* Collapsible Section for Match Rationale and Flags */}
      <Box sx={{ marginTop: 'auto' }}> {/* Pushes this section and Apply button to the bottom */}
        {((trial.matchRationale && trial.matchRationale.length > 0) || (trial.flags && trial.flags.length > 0)) && (
           <Button
              fullWidth
              size="small"
              onClick={() => setExpanded(!expanded)}
              endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              sx={{ mt: 1, mb: onApplyToTrial ? 1 : 0 }} // Margin bottom if Apply button is present
            >
              {expanded ? 'Hide Match Details' : 'Show Match Details'}
            </Button>
        )}
        <Collapse in={expanded} timeout="auto" unmountOnExit>
          {/* Match Rationale List */}
          {trial.matchRationale && trial.matchRationale.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" fontWeight="medium" color="success.main">Match Rationale:</Typography>
              <List dense disablePadding>
                {trial.matchRationale.map((reason, index) => (
                  <ListItem key={`rationale-${index}`} sx={{ py: 0.2, pl: 1 }}>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <CheckCircleOutlineIcon color="success" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={reason} primaryTypographyProps={{ variant: 'body2', fontSize: '0.8rem' }} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          {/* Flags/Potential Issues List */}
          {trial.flags && trial.flags.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="caption" fontWeight="medium" color="warning.main">Flags / Potential Issues:</Typography>
              <List dense disablePadding>
                {trial.flags.map((flag, index) => (
                  <ListItem key={`flag-${index}`} sx={{ py: 0.2, pl: 1 }}>
                    <ListItemIcon sx={{ minWidth: 24 }}>
                      <WarningAmberIcon color="warning" fontSize="small" />
                    </ListItemIcon>
                    <ListItemText primary={flag} primaryTypographyProps={{ variant: 'body2', fontSize: '0.8rem' }} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Collapse>

        {/* Apply to Trial Button */}
        {onApplyToTrial && (
          <CardActions sx={{ justifyContent: 'flex-end', p: 0, pt: 1 }}>
            <Button
              variant={hasApplied ? "text" : "contained"}
              size="small"
              color={hasApplied ? "success" : "primary"}
              startIcon={hasApplied ? <CheckCircleIcon /> : <AssignmentTurnedInIcon />}
              onClick={handleApply}
              disabled={hasApplied}
              fullWidth
            >
              {hasApplied ? "Application Submitted" : "Apply to this Trial (Simulated)"}
            </Button>
          </CardActions>
        )}
      </Box>
    </Paper>
  );
};

export default DynamicTrialCard;