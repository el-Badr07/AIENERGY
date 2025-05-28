import React, { useEffect, useState } from 'react';
import { Box, Grid, Paper, Typography, CircularProgress, Alert, Divider } from '@mui/material';
import { Line, Bar, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title } from 'chart.js';
import { getAllFullInvoices } from '../api/api';
import SavingsIcon from '@mui/icons-material/Savings';
import FlashOnIcon from '@mui/icons-material/FlashOn';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import BusinessIcon from '@mui/icons-material/Business';

// Chart.js registration
// import {
//   Chart as ChartJS,
//   ArcElement,
//   Tooltip,
//   Legend,
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   BarElement,
//   Title,
// } from 'chart.js';
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, BarElement, Title);

export default function Dashboard() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    console.log('Dashboard mounted, attempting fetch');
    getAllFullInvoices()
      .then(res => {
        console.log('Received data from /api/invoices_all:', res.data);
        // Flatten to extract all invoice, analysis, recommendations into one object per invoice
        setInvoices(res.data.map(entry => ({
          ...entry.invoice,
          analysis: entry.analysis,
          recommendations: entry.recommendations
        })));
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching invoices:', err);
        setError('Erreur lors du chargement des factures.');
        setLoading(false);
      });
  }, []);

  // Debug log to see actual structure
  console.log('Invoices data:', invoices);

  // Aggregate data
  const totalAmount = invoices.reduce((sum, inv) => sum + (Number(inv.total_amount) || 0), 0);
  const totalKwh = invoices.reduce((sum, inv) => sum + (Number(inv.total_kwh) || 0), 0);
  
  // Robust potential_savings extraction - check in both root and recommendations
  const getSavings = inv => {
    // First try direct potential_savings
    let val = inv.potential_savings;
    
    // If not found, check in recommendations
    if (!val && inv.recommendations && inv.recommendations.potential_savings) {
      val = inv.recommendations.potential_savings;
    }
    
    // Handle case where we have the full recommendations object
    if (!val && typeof inv === 'object') {
      // Look for recommendations at root level
      if (inv.recommendations) {
        val = inv.recommendations.potential_savings;
      }
      
      // Try to find it in any nested object
      if (!val) {
        for (const key in inv) {
          if (inv[key] && typeof inv[key] === 'object' && inv[key].potential_savings) {
            val = inv[key].potential_savings;
            break;
          }
        }
      }
    }
    
    // Process the value
    if (val && typeof val === 'object') {
      val = val.value || val.amount || Object.values(val).find(v => typeof v === 'number');
    }
    if (typeof val === 'number' && isFinite(val)) return val;
    if (typeof val === 'string') {
      if (val.trim().toUpperCase() === 'N/A') return 0;
      const parsed = Number(val);
      if (!isNaN(parsed) && isFinite(parsed)) return parsed;
    }
    return 0;
  };
  
  const savings = invoices.reduce((sum, inv) => sum + getSavings(inv), 0);

  // Monthly trends
  const months = {};
  invoices.forEach(inv => {
    const date = inv.issue_date || inv.period_start;
    if (date) {
      const month = date.slice(0,7); // YYYY-MM
      if (!months[month]) months[month] = { amount: 0, kwh: 0, count: 0 };
      months[month].amount += Number(inv.total_amount) || 0;
      months[month].kwh += Number(inv.total_kwh) || 0;
      months[month].count++;
    }
  });
  const sortedMonths = Object.keys(months).sort();

  // Provider breakdown
  const providers = {};
  invoices.forEach(inv => {
    const p = inv.provider || 'Autre';
    if (!providers[p]) providers[p] = { amount: 0, kwh: 0, count: 0 };
    providers[p].amount += Number(inv.total_amount) || 0;
    providers[p].kwh += Number(inv.total_kwh) || 0;
    providers[p].count++;
  });

  // Peak/off-peak breakdown
  // Heures Pleines vs Creuses (robust)
  let peak = 0, offpeak = 0, normal = 0;
  invoices.forEach(inv => {
    // Try both possible spellings and fallback to items
    peak += Number(inv.peak_kwh) || 0;
    offpeak += Number(inv.off_peak_kwh) || 0;
    
    // If we have invoice items, extract from there
    if (Array.isArray(inv.items)) {
      inv.items.forEach(item => {
        const desc = (item.description || '').toLowerCase();
        if (desc.includes('pointe')) peak += Number(item.quantity) || 0;
        else if (desc.includes('creuse')) offpeak += Number(item.quantity) || 0;
        else if (desc.includes('normale')) normal += Number(item.quantity) || 0;
      });
    }
    
    // Handle case where we have a single invoice with the structure shown in your example
    if (inv.invoice && inv.invoice.peak_kwh) peak += Number(inv.invoice.peak_kwh) || 0;
    if (inv.invoice && inv.invoice.off_peak_kwh) offpeak += Number(inv.invoice.off_peak_kwh) || 0;
  });
  
  // If we still have no data but we have the sample data structure, use it
  if (peak === 0 && offpeak === 0 && invoices.length === 1) {
    const sampleInv = invoices[0];
    if (sampleInv.invoice) {
      // Try to extract from the sample structure
      const items = sampleInv.invoice.items || [];
      items.forEach(item => {
        const desc = (item.description || '').toLowerCase();
        if (desc.includes('pointe')) peak += Number(item.quantity) || 0;
        else if (desc.includes('creuse')) offpeak += Number(item.quantity) || 0;
        else if (desc.includes('normale')) normal += Number(item.quantity) || 0;
      });
    }
  }

  // Invoice items by type (pie)
  const itemTypes = {};
  invoices.forEach(inv => {
    // Handle regular invoice items
    const items = inv.items || [];
    items.forEach(item => {
      const key = item.description || 'Autre';
      if (!itemTypes[key]) itemTypes[key] = 0;
      itemTypes[key] += Number(item.total) || 0;
    });
    
    // Handle nested invoice structure
    if (inv.invoice && Array.isArray(inv.invoice.items)) {
      inv.invoice.items.forEach(item => {
        const key = item.description || 'Autre';
        if (!itemTypes[key]) itemTypes[key] = 0;
        itemTypes[key] += Number(item.total) || 0;
      });
    }
  });
  
  // If we still have no data, try to extract from the sample JSON structure
  if (Object.keys(itemTypes).length === 0 && invoices.length > 0) {
    // Try the structure from your example JSON
    const sampleInv = invoices[0];
    if (sampleInv.invoice && Array.isArray(sampleInv.invoice.items)) {
      sampleInv.invoice.items.forEach(item => {
        const key = item.description || 'Autre';
        if (!itemTypes[key]) itemTypes[key] = 0;
        itemTypes[key] += Number(item.total) || 0;
      });
    }
  }
  // Only show item types with >0 value
  const filteredItemLabels = Object.keys(itemTypes).filter((k, i) => Number(itemTypes[k]) > 0);
  const filteredItemData = filteredItemLabels.map(k => itemTypes[k]);
  const itemPieData = {
    labels: filteredItemLabels,
    datasets: [{
      data: filteredItemData,
      backgroundColor: ['#1976d2', '#43a047', '#ffa726', '#ef5350', '#90caf9', '#a1887f', '#ce93d8', '#ffb74d'],
    }],
  };

  // Taxes breakdown (bar)
  const taxMap = {};
  invoices.forEach(inv => {
    // Handle direct taxes object
    if (inv.taxes) {
      Object.entries(inv.taxes).forEach(([tax, val]) => {
        if (!taxMap[tax]) taxMap[tax] = 0;
        taxMap[tax] += Number(val) || 0;
      });
    }
    
    // Handle nested invoice structure
    if (inv.invoice && inv.invoice.taxes) {
      Object.entries(inv.invoice.taxes).forEach(([tax, val]) => {
        if (!taxMap[tax]) taxMap[tax] = 0;
        taxMap[tax] += Number(val) || 0;
      });
    }
  });
  
  // If we still have no data, try to extract from the sample JSON structure
  if (Object.keys(taxMap).length === 0 && invoices.length > 0) {
    // Try the structure from your example JSON
    const sampleInv = invoices[0];
    if (sampleInv.invoice && sampleInv.invoice.taxes) {
      Object.entries(sampleInv.invoice.taxes).forEach(([tax, val]) => {
        if (!taxMap[tax]) taxMap[tax] = 0;
        taxMap[tax] += Number(val) || 0;
      });
    }
  }
  // Only show tax types with >0 value
  const filteredTaxLabels = Object.keys(taxMap).filter(k => Number(taxMap[k]) > 0);
  const filteredTaxData = filteredTaxLabels.map(k => taxMap[k]);
  const taxBarData = {
    labels: filteredTaxLabels,
    datasets: [{
      label: 'Montant total',
      data: filteredTaxData,
      backgroundColor: ['#1976d2', '#ffa726', '#43a047', '#ef5350', '#90caf9', '#a1887f'],
    }],
  };

  // Efficiency score (gauge simulation)
  const efficiencyScores = invoices.map(inv => Number(inv.efficiency_score) || 0).filter(x => x > 0);
  const avgEfficiency = efficiencyScores.length ? efficiencyScores.reduce((a, b) => a + b, 0) / efficiencyScores.length : null;

  // Chart data
  const lineData = {
    labels: sortedMonths,
    datasets: [
      {
        label: 'Montant total (Dhs)',
        data: sortedMonths.map(m => months[m].amount),
        fill: false,
        borderColor: '#1976d2',
        backgroundColor: '#1976d2',
        tension: 0.3,
      },
      {
        label: 'Consommation (kWh)',
        data: sortedMonths.map(m => months[m].kwh),
        fill: false,
        borderColor: '#43a047',
        backgroundColor: '#43a047',
        tension: 0.3,
      },
    ],
  };
  const providerData = {
    labels: Object.keys(providers),
    datasets: [
      {
        label: 'Montant total',
        data: Object.values(providers).map(p => p.amount),
        backgroundColor: ['#1976d2', '#43a047', '#ffa726', '#ef5350', '#90caf9', '#a1887f'],
      },
    ],
  };
  const peakPieData = {
    labels: ['Heures Pleines (HP)', 'Heures Creuses (HC)', 'Heures Normales (HN)'],
    datasets: [
      {
        data: [peak, offpeak, normal],
        backgroundColor: ['#ffa726', '#90caf9', '#81c784'],
      },
    ],
  };

  return (
    <Box sx={{ px: { xs: 0, md: 2 }, py: 2 }}>
      <Typography variant="h3" fontWeight={800} sx={{ mb: 3, textAlign: 'center', letterSpacing: 2 }}>
        Tableau de bord
      </Typography>
      {loading ? (
        <CircularProgress sx={{ mt: 6 }} />
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <>
          <Grid container spacing={3} sx={{ mb: 2 }}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', background: '#e3f2fd' }} elevation={3}>
                <SavingsIcon sx={{ fontSize: 40, color: '#43a047', mb: 1 }} />
                <Typography variant="h5" fontWeight={700}>
                  {totalAmount.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} Dhs
                </Typography>
                <Typography color="text.secondary">Dépenses totales</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', background: '#e8f5e9' }} elevation={3}>
                <FlashOnIcon sx={{ fontSize: 40, color: '#1976d2', mb: 1 }} />
                <Typography variant="h5" fontWeight={700}>
                  {totalKwh.toLocaleString('fr-FR', { minimumFractionDigits: 0 })} kWh
                </Typography>
                <Typography color="text.secondary">Consommation totale</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, textAlign: 'center', background: '#fffde7' }} elevation={3}>
                <SavingsIcon sx={{ fontSize: 40, color: '#ffa726', mb: 1 }} />
                <Typography variant="h5" fontWeight={700}>
                  {savings.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} Dhs
                </Typography>
                <Typography color="text.secondary">Économies potentielles</Typography>
              </Paper>
            </Grid>
          </Grid>
          <Divider sx={{ my: 3 }} />
          <Grid container spacing={4}>
            <Grid item xs={12} md={7}>
              <Paper sx={{ p: 3, mb: 3 }} elevation={2}>
                <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                  Évolution mensuelle (Montant & kWh)
                </Typography>
                <Line data={lineData} options={{ responsive: true, plugins: { legend: { position: 'top' } } }} />
            </Paper>
            <Paper sx={{ p: 3, mb: 3 }} elevation={2}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Répartition des postes de facture
              </Typography>
              {filteredItemData.length > 0 ? (
                <Pie data={itemPieData} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
              ) : (
                <Typography color="text.secondary">Aucune donnée disponible pour ce graphique.</Typography>
              )}
            </Paper>
          </Grid>
          <Grid item xs={12} md={5}>
            <Paper sx={{ p: 3, mb: 3 }} elevation={2}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Heures Pleines vs Creuses
              </Typography>
              {(peak > 0 || offpeak > 0) ? (
                <Pie data={peakPieData} options={{ responsive: true, plugins: { legend: { position: 'bottom' } } }} />
              ) : (
                <Typography color="text.secondary">Aucune donnée disponible pour ce graphique.</Typography>
              )}
            </Paper>
            <Paper sx={{ p: 3, mb: 3 }} elevation={2}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Répartition par fournisseur
              </Typography>
              {Object.keys(providers).length > 0 ? (
                <Bar data={providerData} options={{ 
                  responsive: true, 
                  plugins: { 
                    legend: { display: false },
                    title: {
                      display: true,
                      text: 'Montant total par fournisseur'
                    }
                  } 
                }} />
              ) : (
                <Typography color="text.secondary">Aucune donnée disponible pour ce graphique.</Typography>
              )}
            </Paper>
            <Paper sx={{ p: 3, mb: 3 }} elevation={2}>
              <Typography variant="h6" fontWeight={700} sx={{ mb: 2 }}>
                Répartition des taxes
              </Typography>
              {filteredTaxData.length > 0 ? (
                <Bar data={taxBarData} options={{ responsive: true, plugins: { legend: { display: false } } }} />
              ) : (
                <Typography color="text.secondary">Aucune donnée disponible pour ce graphique.</Typography>
              )}
            </Paper>
            <Paper sx={{ p: 3, background: '#f4f6f8', mb: 3 }} elevation={0}>
              <Typography variant="body1" color="text.secondary">
                <CalendarMonthIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#1976d2' }} />
                Période couverte : {sortedMonths[0] || 'N/A'} à {sortedMonths[sortedMonths.length-1] || 'N/A'}
              </Typography>
              <Typography variant="body1" color="text.secondary" sx={{ mt: 1 }}>
                <BusinessIcon sx={{ mr: 1, verticalAlign: 'middle', color: '#43a047' }} />
                Fournisseurs : {Object.keys(providers).join(', ')}
              </Typography>
            </Paper>
            {/* Efficiency score gauge removed as requested */}
          </Grid>
        </Grid>
      </>
    )}
  </Box>
);
}
