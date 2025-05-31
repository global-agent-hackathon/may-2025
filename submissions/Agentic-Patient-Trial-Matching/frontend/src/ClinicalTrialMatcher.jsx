// frontend/src/ClinicalTrialMatcher.jsx
import React, { useState, useEffect } from 'react';
import {
  Box, Grid, Typography, Paper, List, ListItem, ListItemButton,
  ListItemIcon, ListItemText, Avatar, Chip, Button, Link, Divider, Tooltip
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
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import FavoriteIcon from '@mui/icons-material/Favorite';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import LogoutIcon from '@mui/icons-material/Logout';
// Icons for mock notifications, to be used in initialMockNotifications
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
const MAX_SAVED_ITEMS = 10;
const mockUser = { name: 'Robert Maxwell', initials: 'RM' };
const VIEWS = {
  DASHBOARD: 'dashboard', APPLICATIONS: 'applications', FAVORITES: 'favorites',
  SAVED_SEARCHES: 'saved_searches', NOTIFICATIONS: 'notifications',
  SETTINGS: 'settings', HELP: 'help', BLOG: 'blog',
};

// Initial mock notifications - now defined here
const initialMockNotifications = [
  { id: 'notif1', type: 'New Feature', icon: <NewReleasesIcon color="primary" />, title: "Advanced Search Filters Implemented!", message: "Explore more precise trial matching...", timestamp: "2025-05-31T10:00:00Z", read: false, },
  { id: 'notif2', type: 'Application Update', icon: <CheckCircleIcon color="success" />, title: "Application for NCT01234567 Status Update", message: "Your simulated application for trial NCT01234567 has been 'Reviewed'.", timestamp: "2025-05-30T14:30:00Z", read: true, },
  { id: 'notif3', type: 'System Maintenance', icon: <WarningIcon color="warning" />, title: "Scheduled Maintenance Upcoming", message: "AI Clinical Trial Matching will undergo scheduled maintenance on June 5th...", timestamp: "2025-05-29T09:15:00Z", read: false, },
  { id: 'notif4', type: 'New Blog Post', icon: <InfoIcon color="info" />, title: "Read Our Latest Blog: 'Understanding Clinical Trial Phases'", message: "A new article has been published on our blog...", timestamp: "2025-05-28T16:00:00Z", read: true, },
  { id: 'notif5', type: 'Tip', icon: <HelpOutlineIcon color="action" />, title: "Tip: Save Your Searches!", message: "Don't forget you can save your frequent Patient ID searches...", timestamp: "2025-05-27T11:00:00Z", read: false, }
];


const initialOverviewStatsTemplate = [ // Template for resetting stats
    { label: 'Trials applied (Searches)', value: 0, color: 'primary.main', key: 'trialsApplied' },
    { label: 'Favorite trials', value: 0, color: 'error.main', key: 'favoriteTrialsCount' },
    { label: 'Saved searches', value: 0, color: 'success.main', key: 'savedSearchesCount' },
    { label: 'Applications Submitted', value: 0, color: 'info.main', key: 'applicationsSubmittedCount' },
    { label: 'Unread Notifications', value: 0, color: 'secondary.main', key: 'unreadNotificationsCount' }, // Changed label
];

const StyledListItemButton = styled(ListItemButton, { /* ... same ... */
  shouldForwardProp: (prop) => prop !== 'active',
})(({ theme, active }) => ({ margin: theme.spacing(0.5, 1), borderRadius: theme.shape.borderRadius, color: theme.palette.text.secondary, '& .MuiListItemIcon-root': { color: theme.palette.action.active, }, ...(active && { backgroundColor: theme.palette.action.selected, color: theme.palette.primary.main, fontWeight: theme.typography.fontWeightMedium, '& .MuiListItemIcon-root': { color: theme.palette.primary.main, }, }), '&:hover': { backgroundColor: theme.palette.action.hover, color: theme.palette.text.primary, '& .MuiListItemIcon-root': { color: theme.palette.action.active, } },
}));


function DashboardLayout({ currentThemeMode, onThemeChange }) {
  const theme = useTheme();
  const [activeView, setActiveView] = useState(VIEWS.DASHBOARD);
  const [overviewStats, setOverviewStats] = useState(initialOverviewStatsTemplate); // Use template
  const [favoriteTrialsList, setFavoriteTrialsList] = useState(() => JSON.parse(sessionStorage.getItem('favoriteClinicalTrials')) || []);
  const [savedSearchesList, setSavedSearchesList] = useState(() => JSON.parse(sessionStorage.getItem('savedClinicalSearches')) || []);
  const [initialSearchTermForDashboard, setInitialSearchTermForDashboard] = useState('');
  const [appliedTrialsList, setAppliedTrialsList] = useState(() => JSON.parse(sessionStorage.getItem('appliedClinicalTrials')) || []);

  // Notifications state lifted here
  const [notifications, setNotifications] = useState(() => {
    const savedNotifications = sessionStorage.getItem('userNotifications');
    return savedNotifications ? JSON.parse(savedNotifications) : initialMockNotifications;
  });

  // --- useEffect Hooks ---
  useEffect(() => { sessionStorage.setItem('favoriteClinicalTrials', JSON.stringify(favoriteTrialsList)); setOverviewStats(prev => prev.map(s => s.key === 'favoriteTrialsCount' ? {...s, value: favoriteTrialsList.length} : s)); }, [favoriteTrialsList]);
  useEffect(() => { sessionStorage.setItem('savedClinicalSearches', JSON.stringify(savedSearchesList)); setOverviewStats(prev => prev.map(s => s.key === 'savedSearchesCount' ? {...s, value: savedSearchesList.length} : s)); }, [savedSearchesList]);
  useEffect(() => { sessionStorage.setItem('appliedClinicalTrials', JSON.stringify(appliedTrialsList)); setOverviewStats(prev => prev.map(s => s.key === 'applicationsSubmittedCount' ? {...s, value: appliedTrialsList.length} : s)); }, [appliedTrialsList]);
  useEffect(() => { if (initialSearchTermForDashboard && activeView === VIEWS.DASHBOARD) { if (initialSearchTermForDashboard !== '__CLEAR_HISTORY_TRIGGER__') {} const timer = setTimeout(() => { setInitialSearchTermForDashboard(''); }, 50); return () => clearTimeout(timer); } }, [initialSearchTermForDashboard, activeView]);

  // useEffect for notifications: update overview and badge
  useEffect(() => {
    sessionStorage.setItem('userNotifications', JSON.stringify(notifications));
    const unreadCount = notifications.filter(n => !n.read).length;
    setOverviewStats(prevStats =>
      prevStats.map(stat =>
        stat.key === 'unreadNotificationsCount' ? { ...stat, value: unreadCount } : stat
      )
    );
    // This will update navItems which is defined below, so we need to ensure navItems is also state or re-rendered
  }, [notifications]);


  // --- Handlers ---
  const handleViewChange = (view) => { setActiveView(view); if (view !== VIEWS.DASHBOARD && initialSearchTermForDashboard) { setInitialSearchTermForDashboard(''); } };
  const incrementTrialsAppliedCount = () => { setOverviewStats(prev => prev.map(s => s.key === 'trialsApplied' ? { ...s, value: s.value + 1 } : s)); };
  const toggleFavoriteTrial = (trialToToggle) => { setFavoriteTrialsList(prev => { const isFav = prev.some(f => f.id === trialToToggle.id); if (isFav) return prev.filter(f => f.id !== trialToToggle.id); const updated = [trialToToggle, ...prev.filter(f => f.id !== trialToToggle.id)]; return updated.slice(0, MAX_SAVED_ITEMS); }); };
  const handleSaveSearch = (searchTerm) => { if (searchTerm && !savedSearchesList.includes(searchTerm)) { setSavedSearchesList(prev => [searchTerm, ...prev.filter(s => s !== searchTerm)].slice(0, MAX_SAVED_ITEMS)); } };
  const handleRemoveSavedSearch = (searchTerm) => { setSavedSearchesList(prev => prev.filter(s => s !== searchTerm)); };
  const executeSavedSearch = (searchTerm) => { setInitialSearchTermForDashboard(searchTerm); setActiveView(VIEWS.DASHBOARD); };
  const handleApplyToTrial = (trialToApply) => { setAppliedTrialsList(prev => { if (!prev.some(a => a.id === trialToApply.id)) { const app = { ...trialToApply, applicationStatus: "Applied", applicationDate: new Date().toISOString() }; return [app, ...prev].slice(0, MAX_SAVED_ITEMS); } return prev; }); };

  // Data Clearing
  const clearFavoriteTrials = () => setFavoriteTrialsList([]);
  const clearSavedSearches = () => setSavedSearchesList([]);
  const clearTrialApplications = () => setAppliedTrialsList([]);
  const clearRecentSearchHistory = () => { sessionStorage.removeItem('recentSearchesHistory'); sessionStorage.removeItem('recentPatientIdsForSearch'); if (activeView === VIEWS.DASHBOARD) { setInitialSearchTermForDashboard('__CLEAR_HISTORY_TRIGGER__'); } };
  const clearAllNotifications = () => { // Could be added to settings
    const allRead = notifications.map(n => ({ ...n, read: true }));
    setNotifications(allRead);
  };


  // Mark notification as read/unread
  const handleMarkAsReadToggle = (notificationId) => {
    setNotifications(prevNotifications =>
      prevNotifications.map(notif =>
        notif.id === notificationId ? { ...notif, read: !notif.read } : notif
      )
    );
  };

  const handleLogout = () => {
    if (window.confirm("Are you sure you want to 'logout'? This will clear all your session data.")) {
      clearFavoriteTrials(); clearSavedSearches(); clearRecentSearchHistory(); clearTrialApplications();
      setNotifications(initialMockNotifications.map(n => ({...n, read: false }))); // Reset notifications to initial unread state
      setOverviewStats(initialOverviewStatsTemplate.map(s => ({...s, value: s.key === 'unreadNotificationsCount' ? initialMockNotifications.filter(n=>!n.read).length : 0 })));
      setActiveView(VIEWS.DASHBOARD);
    }
  };

  // Navigation items - badge for notifications is now dynamic
  const unreadNotificationsCount = notifications.filter(n => !n.read).length;
  const navItems = [
    { view: VIEWS.DASHBOARD, text: 'Dashboard', icon: <DashboardIconOriginal /> },
    { view: VIEWS.APPLICATIONS, text: 'Trial applications', icon: <AssessmentIcon /> },
    { view: VIEWS.FAVORITES, text: 'Favorite trials', icon: <FavoriteBorderIcon /> },
    { view: VIEWS.SAVED_SEARCHES, text: 'Saved searches', icon: <BookmarkBorderIcon /> },
    { view: VIEWS.NOTIFICATIONS, text: 'Notifications', icon: <NotificationsNoneIcon />, badge: unreadNotificationsCount > 0 ? unreadNotificationsCount : undefined },
  ];
  const settingsHelpItems = [ /* ... same ... */
    { view: VIEWS.SETTINGS, text: 'Settings', icon: <SettingsIcon /> }, { view: VIEWS.HELP, text: 'Help center', icon: <HelpOutlineIcon /> }, { view: VIEWS.BLOG, text: 'Blog', icon: <ArticleIcon /> },
  ];
  const explorePlatformItems = [ /* ... same ... */
      { icon: <HelpOutlineIcon />, text: "Need help getting started?", action: "Contact us", link: "#" }, { icon: <FavoriteIcon />, text: "Understand your condition", action: "Coming soon", link: "#", disabled: true },
  ];


  const renderMainContent = () => { /* ... pass notifications and handler to NotificationsPage ... */
    const dashboardInitialSearch = (activeView === VIEWS.DASHBOARD && initialSearchTermForDashboard) ? initialSearchTermForDashboard : '';
    switch (activeView) {
      case VIEWS.DASHBOARD: return (<> <Box><Typography variant="h4" component="h1" fontWeight="bold">Welcome, {mockUser.name.split(' ')[0]}</Typography><Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>Here's what's happening on your clinical trial journey</Typography></Box> <TrialSearchSection onSearchApplied={incrementTrialsAppliedCount} favoriteTrialsList={favoriteTrialsList} onToggleFavorite={toggleFavoriteTrial} onSaveSearch={handleSaveSearch} initialSearchTerm={dashboardInitialSearch} savedSearchesList={savedSearchesList} onApplyToTrial={handleApplyToTrial} appliedTrialsList={appliedTrialsList} /> </>);
      case VIEWS.APPLICATIONS: return <TrialApplicationsPage appliedTrialsList={appliedTrialsList} />;
      case VIEWS.FAVORITES: return ( <FavoriteTrialsDisplayPage favoriteTrialsList={favoriteTrialsList} onToggleFavorite={toggleFavoriteTrial} /> );
      case VIEWS.SAVED_SEARCHES: return ( <SavedSearchesPage savedSearchesList={savedSearchesList} onExecuteSavedSearch={executeSavedSearch} onRemoveSavedSearch={handleRemoveSavedSearch} /> );
      case VIEWS.NOTIFICATIONS:
        return <NotificationsPage notifications={notifications} onMarkAsReadToggle={handleMarkAsReadToggle} />;
      case VIEWS.SETTINGS: return ( <SettingsPage currentThemeMode={currentThemeMode} onThemeChange={onThemeChange} onClearFavoriteTrials={clearFavoriteTrials} onClearSavedSearches={clearSavedSearches} onClearRecentSearchHistory={clearRecentSearchHistory} /> ); // Consider adding onClearTrialApplications
      case VIEWS.HELP: return <HelpCenterPage />;
      case VIEWS.BLOG: return <BlogPage />;
      default: return <Typography>Page not found.</Typography>;
    }
  };

  // ... (JSX for Sidebar, Main Content Area, Right Column remains structurally the same) ...
  // Ensure Overview panel correctly maps `overviewStats` (which is now updated for notifications)
  return (
    <Box sx={{ display: 'flex', width: '100%', minHeight: '100vh', bgcolor: theme.palette.background.default }}>
      <Box component="nav" sx={{ width: SIDEBAR_WIDTH, flexShrink: 0, bgcolor: theme.palette.background.paper, borderRight: `1px solid ${theme.palette.divider}`, display: 'flex', flexDirection: 'column', }} >
        <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center' }}><Typography variant="h5" component="div" sx={{ fontWeight: 'bold', color: 'primary.main' }}>AI Clinical Trial Matching</Typography></Box>
        <List sx={{ flexGrow: 1 }}> {navItems.map((item) => ( <ListItem key={item.view} disablePadding><StyledListItemButton active={activeView === item.view ? 1 : 0} onClick={() => handleViewChange(item.view)}><ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon><ListItemText primary={item.text} />{item.badge !== undefined && ( <Chip label={item.badge} color="primary" size="small" sx={{ height: 20, fontSize: '0.7rem', fontWeight: 'bold' }}/> )}</StyledListItemButton></ListItem> ))} </List>
        <Box><Typography variant="caption" sx={{ pl: 2.5, pb: 1, display: 'block', textTransform: 'uppercase', fontSize: '0.65rem', fontWeight:'bold', color: 'text.secondary' }}>Settings & Help</Typography> <List> {settingsHelpItems.map((item) => ( <ListItem key={item.view} disablePadding><StyledListItemButton active={activeView === item.view ? 1 : 0} onClick={() => handleViewChange(item.view)}><ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon><ListItemText primary={item.text} /></StyledListItemButton></ListItem> ))} </List> </Box>
        <Divider />
        <Tooltip title="Logout (Clear Session Data)" placement="right"><Box onClick={handleLogout} sx={{ p: 2, display: 'flex', alignItems: 'center', cursor: 'pointer', '&:hover': { backgroundColor: theme.palette.action.hover, } }}><Avatar sx={{ bgcolor: theme.palette.mode === 'dark' ? theme.palette.primary.dark : theme.palette.secondary.main, width: 32, height: 32, fontSize: '0.875rem', mr: 1.5 }}>{mockUser.initials}</Avatar><ListItemText primary={mockUser.name} primaryTypographyProps={{ variant: 'subtitle2', fontWeight: 'medium', color: 'text.primary' }} sx={{m:0, flexGrow: 1 }} /><LogoutIcon sx={{ color: 'action.active', ml: 1 }} /></Box></Tooltip>
      </Box>
      <Box component="main" sx={{ flexGrow: 1, p: { xs: 2, md: 3 }, display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: { xs: 2, md: 3 }, overflowY: 'auto',}}>
        <Box sx={{ flexGrow: { xs: 1, md: 2.5 }, flexShrink: 1, flexBasis: '0%', display: 'flex', flexDirection: 'column', gap: { xs: 2, md: 3 }, minWidth: 0, overflowX: 'hidden', }}>{renderMainContent()}</Box>
        <Box sx={{ flexGrow: { xs: 1, md: 1 }, flexShrink: 1, flexBasis: { md: '320px' }, display: { xs: activeView === VIEWS.DASHBOARD ? 'flex' : 'none', md: 'flex' }, flexDirection: 'column', gap: { xs: 2, md: 3 }, minWidth: { xs: '100%', sm: 280, md: 300 }, maxWidth: { xs: '100%', md: 400 } }}>
          <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, bgcolor: theme.palette.background.paper }}><Typography variant="h6" fontWeight="bold" gutterBottom>Overview</Typography>{overviewStats.map(stat => ( <Box key={stat.key} sx={{ display: 'flex', alignItems: 'center', py: 1.5, borderBottom: `1px solid ${theme.palette.divider}`, '&:last-child': { borderBottom: 'none'} }}><Box sx={{ width: 4, height: 32, bgcolor: stat.color, borderRadius: 1, mr: 1.5 }} /><Box><Typography variant="body2" color="text.secondary">{stat.label}</Typography><Typography variant="h4" component="p" fontWeight="bold">{stat.value}</Typography></Box></Box> ))}</Paper>
          <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, bgcolor: theme.palette.background.paper }}><Typography variant="h6" fontWeight="bold" gutterBottom>Explore platform</Typography><List disablePadding>{explorePlatformItems.map(item => ( <ListItem key={item.text} disablePadding sx={{py: 1}}><ListItemIcon sx={{minWidth: 36, color: theme.palette.primary.main }}>{item.icon}</ListItemIcon><ListItemText primary={item.text} secondary={ <Link href={item.link} underline="none" color="primary" sx={{fontSize: '0.875rem', fontWeight:'medium', display:'flex', alignItems:'center'}}> {item.action} {!item.disabled && <ArrowForwardIcon sx={{fontSize: '1rem', ml: 0.5}}/>} </Link> } primaryTypographyProps={{fontWeight:'medium', fontSize: '0.9rem'}} /></ListItem> ))}</List></Paper>
        </Box>
      </Box>
    </Box>
  );
}

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