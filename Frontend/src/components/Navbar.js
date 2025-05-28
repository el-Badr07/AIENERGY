import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box, useTheme } from '@mui/material';
import BoltIcon from '@mui/icons-material/Bolt';
import { Link, useLocation } from 'react-router-dom';

export default function Navbar() {
  const location = useLocation();
  const theme = useTheme();
  return (
    <AppBar
      position="static"
      elevation={2}
      sx={{
        background: 'linear-gradient(90deg, #1976d2 60%, #43a047 100%)',
        borderRadius: '0 0 18px 18px',
        boxShadow: '0 4px 16px 0 rgba(25,118,210,0.10)',
        mb: 3,
        px: 2
      }}
    >
      <Toolbar sx={{ minHeight: 72 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <BoltIcon sx={{ fontSize: 36, color: '#ffe082', mr: 1 }} />
          <Typography
            variant="h4"
            component={Link}
            to="/invoices"
            sx={{
              fontWeight: 800,
              textDecoration: 'none',
              color: 'white',
              letterSpacing: 2,
              textShadow: '1px 1px 6px #1976d2',
              mr: 3
            }}
          >
            AIENERGY
          </Typography>
        </Box>
        <Box>
          <Button
            component={Link}
            to="/dashboard"
            sx={{
              mr: 2,
              fontWeight: 600,
              color: location.pathname.startsWith('/dashboard') ? '#fff' : '#e3f2fd',
              background: location.pathname.startsWith('/dashboard') ? 'rgba(2,136,209,0.18)' : 'transparent',
              borderRadius: 2,
              px: 3,
              boxShadow: location.pathname.startsWith('/dashboard') ? '0 2px 8px 0 rgba(2,136,209,0.08)' : 'none',
              transition: 'all 0.2s',
              '&:hover': {
                background: 'rgba(2,136,209,0.28)',
                color: '#fff',
              },
            }}
          >
            Dashboard
          </Button>
          <Button
            component={Link}
            to="/invoices"
            sx={{
              mr: 2,
              fontWeight: 600,
              color: location.pathname.startsWith('/invoices') ? '#fff' : '#e3f2fd',
              background: location.pathname.startsWith('/invoices') ? 'rgba(25,118,210,0.18)' : 'transparent',
              borderRadius: 2,
              px: 3,
              boxShadow: location.pathname.startsWith('/invoices') ? '0 2px 8px 0 rgba(25,118,210,0.08)' : 'none',
              transition: 'all 0.2s',
              '&:hover': {
                background: 'rgba(25,118,210,0.28)',
                color: '#fff',
              },
            }}
          >
            Factures
          </Button>
          <Button
            component={Link}
            to="/upload"
            sx={{
              fontWeight: 600,
              color: location.pathname === '/upload' ? '#fff' : '#e3f2fd',
              background: location.pathname === '/upload' ? 'rgba(67,160,71,0.18)' : 'transparent',
              borderRadius: 2,
              px: 3,
              boxShadow: location.pathname === '/upload' ? '0 2px 8px 0 rgba(67,160,71,0.08)' : 'none',
              transition: 'all 0.2s',
              '&:hover': {
                background: 'rgba(67,160,71,0.28)',
                color: '#fff',
              },
            }}
          >
            Importer
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
