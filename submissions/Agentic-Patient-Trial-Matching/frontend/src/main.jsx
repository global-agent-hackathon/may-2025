import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import CssBaseline from '@mui/material/CssBaseline';
// Optional: Import ThemeProvider if you want to customize the theme later
// import { ThemeProvider, createTheme } from '@mui/material/styles';

// Optional: Define a custom theme
// const theme = createTheme({
//   palette: {
//     primary: {
//       main: '#1976d2', // Example primary color
//     },
//   },
// });


createRoot(document.getElementById('root')).render(
  <StrictMode>
    {/* <ThemeProvider theme={theme}> */}
    <CssBaseline /> {/* Apply baseline normalization */}
    <App />
    {/* </ThemeProvider> */}
  </StrictMode>,
)
