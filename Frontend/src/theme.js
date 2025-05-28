import { createTheme, ThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import React from 'react';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      dark: '#004ba0',
      light: '#63a4ff',
    },
    secondary: {
      main: '#43a047',
      dark: '#00701a',
      light: '#76d275',
    },
    background: {
      default: 'linear-gradient(135deg, #f4f6f8 0%, #e3f2fd 100%)',
      paper: '#ffffff',
    },
    info: {
      main: '#0288d1',
    },
    error: {
      main: '#e53935',
    },
  },
  typography: {
    fontFamily: 'Montserrat, Roboto, Arial, sans-serif',
    h1: { fontFamily: 'Montserrat, Roboto, Arial, sans-serif', fontWeight: 800 },
    h2: { fontFamily: 'Montserrat, Roboto, Arial, sans-serif', fontWeight: 700 },
    h5: { fontWeight: 700 },
  },
  shape: {
    borderRadius: 18,
  },
  shadows: [
    'none',
    '0px 2px 8px 0px rgba(25, 118, 210, 0.08)',
    ...Array(23).fill('0px 2px 8px 0px rgba(25, 118, 210, 0.08)')
  ],
  transitions: {
    duration: {
      shortest: 150,
      shorter: 200,
      short: 250,
      standard: 300,
      complex: 375,
      enteringScreen: 225,
      leavingScreen: 195,
    },
  },
});

export default function ThemeWrapper({ children }) {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}
