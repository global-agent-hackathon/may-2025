// frontend/src/ClinicalTrialMatcher.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid, // Note: Grid is imported but not used. Consider removing if not planned for use.
  Typography,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Chip,
  Button, // Note: Button is imported but not used. Consider removing if not planned for use.
  Link,
  Divider,
  Tooltip,
} from '@mui/material';
import { styled, useTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// --- MUI Icons ---
import DashboardIconOriginal from '@mui/icons-material/Dashboard';
import AssessmentIcon from '@mui/icons-material/Assessment';
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder';
import BookmarkBorderIcon from '@mui/icons-material/BookmarkBorder';
import NotificationsNoneIcon from '@mui/icons-material/NotificationsNone';
import SettingsIcon from '@mui/icons-material/Settings';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import ArticleIcon from '@mui/icons-material/Article';
// ExpandMoreIcon is imported but not used. Consider removing.
// import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FavoriteIcon from '@mui/icons-material/Favorite';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import LogoutIcon from '@mui/icons-material/Logout';
// Icons for mock notifications
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import WarningIcon from '@mui/icons-material/Warning';
import NewReleasesIcon from '@mui/icons-material/NewReleases';

// --- Custom Components ---
import TrialSearchSection from './components/TrialSearchSection';

// --- Page Components ---
import TrialApplicationsPage from './pages/TrialApplicationsPage';
import FavoriteTrialsDisplayPage from './pages/FavoriteTrialsDisplayPage';
import SavedSearchesPage from './pages/SavedSearchesPage';
import NotificationsPage from './pages/NotificationsPage';
import SettingsPage from './pages/SettingsPage';
import HelpCenterPage from './pages/HelpCenterPage';
import BlogPage from './pages/BlogPage';

// --- Constants ---
const SIDEBAR_WIDTH = 280;
const MAX_SAVED_ITEMS = 10; // Maximum number of items for lists like favorites, saved searches, etc.
const CLEAR_HISTORY_TRIGGER_VALUE = '__CLEAR_HISTORY_TRIGGER__'; // Special value to trigger history clearing

const mockUser = {
  name: 'Dipanjan Ghosal',
  initials: 'DG',
};

const VIEWS = {
  DASHBOARD: 'dashboard',
  APPLICATIONS: 'applications',
  FAVORITES: 'favorites',
  SAVED_SEARCHES: 'saved_searches',
  NOTIFICATIONS: 'notifications',
  SETTINGS: 'settings',
  HELP: 'help',
  BLOG: 'blog',
};

// Initial mock notifications data
const initialMockNotifications = [
  {
    id: 'notif1',
    type: 'New Feature',
    icon: <NewReleasesIcon color="primary" />,
    title: "Advanced Search Filters Implemented!",
    message: "Explore more precise trial matching...",
    timestamp: "2025-05-31T10:00:00Z",
    read: false,
  },
  {
    id: 'notif2',
    type: 'Application Update',
    icon: <CheckCircleIcon color="success" />,
    title: "Application for NCT01234567 Status Update",
    message: "Your simulated application for trial NCT01234567 has been 'Reviewed'.",
    timestamp: "2025-05-30T14:30:00Z",
    read: true,
  },
  {
    id: 'notif3',
    type: 'System Maintenance',
    icon: <WarningIcon color="warning" />,
    title: "Scheduled Maintenance Upcoming",
    message: "AI Clinical Trial Matching will undergo scheduled maintenance on June 5th...",
    timestamp: "2025-05-29T09:15:00Z",
    read: false,
  },
  {
    id: 'notif4',
    type: 'New Blog Post',
    icon: <InfoIcon color="info" />,
    title: "Read Our Latest Blog: 'Understanding Clinical Trial Phases'",
    message: "A new article has been published on our blog...",
    timestamp: "2025-05-28T16:00:00Z",
    read: true,
  },
  {
    id: 'notif5',
    type: 'Tip',
    icon: <HelpOutlineIcon color="action" />,
    title: "Tip: Save Your Searches!",
    message: "Don't forget you can save your frequent Patient ID searches...",
    timestamp: "2025-05-27T11:00:00Z",
    read: false,
  },
];

// Template for initializing or resetting overview statistics
const initialOverviewStatsTemplate = [
  { label: 'Trials applied (Searches)', value: 0, color: 'primary.main', key: 'trialsApplied' },
  { label: 'Favorite trials', value: 0, color: 'error.main', key: 'favoriteTrialsCount' },
  { label: 'Saved searches', value: 0, color: 'success.main', key: 'savedSearchesCount' },
  { label: 'Applications Submitted', value: 0, color: 'info.main', key: 'applicationsSubmittedCount' },
  { label: 'Unread Notifications', value: 0, color: 'secondary.main', key: 'unreadNotificationsCount' },
];

// --- Styled Components ---

/**
 * StyledListItemButton is a custom styled MUI ListItemButton for navigation items.
 * It applies specific styles for active and hover states.
 */
const StyledListItemButton = styled(ListItemButton, {
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({
  margin: theme.spacing(0.5, 1),
  borderRadius: theme.shape.borderRadius,
  color: theme.palette.text.secondary,
  '& .MuiListItemIcon-root': {
    color: theme.palette.action.active,
  },
  ...(active && { // Styles for active state
    backgroundColor: theme.palette.action.selected,
    color: theme.palette.primary.main,
    fontWeight: theme.typography.fontWeightMedium,
    '& .MuiListItemIcon-root': {
      color: theme.palette.primary.main,
    },
  }),
  '&:hover': { // Styles for hover state
    backgroundColor: theme.palette.action.hover,
    color: theme.palette.text.primary,
    '& .MuiListItemIcon-root': {
      color: theme.palette.action.active,
    },
  },
}));

/**
 * @typedef {object} Notification
 * @property {string} id - Unique identifier for the notification.
 * @property {string} type - Type of notification (e.g., 'New Feature', 'Application Update').
 * @property {React.ReactElement} icon - Icon element for the notification.
 * @property {string} title - Title of the notification.
 * @property {string} message - Detailed message of the notification.
 * @property {string} timestamp - ISO date string for when the notification was generated.
 * @property {boolean} read - Read status of the notification.
 */

/**
 * @typedef {object} Trial
 * @property {string} id - Unique identifier for the trial (e.g., NCT ID).
 * // Add other trial properties as needed for type safety
 */

/**
 * @typedef {object} AppliedTrial
 * @extends Trial
 * @property {string} applicationStatus - Status of the application (e.g., "Applied", "Reviewed").
 * @property {string} applicationDate - ISO date string for when the application was made.
 */


/**
 * DashboardLayout component provides the main structure for the application,
 * including a sidebar, main content area, and a right-hand overview column.
 * It manages the active view, user data (favorites, saved searches, applications, notifications),
 * and related statistics.
 *
 * @param {object} props - The component's props.
 * @param {string} props.currentThemeMode - The current theme mode ('light' or 'dark').
 * @param {function} props.onThemeChange - Callback function to change the theme mode.
 */
function DashboardLayout({ currentThemeMode, onThemeChange }) {
  const theme = useTheme();

  // --- State Variables ---
  /** @type {[string, React.Dispatch<React.SetStateAction<string>>]} */
  const [activeView, setActiveView] = useState(VIEWS.DASHBOARD);

  /** @type {[Array<object>, React.Dispatch<React.SetStateAction<Array<object>>>]} */
  const [overviewStats, setOverviewStats] = useState(initialOverviewStatsTemplate);

  /** @type {[Array<Trial>, React.Dispatch<React.SetStateAction<Array<Trial>>>]} */
  const [favoriteTrialsList, setFavoriteTrialsList] = useState(() => {
    const saved = sessionStorage.getItem('favoriteClinicalTrials');
    return saved ? JSON.parse(saved) : [];
  });

  /** @type {[Array<string>, React.Dispatch<React.SetStateAction<Array<string>>>]} */
  const [savedSearchesList, setSavedSearchesList] = useState(() => {
    const saved = sessionStorage.getItem('savedClinicalSearches');
    return saved ? JSON.parse(saved) : [];
  });

  /**
   * Stores a search term passed from another view (e.g., saved searches)
   * to be pre-filled in the dashboard's search section.
   * @type {[string, React.Dispatch<React.SetStateAction<string>>]}
   */
  const [initialSearchTermForDashboard, setInitialSearchTermForDashboard] = useState('');

  /** @type {[Array<AppliedTrial>, React.Dispatch<React.SetStateAction<Array<AppliedTrial>>>]} */
  const [appliedTrialsList, setAppliedTrialsList] = useState(() => {
    const saved = sessionStorage.getItem('appliedClinicalTrials');
    return saved ? JSON.parse(saved) : [];
  });

  /** @type {[Array<Notification>, React.Dispatch<React.SetStateAction<Array<Notification>>>]} */
  const [notifications, setNotifications] = useState(() => {
    const savedNotifications = sessionStorage.getItem('userNotifications');
    return savedNotifications ? JSON.parse(savedNotifications) : initialMockNotifications;
  });

  // --- useEffect Hooks ---

  // Effect to persist favorite trials to session storage and update overview stats.
  useEffect(() => {
    sessionStorage.setItem('favoriteClinicalTrials', JSON.stringify(favoriteTrialsList));
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'favoriteTrialsCount' ? { ...stat, value: favoriteTrialsList.length } : stat
      )
    );
  }, [favoriteTrialsList]);

  // Effect to persist saved searches to session storage and update overview stats.
  useEffect(() => {
    sessionStorage.setItem('savedClinicalSearches', JSON.stringify(savedSearchesList));
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'savedSearchesCount' ? { ...stat, value: savedSearchesList.length } : stat
      )
    );
  }, [savedSearchesList]);

  // Effect to persist applied trials to session storage and update overview stats.
  useEffect(() => {
    sessionStorage.setItem('appliedClinicalTrials', JSON.stringify(appliedTrialsList));
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'applicationsSubmittedCount' ? { ...stat, value: appliedTrialsList.length } : stat
      )
    );
  }, [appliedTrialsList]);

  // Effect to handle initial search term for the dashboard.
  // Clears the term after a short delay to ensure it's used once.
  useEffect(() => {
    if (initialSearchTermForDashboard && activeView === VIEWS.DASHBOARD) {
      // The following 'if' block is empty in the original code.
      // It might be a placeholder or an incomplete feature.
      // If `CLEAR_HISTORY_TRIGGER_VALUE` is used, it should not trigger a search.
      if (initialSearchTermForDashboard !== CLEAR_HISTORY_TRIGGER_VALUE) {
        // Potential logic for non-trigger values could go here.
      }
      // Reset the initial search term after a brief moment.
      const timer = setTimeout(() => {
        setInitialSearchTermForDashboard('');
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [initialSearchTermForDashboard, activeView]);

  // Effect to persist notifications to session storage and update overview stats for unread count.
  useEffect(() => {
    sessionStorage.setItem('userNotifications', JSON.stringify(notifications));
    const unreadCount = notifications.filter(n => !n.read).length;
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'unreadNotificationsCount' ? { ...stat, value: unreadCount } : stat
      )
    );
  }, [notifications]);


  // --- Event Handlers ---

  /**
   * Changes the active view in the dashboard.
   * If navigating away from the dashboard, clears any pending initial search term.
   * @param {string} view - The key of the view to switch to (from VIEWS object).
   */
  const handleViewChange = (view) => {
    setActiveView(view);
    if (view !== VIEWS.DASHBOARD && initialSearchTermForDashboard) {
      setInitialSearchTermForDashboard('');
    }
  };

  /**
   * Increments the count of "Trials applied (Searches)" in the overview statistics.
   * This is typically called when a search is executed in the TrialSearchSection.
   */
  const incrementTrialsAppliedCount = () => {
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'trialsApplied' ? { ...stat, value: stat.value + 1 } : stat
      )
    );
  };

  /**
   * Toggles a trial's favorite status.
   * Adds the trial to favorites if not already present, or removes it if it is.
   * Maintains a maximum number of favorite trials.
   * @param {Trial} trialToToggle - The trial object to toggle.
   */
  const toggleFavoriteTrial = (trialToToggle) => {
    setFavoriteTrialsList(prevList => {
      const isFavorite = prevList.some(favTrial => favTrial.id === trialToToggle.id);
      if (isFavorite) {
        return prevList.filter(favTrial => favTrial.id !== trialToToggle.id);
      } else {
        const updatedList = [trialToToggle, ...prevList.filter(favTrial => favTrial.id !== trialToToggle.id)];
        return updatedList.slice(0, MAX_SAVED_ITEMS); // Keep only the most recent MAX_SAVED_ITEMS
      }
    });
  };

  /**
   * Saves a new search term if it's not empty and not already saved.
   * Maintains a maximum number of saved searches.
   * @param {string} searchTerm - The search term to save.
   */
  const handleSaveSearch = (searchTerm) => {
    if (searchTerm && !savedSearchesList.includes(searchTerm)) {
      setSavedSearchesList(prevList => {
        const updatedList = [searchTerm, ...prevList.filter(s => s !== searchTerm)];
        return updatedList.slice(0, MAX_SAVED_ITEMS);
      });
    }
  };

  /**
   * Removes a search term from the list of saved searches.
   * @param {string} searchTerm - The search term to remove.
   */
  const handleRemoveSavedSearch = (searchTerm) => {
    setSavedSearchesList(prevList => prevList.filter(s => s !== searchTerm));
  };

  /**
   * Sets a saved search term as the initial search term for the dashboard
   * and navigates to the dashboard view.
   * @param {string} searchTerm - The search term to execute.
   */
  const executeSavedSearch = (searchTerm) => {
    setInitialSearchTermForDashboard(searchTerm);
    setActiveView(VIEWS.DASHBOARD);
  };

  /**
   * Adds a trial to the list of applied trials if not already applied.
   * Attaches application status and date.
   * @param {Trial} trialToApply - The trial object to apply for.
   */
  const handleApplyToTrial = (trialToApply) => {
    setAppliedTrialsList(prevList => {
      const alreadyApplied = prevList.some(appliedTrial => appliedTrial.id === trialToApply.id);
      if (!alreadyApplied) {
        const application = {
          ...trialToApply,
          applicationStatus: "Applied",
          applicationDate: new Date().toISOString(),
        };
        const updatedList = [application, ...prevList];
        return updatedList.slice(0, MAX_SAVED_ITEMS);
      }
      return prevList;
    });
  };

  // --- Data Clearing Handlers ---

  /** Clears all favorite trials. */
  const clearFavoriteTrials = () => setFavoriteTrialsList([]);

  /** Clears all saved searches. */
  const clearSavedSearches = () => setSavedSearchesList([]);

  /** Clears all trial applications. */
  const clearTrialApplications = () => setAppliedTrialsList([]);

  /**
   * Clears recent search history from session storage.
   * If on the dashboard, uses a special trigger value to signal a history clear event.
   */
  const clearRecentSearchHistory = () => {
    sessionStorage.removeItem('recentSearchesHistory');
    sessionStorage.removeItem('recentPatientIdsForSearch');
    if (activeView === VIEWS.DASHBOARD) {
      setInitialSearchTermForDashboard(CLEAR_HISTORY_TRIGGER_VALUE);
    }
  };

  /** Marks all notifications as read. */
  const clearAllNotifications = () => {
    const allReadNotifications = notifications.map(n => ({ ...n, read: true }));
    setNotifications(allReadNotifications);
  };

  /**
   * Toggles the read/unread status of a specific notification.
   * @param {string} notificationId - The ID of the notification to toggle.
   */
  const handleMarkAsReadToggle = (notificationId) => {
    setNotifications(prevNotifications =>
      prevNotifications.map(notif =>
        notif.id === notificationId ? { ...notif, read: !notif.read } : notif
      )
    );
  };

  /**
   * Handles user logout.
   * Clears all session-related data (favorites, searches, applications, history, notifications)
   * and resets overview statistics and view to default.
   */
  const handleLogout = () => {
    if (window.confirm("Are you sure you want to 'logout'? This will clear all your session data.")) {
      clearFavoriteTrials();
      clearSavedSearches();
      clearRecentSearchHistory(); // Clears session storage items directly
      clearTrialApplications();

      // Reset notifications to initial unread state
      const resetNotifications = initialMockNotifications.map(n => ({ ...n, read: false }));
      setNotifications(resetNotifications);

      // Reset overview stats, calculating unread notifications from the reset state
      const initialUnreadCount = resetNotifications.filter(n => !n.read).length;
      setOverviewStats(
        initialOverviewStatsTemplate.map(stat => ({
          ...stat,
          value: stat.key === 'unreadNotificationsCount' ? initialUnreadCount : 0,
        }))
      );

      setActiveView(VIEWS.DASHBOARD);
    }
  };

  // --- Navigation and UI Data ---
  const unreadNotificationsCount = notifications.filter(n => !n.read).length;

  const navItems = [
    { view: VIEWS.DASHBOARD, text: 'Dashboard', icon: <DashboardIconOriginal /> },
    { view: VIEWS.APPLICATIONS, text: 'Trial applications', icon: <AssessmentIcon /> },
    { view: VIEWS.FAVORITES, text: 'Favorite trials', icon: <FavoriteBorderIcon /> },
    { view: VIEWS.SAVED_SEARCHES, text: 'Saved searches', icon: <BookmarkBorderIcon /> },
    {
      view: VIEWS.NOTIFICATIONS,
      text: 'Notifications',
      icon: <NotificationsNoneIcon />,
      badge: unreadNotificationsCount > 0 ? unreadNotificationsCount : undefined,
    },
  ];

  const settingsHelpItems = [
    { view: VIEWS.SETTINGS, text: 'Settings', icon: <SettingsIcon /> },
    { view: VIEWS.HELP, text: 'Help center', icon: <HelpOutlineIcon /> },
    { view: VIEWS.BLOG, text: 'Blog', icon: <ArticleIcon /> },
  ];

  const explorePlatformItems = [
    {
      icon: <HelpOutlineIcon />,
      text: "Need help getting started?",
      action: "Contact us",
      link: "mailto:Phoenix.CoCExtreme@gmail.com?subject=Getting%20Started%20Help&body=Hi%2C%20I%20need%20help%20getting%20started.",
    },
    {
      icon: <FavoriteIcon />,
      text: "Understand your condition",
      action: "Coming soon",
      link: "#", // Placeholder link
      disabled: true,
    },
  ];


  /**
   * Renders the main content area based on the active view.
   * @returns {React.ReactElement} The JSX for the current view.
   */
  const renderMainContent = () => {
    // Pass initial search term only if dashboard is active and term exists
    const dashboardInitialSearch =
      activeView === VIEWS.DASHBOARD && initialSearchTermForDashboard
        ? initialSearchTermForDashboard
        : '';

    switch (activeView) {
      case VIEWS.DASHBOARD:
        return (
          <>
            <Box>
              <Typography variant="h4" component="h1" fontWeight="bold">
                Welcome, {mockUser.name.split(' ')[0]}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
                Here's what's happening on your clinical trial journey
              </Typography>
            </Box>
            <TrialSearchSection
              onSearchApplied={incrementTrialsAppliedCount}
              favoriteTrialsList={favoriteTrialsList}
              onToggleFavorite={toggleFavoriteTrial}
              onSaveSearch={handleSaveSearch}
              initialSearchTerm={dashboardInitialSearch}
              savedSearchesList={savedSearchesList}
              onApplyToTrial={handleApplyToTrial}
              appliedTrialsList={appliedTrialsList}
            />
          </>
        );
      case VIEWS.APPLICATIONS:
        return <TrialApplicationsPage appliedTrialsList={appliedTrialsList} />;
      case VIEWS.FAVORITES:
        return (
          <FavoriteTrialsDisplayPage
            favoriteTrialsList={favoriteTrialsList}
            onToggleFavorite={toggleFavoriteTrial}
          />
        );
      case VIEWS.SAVED_SEARCHES:
        return (
          <SavedSearchesPage
            savedSearchesList={savedSearchesList}
            onExecuteSavedSearch={executeSavedSearch}
            onRemoveSavedSearch={handleRemoveSavedSearch}
          />
        );
      case VIEWS.NOTIFICATIONS:
        return (
          <NotificationsPage
            notifications={notifications}
            onMarkAsReadToggle={handleMarkAsReadToggle}
            // onClearAllNotifications={clearAllNotifications} // Example: if needed by page
          />
        );
      case VIEWS.SETTINGS:
        return (
          <SettingsPage
            currentThemeMode={currentThemeMode}
            onThemeChange={onThemeChange}
            onClearFavoriteTrials={clearFavoriteTrials}
            onClearSavedSearches={clearSavedSearches}
            onClearRecentSearchHistory={clearRecentSearchHistory}
            onClearTrialApplications={clearTrialApplications} // Pass this if SettingsPage handles it
            onClearAllNotifications={clearAllNotifications} // Pass this if SettingsPage handles it
          />
        );
      case VIEWS.HELP:
        return <HelpCenterPage />;
      case VIEWS.BLOG:
        return <BlogPage />;
      default:
        return <Typography>Page not found.</Typography>;
    }
  };

  // --- Component JSX ---
  return (
    <Box
      sx={{
        display: 'flex',
        width: '100%',
        minHeight: '100vh',
        bgcolor: theme.palette.background.default,
      }}
    >
      {/* Sidebar Navigation */}
      <Box
        component="nav"
        sx={{
          width: SIDEBAR_WIDTH,
          flexShrink: 0,
          bgcolor: theme.palette.background.paper,
          borderRight: `1px solid ${theme.palette.divider}`,
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center' }}>
          <Typography
            variant="h5"
            component="div"
            sx={{ fontWeight: 'bold', color: 'primary.main' }}
          >
            AI Clinical Trial Matching
          </Typography>
        </Box>

        <List sx={{ flexGrow: 1 }}>
          {navItems.map((item) => (
            <ListItem key={item.view} disablePadding>
              <StyledListItemButton
                active={activeView === item.view ? 1 : 0} // Using 1/0 as per original for 'active' prop
                onClick={() => handleViewChange(item.view)}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText primary={item.text} />
                {item.badge !== undefined && (
                  <Chip
                    label={item.badge}
                    color="primary"
                    size="small"
                    sx={{
                      height: 20,
                      fontSize: '0.7rem',
                      fontWeight: 'bold',
                    }}
                  />
                )}
              </StyledListItemButton>
            </ListItem>
          ))}
        </List>

        <Box>
          <Typography
            variant="caption"
            sx={{
              pl: 2.5,
              pb: 1,
              display: 'block',
              textTransform: 'uppercase',
              fontSize: '0.65rem',
              fontWeight: 'bold',
              color: 'text.secondary',
            }}
          >
            Settings & Help
          </Typography>
          <List>
            {settingsHelpItems.map((item) => (
              <ListItem key={item.view} disablePadding>
                <StyledListItemButton
                  active={activeView === item.view ? 1 : 0}
                  onClick={() => handleViewChange(item.view)}
                >
                  <ListItemIcon sx={{ minWidth: 40 }}>
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText primary={item.text} />
                </StyledListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>

        <Divider />

        <Tooltip title="Logout (Clear Session Data)" placement="right">
          <Box
            onClick={handleLogout}
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              },
            }}
          >
            <Avatar
              sx={{
                bgcolor: theme.palette.mode === 'dark'
                  ? theme.palette.primary.dark
                  : theme.palette.secondary.main,
                width: 32,
                height: 32,
                fontSize: '0.875rem',
                mr: 1.5,
              }}
            >
              {mockUser.initials}
            </Avatar>
            <ListItemText
              primary={mockUser.name}
              primaryTypographyProps={{
                variant: 'subtitle2',
                fontWeight: 'medium',
                color: 'text.primary',
              }}
              sx={{ m: 0, flexGrow: 1 }}
            />
            <LogoutIcon sx={{ color: 'action.active', ml: 1 }} />
          </Box>
        </Tooltip>
      </Box>

      {/* Main Content Area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: { xs: 2, md: 3 },
          display: 'flex',
          flexDirection: { xs: 'column', md: 'row' },
          gap: { xs: 2, md: 3 },
          overflowY: 'auto',
        }}
      >
        {/* Left part of Main Content (Dynamic Content) */}
        <Box
          sx={{
            flexGrow: { xs: 1, md: 2.5 },
            flexShrink: 1,
            flexBasis: '0%', // Ensures proper flex distribution
            display: 'flex',
            flexDirection: 'column',
            gap: { xs: 2, md: 3 },
            minWidth: 0, // Prevents overflow issues with flex items
            overflowX: 'hidden', // Prevents horizontal scroll in content area
          }}
        >
          {renderMainContent()}
        </Box>

        {/* Right Column (Overview and Explore) */}
        <Box
          sx={{
            flexGrow: { xs: 1, md: 1 },
            flexShrink: 1,
            flexBasis: { md: '320px' }, // Initial width for the right column on medium screens
            display: {
              xs: activeView === VIEWS.DASHBOARD ? 'flex' : 'none', // Show on mobile only for dashboard
              md: 'flex', // Always show on medium screens and up
            },
            flexDirection: 'column',
            gap: { xs: 2, md: 3 },
            minWidth: { xs: '100%', sm: 280, md: 300 },
            maxWidth: { xs: '100%', md: 400 },
          }}
        >
          <Paper
            elevation={0}
            sx={{
              p: 2.5,
              borderRadius: 2,
              bgcolor: theme.palette.background.paper,
            }}
          >
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Overview
            </Typography>
            {overviewStats.map(stat => (
              <Box
                key={stat.key}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  py: 1.5,
                  borderBottom: `1px solid ${theme.palette.divider}`,
                  '&:last-child': {
                    borderBottom: 'none',
                  },
                }}
              >
                <Box
                  sx={{
                    width: 4,
                    height: 32,
                    bgcolor: stat.color,
                    borderRadius: 1,
                    mr: 1.5,
                  }}
                />
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    {stat.label}
                  </Typography>
                  <Typography variant="h4" component="p" fontWeight="bold">
                    {stat.value}
                  </Typography>
                </Box>
              </Box>
            ))}
          </Paper>

          <Paper
            elevation={0}
            sx={{
              p: 2.5,
              borderRadius: 2,
              bgcolor: theme.palette.background.paper,
            }}
          >
            <Typography variant="h6" fontWeight="bold" gutterBottom>
              Explore platform
            </Typography>
            <List disablePadding>
              {explorePlatformItems.map(item => (
                <ListItem key={item.text} disablePadding sx={{ py: 1 }}>
                  <ListItemIcon
                    sx={{
                      minWidth: 36,
                      color: theme.palette.primary.main,
                    }}
                  >
                    {item.icon}
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    secondary={
                      <Link
                        href={item.link}
                        underline="none"
                        color="primary"
                        sx={{
                          fontSize: '0.875rem',
                          fontWeight: 'medium',
                          display: 'flex',
                          alignItems: 'center',
                        }}
                      >
                        {item.action}
                        {!item.disabled && (
                          <ArrowForwardIcon sx={{ fontSize: '1rem', ml: 0.5 }} />
                        )}
                      </Link>
                    }
                    primaryTypographyProps={{
                      fontWeight: 'medium',
                      fontSize: '0.9rem',
                    }}
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
}

/**
 * ClinicalTrialMatcher is the main application component that sets up
 * the global styles and renders the primary layout.
 *
 * @param {object} props - The component's props.
 * @param {string} props.currentThemeMode - The current theme mode ('light' or 'dark').
 * @param {function} props.onThemeChange - Callback function to change the theme mode.
 */
function ClinicalTrialMatcher({ currentThemeMode, onThemeChange }) {
  return (
    <>
      <CssBaseline />
      <DashboardLayout
        currentThemeMode={currentThemeMode}
        onThemeChange={onThemeChange}
      />
    </>
  );
}

export default ClinicalTrialMatcher;
