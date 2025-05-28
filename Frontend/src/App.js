import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box, Container } from '@mui/material';
import UploadInvoice from './components/InvoiceUpload';
import InvoiceList from './components/InvoiceList';
import InvoiceDetails from './components/InvoiceDetails';
import NotFound from './components/NotFound';
import Navbar from './components/Navbar';
import ThemeWrapper from './theme';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <ThemeWrapper>
      <Box sx={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #e3f2fd 0%, #f4f6f8 100%)',
        pb: 0,
        display: 'flex',
        flexDirection: 'column',
      }}>
        <Navbar />
        <Container maxWidth="lg" sx={{
          mt: 4,
          mb: 2,
          background: 'rgba(255,255,255,0.95)',
          borderRadius: 5,
          boxShadow: '0 6px 32px 0 rgba(25,118,210,0.06)',
          px: { xs: 1, sm: 4 },
          py: 4,
          flex: 1
        }}>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/invoices" element={<InvoiceList />} />
            <Route path="/upload" element={<UploadInvoice />} />
            <Route path="/invoices/:id" element={<InvoiceDetails />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Container>
        <Box sx={{ textAlign: 'center', py: 3, color: '#b0bec5', fontSize: 16 }}>
          © {new Date().getFullYear()} AIENERGY — Analyse intelligente des factures d'énergie
        </Box>
      </Box>
    </ThemeWrapper>
  );
}

export default App;
