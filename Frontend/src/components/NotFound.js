import React from 'react';
import { Typography, Box, Button } from '@mui/material';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <Box sx={{ mt: 8, textAlign: 'center' }}>
      <Typography variant="h3" color="primary" gutterBottom>
        404
      </Typography>
      <Typography variant="h5" gutterBottom>
        Page non trouvée
      </Typography>
      <Button variant="contained" color="primary" component={Link} to="/invoices" sx={{ mt: 2 }}>
        Retour à l'accueil
      </Button>
    </Box>
  );
}
