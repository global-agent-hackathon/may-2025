// frontend/src/pages/HelpCenterPage.jsx
import React from 'react';
import {
  Typography,
  Box,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Link
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline'; // Main page icon
import ContactSupportIcon from '@mui/icons-material/ContactSupport';

const faqData = [
  {
    id: 'faq1',
    question: "How do I use the 'Find Clinical Trials' feature?",
    answer: "Simply navigate to the 'Dashboard'. In the 'Find Clinical Trials' section, enter a valid Patient ID into the text field and click the 'Search Trials' button. The system will then display any potentially matching clinical trials based on the mock patient data associated with that ID."
  },
  {
    id: 'faq2',
    question: "What do the 'Match Rationale' and 'Flags' on a trial card mean?",
    answer: "The 'Match Rationale' provides a list of reasons why the system considers the trial a potential match for the patient profile. 'Flags' highlight potential issues or criteria that might make the patient ineligible, or aspects that require further review with a healthcare professional. This is all based on a simulated analysis for demonstration purposes."
  },
  {
    id: 'faq3',
    question: "How do 'Favorite Trials' work?",
    answer: "When viewing trial search results, you can click the heart icon on any trial card to mark it as a favorite. These favorited trials will then appear in the 'Favorite Trials' section, accessible from the sidebar. This list is stored for your current browser session."
  },
  {
    id: 'faq4',
    question: "What are 'Saved Searches'?",
    answer: "If you frequently search for a specific Patient ID, you can click the 'Save Search' button (appears below the search input after typing an ID) on the Dashboard. This saves the Patient ID. You can then go to the 'Saved Searches' page from the sidebar to see your list of saved IDs and quickly re-run a search for any of them."
  },
  {
    id: 'faq5',
    question: "Are the recent searches and their results automatically updated?",
    answer: "The 'Recent Search Results' section on your Dashboard displays a snapshot of the results for your last two unique Patient ID searches. This displayed data is from when that search was performed. To get the absolute latest information for one of those Patient IDs, use the 'Re-run Search' button next to the historical results. Performing a new search for any Patient ID will always fetch the latest available data from our mock database."
  },
  {
    id: 'faq6',
    question: "Is the patient and trial data real?",
    answer: "No, all patient profiles and clinical trial data used in the 'AI Clinical Trial Matching' platform are mock (simulated) data for demonstration and development purposes only. It does not represent real individuals or actual clinical trials."
  },
  {
    id: 'faq7',
    question: "How is the 'Overview' panel updated?",
    answer: "The 'Overview' panel on the right side of the Dashboard dynamically updates based on your actions during the current session. 'Trials applied' increments each time you perform a search. 'Favorite trials' and 'Saved searches' counts reflect the number of items you've added to those respective lists."
  },
  {
    id: 'faq8',
    question: "Who can I contact for more help?",
    answer: "As this is a demonstration project, direct support is not available. However, you can review the 'Blog' section for more information about the platform's features. For real clinical trial information, always consult with healthcare professionals and refer to official clinical trial registries. If you have any questions about the demo itself, feel free to mail by clicking on the contact us link located at the right of the webpage."
  }
];

function HelpCenterPage() {
  const [expanded, setExpanded] = React.useState(false);

  const handleChange = (panel) => (event, isExpanded) => {
    setExpanded(isExpanded ? panel : false);
  };

  return (
    <Box>
      <Typography variant="h3" component="h1" gutterBottom sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <HelpOutlineIcon fontSize="inherit" sx={{ mr: 1.5, color: 'primary.main' }} />
        Help Center
      </Typography>
      <Typography variant="h6" color="text.secondary" sx={{ mb: 4 }}>
        Frequently Asked Questions about the AI Clinical Trial Matching platform.
      </Typography>

      <Paper variant="outlined" sx={{ p: {xs: 1, sm: 2} }}>
        {faqData.map((faqItem) => (
          <Accordion
            key={faqItem.id}
            expanded={expanded === faqItem.id}
            onChange={handleChange(faqItem.id)}
            sx={{ 
                '&:before': { display: 'none' }, // Remove default top border from MUI Accordion
                boxShadow: 'none',
                borderBottom: '1px solid',
                borderColor: 'divider',
                '&:last-child': { borderBottom: 'none' }
            }}
            disableGutters
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              aria-controls={`${faqItem.id}-content`}
              id={`${faqItem.id}-header`}
              sx={{ py: 1 }}
            >
              <Typography variant="subtitle1" fontWeight="medium">{faqItem.question}</Typography>
            </AccordionSummary>
            <AccordionDetails sx={{ backgroundColor: 'action.hover', borderTop: '1px dashed', borderColor: 'divider' }}>
              <Typography variant="body2" sx={{ lineHeight: 1.7 }}>
                {faqItem.answer}
              </Typography>
            </AccordionDetails>
          </Accordion>
        ))}
      </Paper>

      <Paper variant="outlined" sx={{ p: 3, mt: 4, textAlign: 'center', backgroundColor: 'background.default' }}>
        <ContactSupportIcon sx={{ fontSize: 40, color: 'primary.light', mb: 1 }} />
        <Typography variant="h6" gutterBottom>
          Still Need Help?
        </Typography>
        <Typography variant="body1" color="text.secondary">
          If you can't find the answer you're looking for, please refer to our project documentation or contact a conceptual administrator (this is a demo).
        </Typography>
        {/* <Button variant="contained" sx={{mt: 2}}>Contact Support (Demo)</Button> */}
      </Paper>
    </Box>
  );
}
export default HelpCenterPage;