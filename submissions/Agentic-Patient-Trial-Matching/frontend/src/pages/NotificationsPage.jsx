// frontend/src/pages/NotificationsPage.jsx
import React from 'react'; // Removed useState, useEffect as state is lifted
import {
  Typography,
  Box,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  useTheme,
  ListItemButton
} from '@mui/material';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
// Icons for mock data will be passed in notification objects
// import InfoIcon from '@mui/icons-material/Info';
// import CheckCircleIcon from '@mui/icons-material/CheckCircle';
// import WarningIcon from '@mui/icons-material/Warning';
// import NewReleasesIcon from '@mui/icons-material/NewReleases';
// import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
// logger can be removed if not used here, or keep if you add local logging
// import { logger } from '../utils/logger';

// formatTimestamp can remain here or be moved to a utils file if used elsewhere
const formatTimestamp = (isoString) => {
  if (!isoString) return '';
  const date = new Date(isoString);
  return date.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
};

// This component now receives notifications and the handler as props
function NotificationsPage({ notifications, onMarkAsReadToggle }) {
  const theme = useTheme();

  if (!notifications || notifications.length === 0) {
    return (
      <Paper sx={{ p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, textAlign: 'center' }}>
        <NotificationsNoneIcon sx={{ fontSize: {xs: 50, sm:60}, color: 'action.disabled' }} />
        <Typography variant="h5" component="h2" gutterBottom>
          No Notifications
        </Typography>
        <Typography variant="body1" color="text.secondary">
          You're all caught up! We'll let you know when there's something new.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <NotificationsNoneIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        Notifications
      </Typography>
      <Paper variant="outlined" sx={{ borderColor: 'divider' }}>
        <List disablePadding>
          {notifications.map((notification, index) => (
            <React.Fragment key={notification.id}>
              <ListItem
                disablePadding
              >
                <ListItemButton
                  alignItems="flex-start"
                  onClick={() => onMarkAsReadToggle(notification.id)} // Use passed handler
                  sx={{
                    py: 1.5,
                    px: { xs: 1.5, sm: 2 },
                    backgroundColor: notification.read
                      ? (theme.palette.mode === 'dark'
                          ? theme.palette.action.disabledBackground
                          : theme.palette.grey[100]
                        )
                      : (theme.palette.mode === 'dark'
                          ? theme.palette.background.paper
                          : theme.palette.background.paper
                        ),
                    '&:hover': {
                        backgroundColor: theme.palette.action.hover,
                    }
                  }}
                >
                  <ListItemIcon sx={{ mt: 0.5, minWidth: 40, color: notification.icon?.props?.color ? `${notification.icon.props.color}.main` : 'inherit' }}>
                    {/* Ensure icon is a valid React element before cloning */}
                    {React.isValidElement(notification.icon) ? React.cloneElement(notification.icon, { sx: { fontSize: '1.5rem' } }) : null}
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Typography component="span" variant="subtitle1" fontWeight={notification.read ? "normal" : "medium"} color="text.primary">
                        {notification.title}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.secondary"
                          sx={{ display: 'block', mb: 0.5 }}
                        >
                          {notification.message}
                        </Typography>
                        <Typography component="span" variant="caption" color="text.disabled">
                          {formatTimestamp(notification.timestamp)} - {notification.type}
                        </Typography>
                      </>
                    }
                  />
                  {!notification.read && (
                    <Chip
                      label="New"
                      color="primary"
                      size="small"
                      sx={{
                        ml: 1,
                        mt: 0.5,
                        alignSelf: 'flex-start',
                        backgroundColor: theme.palette.primary.main,
                        color: theme.palette.primary.contrastText,
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
              {index < notifications.length - 1 && <Divider component="li" variant="inset" />}
            </React.Fragment>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

export default NotificationsPage;