import React from 'react';
import { Typography, Paper, Box, Chip } from '@mui/material';

export default function Recommendations({ recommendations }) {
  if (!recommendations) return null;

  return (
    <Paper elevation={2} sx={{ p: 3, mt: 2 }}>
      <Typography variant="h6" gutterBottom>
        Recommandations d'optimisation
      </Typography>
      {recommendations.recommendations && recommendations.recommendations.length > 0 ? (
        <Box sx={{ mb: 2 }}>
          {recommendations.recommendations.map((rec, idx) => (
            <Typography key={idx} sx={{ mb: 1 }}>
              • {rec}
            </Typography>
          ))}
        </Box>
      ) : (
        <Typography>Aucune recommandation disponible.</Typography>
      )}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle1">
          Économies potentielles : <b>{
            (() => {
              let val = recommendations.potential_savings;
              if (val && typeof val === 'object') {
                // Try to extract a numeric value from the object
                val = val.value || val.amount || Object.values(val).find(v => typeof v === 'number');
              }
              if (typeof val === 'number') {
                return val.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' Dhs';
              }
              if (typeof val === 'string' && !isNaN(Number(val))) {
                return Number(val).toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + ' Dhs';
              }
              return 'N/A';
            })()
          }</b>
        </Typography>
        <Typography variant="subtitle1">
          Score d'efficacité : <Chip label={recommendations.efficiency_score !== undefined ? recommendations.efficiency_score + '/100' : 'N/A'} color="secondary" />
        </Typography>
      </Box>
    </Paper>
  );
}
