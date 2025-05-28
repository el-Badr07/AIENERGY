import React, { useEffect, useState } from 'react';
import { Box, Typography, Paper, List, ListItem, ListItemText, Divider, Button, CircularProgress, Alert } from '@mui/material';
import { Link } from 'react-router-dom';
import { getAllFullInvoices } from '../api/api';

export default function InvoiceList() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    getAllFullInvoices()
      .then(res => {
        // API returns an array of {invoice, analysis, recommendations}
        setInvoices(Array.isArray(res.data) ? res.data : []);
        setLoading(false);
      })
      .catch(() => {
        setError('Erreur lors du chargement des factures.');
        setLoading(false);
      });
  }, []);

  return (
    <Paper elevation={3} sx={{ p: 4, mt: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h5">Liste des factures</Typography>
        <Button component={Link} to="/upload" variant="contained" color="secondary">
          Nouvelle facture
        </Button>
      </Box>
      {loading && <CircularProgress />}
      {error && <Alert severity="error">{error}</Alert>}
      <Box display="flex" flexWrap="wrap" gap={3} justifyContent="flex-start">
        {invoices.length === 0 && !loading && (
          <Box width="100%" textAlign="center" mt={5}>
            <Box sx={{ fontSize: 64, color: '#d0d0d0', mb: 2 }}>📭</Box>
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Aucune facture disponible pour le moment.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Cliquez sur <b>Nouvelle facture</b> pour importer votre première redevance électrique.
            </Typography>
          </Box>
        )}
        {invoices.map((entry) => (
          <Paper
            key={entry.invoice?.id}
            elevation={4}
            sx={{ width: 330, minHeight: 180, p: 2, mb: 2, borderRadius: 3, position: 'relative', transition: '0.2s', '&:hover': { boxShadow: 8, borderColor: 'primary.main' } }}
            component={Link}
            to={`/invoices/${entry.invoice?.id}`}
            style={{ textDecoration: 'none', color: 'inherit' }}
          >
            <Box display="flex" alignItems="center" mb={1}>
              <Box sx={{ fontSize: 32, mr: 1, color: 'primary.main' }}>📄</Box>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                {entry.invoice?.provider ? (
                  <span title={entry.invoice.provider}>{entry.invoice.provider}</span>
                ) : (
                  <span style={{ color: '#bbb' }}>Fournisseur inconnu</span>
                )}
              </Typography>
            </Box>
            <Typography variant="subtitle2" color="text.secondary">
              Facture n° {entry.invoice?.invoice_number ? (
                <span title={entry.invoice.invoice_number}>{entry.invoice.invoice_number}</span>
              ) : entry.invoice?.id ? (
                <span>{entry.invoice.id}</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )}
            </Typography>
            <Typography variant="body2" sx={{ mt: 1 }}>
              Client : <b>{entry.invoice?.customer_name ? (
                <span title={entry.invoice.customer_name}>{entry.invoice.customer_name}</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )}</b>
            </Typography>
            <Typography variant="body2">
              Période : <b>{entry.invoice?.period_start ? (
                <span title={entry.invoice.period_start}>{entry.invoice.period_start}</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )} à {entry.invoice?.period_end ? (
                <span title={entry.invoice.period_end}>{entry.invoice.period_end}</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )}</b>
            </Typography>
            <Typography variant="body2">
              Montant : <b>{entry.invoice?.total_amount ? (
                <span title={entry.invoice.total_amount + ' Dhs'}>{entry.invoice.total_amount} Dhs</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )}</b>
            </Typography>
            <Typography variant="body2">
              Consommation : <b>{entry.invoice?.total_kwh ? (
                <span title={entry.invoice.total_kwh + ' kWh'}>{entry.invoice.total_kwh} kWh</span>
              ) : (
                <span style={{ color: '#bbb' }}>N/A</span>
              )}</b>
            </Typography>
            <Box sx={{ position: 'absolute', top: 10, right: 10 }}>
              <Button size="small" variant="outlined" color="secondary">Voir</Button>
            </Box>
          </Paper>
        ))}
      </Box>
    </Paper>
  );
}
