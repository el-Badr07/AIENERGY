import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Box, Typography, Paper, Divider, Button, CircularProgress, Alert, Grid, Chip } from '@mui/material';
import { getInvoiceById, getRecommendations, getAnalysis, getFullInvoiceById } from '../api/api';
import Recommendations from './Recommendations';

export default function InvoiceDetails() {
  const { id } = useParams();
  const [invoice, setInvoice] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [analysisLoading, setAnalysisLoading] = useState(true);
  const [analysisError, setAnalysisError] = useState('');

  useEffect(() => {
    setLoading(true);
    setAnalysisLoading(true);
    
    // Use the new full invoice endpoint
    getFullInvoiceById(id)
      .then(res => {
        console.log('Full invoice data:', res.data);
        if (res.data && !res.data.error) {
          // Set all data from the full response
          setInvoice(res.data.invoice);
          setRecommendations(res.data.recommendations);
          setAnalysis(res.data.analysis);
          setLoading(false);
          setAnalysisLoading(false);
        } else {
          throw new Error('Invoice not found or invalid format');
        }
      })
      .catch((err) => {
        console.error('Error loading full invoice:', err);
        setError('Erreur lors du chargement des détails de la facture.');
        setLoading(false);
        setAnalysisLoading(false);
      });
  }, [id]);

  if (loading) return <CircularProgress sx={{ mt: 4 }} />;
  if (error) return <Alert severity="error">{error}</Alert>;
  if (!invoice) return <Typography>Aucune donnée pour cette facture.</Typography>;

  return (
    <Paper elevation={4} sx={{ p: 4, mt: 2, borderRadius: 4, background: '#f8fafc' }}>
      <Button component={Link} to="/invoices" variant="outlined" sx={{ mb: 2 }}>
        ← Retour à la liste
      </Button>
      <Box display="flex" alignItems="center" mb={2}>
        <Box sx={{ fontSize: 36, mr: 2, color: 'primary.main' }}>📄</Box>
        <Typography variant="h5" gutterBottom fontWeight={700}>
          Détails de la facture n° {invoice.invoice_number || id}
        </Typography>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2, background: '#e3f2fd' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Fournisseur</Typography>
            <Typography variant="h6">{invoice.provider || 'N/A'}</Typography>
          </Paper>
          <Paper sx={{ p: 2, mb: 2, background: '#e3f2fd' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Client</Typography>
            <Typography variant="body1">{invoice.customer_name || 'N/A'}</Typography>
            <Typography variant="body2" color="text.secondary">ID : {invoice.customer_id || 'N/A'}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2, background: '#fffde7' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Montant total</Typography>
            <Typography variant="h6">{invoice.total_amount ? invoice.total_amount + ' Dhs' : 'N/A'}</Typography>
          </Paper>
          <Paper sx={{ p: 2, background: '#fffde7' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Consommation</Typography>
            <Typography variant="body1">{invoice.total_kwh || 'N/A'} kWh</Typography>
            <Typography variant="body2" color="text.secondary">Tarif : {invoice.rate_per_kwh || 'N/A'}</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 2, background: '#f3e5f5' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Période</Typography>
            <Typography variant="body1">{invoice.period_start || 'N/A'} à {invoice.period_end || 'N/A'}</Typography>
          </Paper>
          <Paper sx={{ p: 2, background: '#f3e5f5' }} elevation={0}>
            <Typography variant="subtitle2" color="text.secondary">Détails</Typography>
            <Typography variant="body2">kWh Pointe : {invoice.peak_kwh || 'N/A'}</Typography>
            <Typography variant="body2">kWh Creuses : {invoice.off_peak_kwh || 'N/A'}</Typography>
            <Typography variant="body2">Date d'émission : {invoice.issue_date || 'N/A'}</Typography>
            <Typography variant="body2">Date d'échéance : {invoice.due_date || 'N/A'}</Typography>
          </Paper>
        </Grid>
      </Grid>
      <Divider sx={{ my: 3 }} />

      {/* Analysis Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h6" gutterBottom>Analyse de la facture</Typography>
        {analysisLoading ? (
          <CircularProgress size={22} sx={{ mt: 1 }} />
        ) : analysisError ? (
          <Alert severity="error">{analysisError}</Alert>
        ) : analysis && (Array.isArray(analysis.issues) ? analysis.issues.length > 0 : Object.keys(analysis).length > 0) ? (
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              <b>Problèmes détectés :</b>
            </Typography>
            <Grid container spacing={2}>
              {(analysis.issues || Object.values(analysis)).map((issue, idx) => {
                const desc = issue.description || (typeof issue === 'string' ? issue : JSON.stringify(issue));
                const sev = issue.severity || 'medium';
                let icon = '⚠️', color = '#ffa726';
                if (sev === 'high') { icon = '⛔'; color = '#ef5350'; }
                else if (sev === 'low') { icon = 'ℹ️'; color = '#90caf9'; }
                return (
                  <Grid item xs={12} md={6} key={idx}>
                    <Paper sx={{ p: 2, background: '#fff3e0', borderLeft: `6px solid ${color}`, display: 'flex', alignItems: 'center' }} elevation={1}>
                      <Box sx={{ fontSize: 28, mr: 2 }}>{icon}</Box>
                      <Box>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>{desc}</Typography>
                        <Typography variant="caption" color="text.secondary">Gravité : {sev}</Typography>
                      </Box>
                    </Paper>
                  </Grid>
                );
              })}
            </Grid>
          </Box>
        ) : (
          <Alert severity="success">Aucun problème détecté dans cette facture.</Alert>
        )}
      </Box>

      <Typography variant="h6" sx={{ mt: 2 }}>Postes détaillés</Typography>
      <Box sx={{ mt: 1 }}>
        {invoice.items && invoice.items.length > 0 ? (
          invoice.items.map((item, idx) => (
            <Paper key={idx} variant="outlined" sx={{ p: 2, mb: 1 }}>
              <Grid container spacing={1}>
                <Grid item xs={6} sm={4}><b>{item.description}</b></Grid>
                <Grid item xs={6} sm={2}>Quantité : {item.quantity}</Grid>
                <Grid item xs={6} sm={3}>Prix unitaire : {item.unit_price}</Grid>
                <Grid item xs={6} sm={3}>Total : {item.total}</Grid>
              </Grid>
            </Paper>
          ))
        ) : (
          <Typography>Aucun poste détaillé trouvé.</Typography>
        )}
      </Box>
      <Divider sx={{ my: 2 }} />
      <Typography variant="h6">Taxes</Typography>
      <Box sx={{ mt: 1, mb: 2 }}>
        {invoice.taxes ? (
          Object.entries(invoice.taxes).map(([key, value]) => (
            <Chip key={key} label={`${key} : ${value} Dhs`} sx={{ mr: 1, mb: 1 }} />
          ))
        ) : (
          <Typography>Aucune taxe trouvée.</Typography>
        )}
      </Box>
      <Divider sx={{ my: 2 }} />
      <Recommendations recommendations={recommendations} />
    </Paper>
  );
}
