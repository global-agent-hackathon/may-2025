import React, { useState } from 'react';
import { logger } from './utils/logger';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import Alert from '@mui/material/Alert';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Chip from '@mui/material/Chip';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import Link from '@mui/material/Link';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import ContactPhoneIcon from '@mui/icons-material/ContactPhone';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function ClinicalTrialMatcher() {
  const [patientId, setPatientId] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!patientId.trim()) {
      logger.warn('Empty patient ID submitted');
      setError('Please enter a Patient ID.');
      setResults(null);
      setMessage(null);
      return;
    }

    logger.info(`Initiating trial search for patient ID: ${patientId}`);
    setIsLoading(true);
    setError(null);
    setResults(null);
    setMessage(null);

    try {
      logger.debug(`Making API request to ${API_URL}/api/v1/trials/find`);
      const response = await fetch(`${API_URL}/api/v1/trials/find`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ patientId: patientId.trim() }),
      });

      if (!response.ok) {
        let errorDetail = `Request failed! Status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorDetail;
        } catch (parseError) {
          logger.error('Failed to parse error response', parseError);
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();
      logger.debug('Received response:', data);

      if (data.status === 'success') {
        logger.info(`Found ${data.matches?.length || 0} matches for patient ${patientId}`);
        setResults(data.matches);
        if (data.matches?.length === 0) {
          logger.info('No trials matched the criteria');
          setMessage('Search successful, but no trials matched the criteria.');
        }
      } else if (data.status === 'no_matches_found') {
        logger.info('No matches found response received');
        setMessage(data.message || 'No suitable recruiting trials found.');
        setResults([]);
      } else {
        logger.warn(`Unexpected status received: ${data.status}`);
        throw new Error(data.message || 'Received an unexpected status from server.');
      }
    } catch (err) {
      logger.error('Error during trial search:', err);
      setError(err.message || 'Failed to fetch trial data. Check connection or contact support.');
    } finally {
      setIsLoading(false);
      logger.debug('Search request completed');
    }
  };

  return (
    <Card 
      sx={{ 
        width: '100%',
        borderRadius: 2,
        bgcolor: 'background.paper',
        boxShadow: (theme) => theme.shadows[3],
        overflow: 'hidden'
      }}
    >
      <CardContent sx={{ p: 4 }}>
        <Typography 
          variant="h4" 
          component="h1" 
          gutterBottom 
          align="center"
          sx={{
            mb: 4,
            fontWeight: 600,
            background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent'
          }}
        >
          Clinical Trial Matcher
        </Typography>
        
        <Box
          component="form"
          onSubmit={handleSubmit}
          sx={{ 
            display: 'flex', 
            flexDirection: 'column', 
            gap: 3,
            alignItems: 'center',
            mb: 4
          }}
        >
          <TextField
            label="Patient ID"
            variant="outlined"
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            disabled={isLoading}
            fullWidth
            placeholder="e.g., PATIENT_001"
            sx={{ maxWidth: 400 }}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} color="inherit" /> : <SearchIcon />}
            sx={{ 
              minWidth: 160,
              height: 48,
              borderRadius: 2,
              textTransform: 'none',
              fontSize: '1rem'
            }}
          >
            {isLoading ? 'Searching...' : 'Search Trials'}
          </Button>
        </Box>

        {error && (
          <Alert 
            severity="error" 
            sx={{ 
              mb: 3,
              borderRadius: 2
            }}
          >
            {error}
          </Alert>
        )}
        {message && (
          <Alert 
            severity="info"
            sx={{ 
              mb: 3,
              borderRadius: 2
            }}
          >
            {message}
          </Alert>
        )}
        {isLoading && !error && !message && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
            <CircularProgress size={40} />
          </Box>
        )}

        {results && results.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography 
              variant="h5" 
              component="h2" 
              gutterBottom
              sx={{ 
                mb: 3,
                fontWeight: 600,
                color: 'text.primary'
              }}
            >
              Potential Matches
            </Typography>
            <List sx={{ p: 0 }}>
              {results.map((trial) => (
                <Card 
                  key={trial.id} 
                  sx={{ 
                    mb: 2,
                    borderRadius: 2,
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: (theme) => theme.shadows[4]
                    }
                  }} 
                  variant="outlined"
                >
                  <CardContent sx={{ p: 3 }}>
                    <Typography variant="h6" component="div" gutterBottom>
                      {trial.title} ({trial.id})
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                      <Chip
                        label={trial.status}
                        color={trial.status === 'Recruiting' ? 'success' : 'default'}
                        size="small"
                      />
                      <Chip label={`Phase: ${trial.phase}`} variant="outlined" size="small" />
                      <Chip label={`Condition: ${trial.condition}`} variant="outlined" size="small" />
                    </Box>
                    {trial.locations && trial.locations.length > 0 && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}
                      >
                        <LocationOnIcon fontSize="small" /> Locations: {trial.locations.join(', ')}
                      </Typography>
                    )}
                    {trial.contactInfo && (
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}
                      >
                        <ContactPhoneIcon fontSize="small" /> Contact: {trial.contactInfo}
                      </Typography>
                    )}
                    {trial.detailsUrl && (
                      <Typography variant="body2" sx={{ mb: 2 }}>
                        <Link
                          href={trial.detailsUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          underline="hover"
                        >
                          View Full Details on Registry
                        </Link>
                      </Typography>
                    )}
                    {trial.matchRationale && trial.matchRationale.length > 0 && (
                      <Box sx={{ mb: 1 }}>
                        <Typography variant="subtitle2">Match Rationale:</Typography>
                        <List dense disablePadding>
                          {trial.matchRationale.map((reason, index) => (
                            <ListItem key={`rationale-${index}`} disableGutters sx={{ py: 0.2 }}>
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                <CheckCircleOutlineIcon color="success" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText
                                primary={reason}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                    {trial.flags && trial.flags.length > 0 && (
                      <Box>
                        <Typography variant="subtitle2">Flags / Potential Issues:</Typography>
                        <List dense disablePadding>
                          {trial.flags.map((flag, index) => (
                            <ListItem key={`flag-${index}`} disableGutters sx={{ py: 0.2 }}>
                              <ListItemIcon sx={{ minWidth: 32 }}>
                                <WarningAmberIcon color="warning" fontSize="small" />
                              </ListItemIcon>
                              <ListItemText
                                primary={flag}
                                primaryTypographyProps={{ variant: 'body2' }}
                              />
                            </ListItem>
                          ))}
                        </List>
                      </Box>
                    )}
                  </CardContent>
                </Card>
              ))}
            </List>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default ClinicalTrialMatcher;