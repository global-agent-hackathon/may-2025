// frontend/src/components/TrialSearchSection.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid, // Grid is used for both container and items
  TextField,
  Button,
  CircularProgress,
  Alert,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import HistoryIcon from '@mui/icons-material/History';
import BookmarkAddIcon from '@mui/icons-material/BookmarkAdd';
import DynamicTrialCard from './DynamicTrialCard';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const MAX_RECENT_SEARCH_RESULTS_SETS = 2;
const MAX_RECENT_PATIENT_IDS = 5;

function TrialSearchSection({
  onSearchApplied,
  favoriteTrialsList,
  onToggleFavorite,
  onSaveSearch,
  initialSearchTerm,
  savedSearchesList = [],
  onApplyToTrial,
  appliedTrialsList = []
}) {
  // ... (all state and functions from the previous correct version remain identical)
  const [patientId, setPatientId] = useState(initialSearchTerm || '');
  const [isLoading, setIsLoading] = useState(false);
  const [currentSearchResults, setCurrentSearchResults] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [lastSearchedIdForHeader, setLastSearchedIdForHeader] = useState(initialSearchTerm || '');
  const [recentSearchesHistory, setRecentSearchesHistory] = useState(() => { const savedHistory = sessionStorage.getItem('recentSearchesHistory'); return savedHistory ? JSON.parse(savedHistory) : []; });
  const [recentPatientIds, setRecentPatientIds] = useState(() => { const saved = sessionStorage.getItem('recentPatientIdsForSearch'); return saved ? JSON.parse(saved) : []; });

  useEffect(() => { if (initialSearchTerm && initialSearchTerm !== lastSearchedIdForHeader && initialSearchTerm !== '__CLEAR_HISTORY_TRIGGER__') { handleSearchSubmit(initialSearchTerm, true); } else if (initialSearchTerm === '__CLEAR_HISTORY_TRIGGER__') { setRecentSearchesHistory([]); setRecentPatientIds([]); } /* eslint-disable-next-line react-hooks/exhaustive-deps */ }, [initialSearchTerm]);
  useEffect(() => { sessionStorage.setItem('recentSearchesHistory', JSON.stringify(recentSearchesHistory)); }, [recentSearchesHistory]);
  useEffect(() => { sessionStorage.setItem('recentPatientIdsForSearch', JSON.stringify(recentPatientIds)); }, [recentPatientIds]);

  const addSearchToHistoryAndRecents = (searchedId, resultsOfSearch) => { setRecentPatientIds(prevIds => { const lowerId = searchedId.toLowerCase(); const filtered = prevIds.filter(id => id.toLowerCase() !== lowerId); const newIds = [searchedId, ...filtered]; return newIds.slice(0, MAX_RECENT_PATIENT_IDS); }); setRecentSearchesHistory(prevHistory => { const newHistoryEntry = { patientId: searchedId, results: resultsOfSearch, timestamp: Date.now() }; const filteredHistory = prevHistory.filter(entry => entry.patientId.toLowerCase() !== searchedId.toLowerCase()); const updatedHistory = [newHistoryEntry, ...filteredHistory]; return updatedHistory.slice(0, MAX_RECENT_SEARCH_RESULTS_SETS); }); };
  const handleActualApiSearch = async (searchIdToSubmit, isProgrammaticSearch = false) => { setIsLoading(true); setError(null); setCurrentSearchResults(null); setMessage(null); if (!isProgrammaticSearch) { setPatientId(searchIdToSubmit); } setLastSearchedIdForHeader(searchIdToSubmit.trim()); try { const response = await fetch(`${API_URL}/api/v1/trials/find`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patientId: searchIdToSubmit.trim() }), }); const data = await response.json(); if (!response.ok) { const errorDetail = data.detail || `Request failed with status: ${response.status}`; throw new Error(typeof errorDetail === 'string' ? errorDetail : JSON.stringify(errorDetail)); } if (onSearchApplied) { onSearchApplied(); } const trialsData = data.matches || []; setCurrentSearchResults(trialsData); addSearchToHistoryAndRecents(searchIdToSubmit.trim(), trialsData); if (data.status === "success" && trialsData.length > 0) {} else if (data.status === "success" && trialsData.length === 0) { setMessage(`Search for ${searchIdToSubmit} successful, but no trials matched the criteria.`); } else if (data.status === "no_matches_found") { setMessage(data.message || `No suitable recruiting trials found for ${searchIdToSubmit}.`); } else { throw new Error(data.message || 'Received an unexpected response structure from the server.'); } } catch (err) { console.error("API Error:", err); setError(err.message || 'Failed to fetch trial data. Please check your connection or contact support.'); setCurrentSearchResults(null); } finally { setIsLoading(false); } };
  const handleSearchSubmit = (idToSearch, isProgrammaticSearch = false) => { if (!idToSearch || !idToSearch.trim()) { setError('Please enter a Patient ID.'); setCurrentSearchResults(null); setMessage(null); return; } if (!isProgrammaticSearch || (isProgrammaticSearch && initialSearchTerm !== idToSearch)) { setPatientId(idToSearch); } handleActualApiSearch(idToSearch, isProgrammaticSearch); }
  const onFormSubmit = (event) => { event.preventDefault(); handleSearchSubmit(patientId); };
  const handleSaveSearchClick = () => { if (patientId.trim() && onSaveSearch) { onSaveSearch(patientId.trim()); } };
  const isSearchSaved = patientId.trim() && savedSearchesList.includes(patientId.trim());

  return (
    <Paper elevation={0} sx={{ p: { xs: 1.5, sm: 2.5 }, borderRadius: 2, bgcolor: 'transparent' }}>
      {/* Search Form Section */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
        <Typography variant="h6" fontWeight="bold">Find Clinical Trials</Typography>
      </Box>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
        Enter a Patient ID to find potentially matching clinical trials.
      </Typography>

      <Box sx={{ mb: 2.5 }}>
        <Box
          component="form"
          onSubmit={onFormSubmit}
          sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, gap: 2, alignItems: 'center' }}
        >
          <TextField
            label="Patient ID"
            variant="outlined"
            value={patientId}
            onChange={(e) => { setPatientId(e.target.value); }}
            disabled={isLoading}
            fullWidth
            placeholder="e.g., PATIENT_001"
            sx={{ maxWidth: { sm: 400 }, flexGrow: {sm: 1} }}
            onFocus={() => { setError(null); setMessage(null); setCurrentSearchResults(null); }}
          />
          <Button
            type="submit"
            variant="contained"
            color="primary"
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
            sx={{ minWidth: 150, height: 56, width: {xs: '100%', sm: 'auto'} }}
          >
            {isLoading ? 'Searching...' : 'Search Trials'}
          </Button>
        </Box>
        {patientId.trim() && onSaveSearch && (
          <Box sx={{ display: 'flex', justifyContent: 'flex-start', mt: 1 }}>
            <Button
              onClick={handleSaveSearchClick}
              variant="text"
              size="small"
              startIcon={<BookmarkAddIcon />}
              disabled={isSearchSaved || isLoading}
              sx={{ textTransform: 'none' }}
            >
              {isSearchSaved ? 'Search Saved' : 'Save Search'}
            </Button>
          </Box>
        )}
      </Box>

      {/* Feedback Messages for Current Search */}
      {error && ( <Alert severity="error" sx={{ mb: 2.5, borderRadius: 2 }}>{error}</Alert> )}
      {message && (!currentSearchResults || currentSearchResults.length === 0) && ( <Alert severity="info" sx={{ mb: 2.5, borderRadius: 2 }}>{message}</Alert> )}
      {isLoading && ( <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}><CircularProgress /></Box> )}

      {/* Current Search Results Display */}
      {!isLoading && currentSearchResults && currentSearchResults.length > 0 && (
        <Box sx={{mb: 4}}>
          <Typography variant="h6" component="h2" fontWeight="medium" sx={{ mt: 1, mb: 2 }}>
            Displaying Matches ({currentSearchResults.length}) for {lastSearchedIdForHeader}
          </Typography>
          <Grid container spacing={2.5}>
            {currentSearchResults.map((trial) => (
              // Grid v2: No 'item' prop. xs, sm, md directly define column span.
              <Grid xs={12} sm={6} md={6} key={`${lastSearchedIdForHeader}-curr-${trial.id}`}>
                <DynamicTrialCard
                  trial={trial}
                  favoriteTrialsList={favoriteTrialsList}
                  onToggleFavorite={onToggleFavorite}
                  onApplyToTrial={onApplyToTrial}
                  appliedTrialsList={appliedTrialsList}
                />
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
      
      {/* Initial Empty State */}
      {!isLoading && !error && currentSearchResults === null && !message && !initialSearchTerm && recentSearchesHistory.length === 0 && (
        <Paper elevation={0} sx={{ p: 3, borderRadius: 2, bgcolor: 'action.hover', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center', minHeight: 150, mt: 2, mb: 3 }}>
          <SearchIcon sx={{ fontSize: 40, color: 'text.secondary', mb:1 }}/>
          <Typography variant="subtitle1" fontWeight="medium" color="text.secondary">
              Enter a Patient ID above to begin your search.
          </Typography>
          <Typography variant="body2" color="text.disabled">
              Mock Patient IDs: PATIENT_001, PATIENT_002, PATIENT_NO_MATCH, PATIENT_ERROR
          </Typography>
        </Paper>
      )}

      {/* Recent Searches History Display */}
      {recentSearchesHistory.length > 0 && (
        <Box sx={{ mt: (currentSearchResults && currentSearchResults.length > 0) ? 4 : 2, pt: 2, borderTop: '1px solid', borderColor: 'divider' }}>
          <Typography variant="h6" fontWeight="medium" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
            <HistoryIcon sx={{ mr: 1, color: 'text.secondary' }} />
            Recent Search Results
          </Typography>
          {recentSearchesHistory.map((historyEntry, index) => (
            <Box key={`${historyEntry.patientId}-${historyEntry.timestamp}`} sx={{ mb: 3 }}>
              <Box sx={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1.5}}>
                <Typography variant="subtitle1" >
                  Results for Patient ID: <strong>{historyEntry.patientId}</strong>
                </Typography>
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => handleSearchSubmit(historyEntry.patientId, true)}
                  sx={{ textTransform: 'none' }}
                >
                  Re-run Search
                </Button>
              </Box>
              {historyEntry.results.length > 0 ? (
                <Grid container spacing={2.5}>
                  {historyEntry.results.map((trial) => (
                    // Grid v2: No 'item' prop. xs, sm, md directly define column span.
                    <Grid xs={12} sm={6} md={6} key={`${historyEntry.patientId}-hist-${trial.id}`}>
                      <DynamicTrialCard
                        trial={trial}
                        favoriteTrialsList={favoriteTrialsList}
                        onToggleFavorite={onToggleFavorite}
                        onApplyToTrial={onApplyToTrial}
                        appliedTrialsList={appliedTrialsList}
                      />
                    </Grid>
                  ))}
                </Grid>
              ) : (
                <Typography variant="body2" color="text.secondary" sx={{pl:0.5}}>
                  No trials were found for this patient in that search.
                </Typography>
              )}
              {index < recentSearchesHistory.length -1 && <Box sx={{height: '1px', bgcolor: 'divider', my: 3}}/>}
            </Box>
          ))}
        </Box>
      )}
    </Paper>
  );
}

export default TrialSearchSection;