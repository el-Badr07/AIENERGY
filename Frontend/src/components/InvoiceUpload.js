import React, { useState } from 'react';
import { Box, Button, Typography, Paper, LinearProgress, Alert, Fade } from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined';
import UploadFileOutlinedIcon from '@mui/icons-material/UploadFileOutlined';
import { uploadInvoice } from '../api/api';
import { useNavigate } from 'react-router-dom';

export default function InvoiceUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError('');
    setSuccess(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragActive(true);
  };
  const handleDragLeave = (e) => {
    e.preventDefault();
    setDragActive(false);
  };
  const handleDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      setError('');
      setSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier.');
      return;
    }
    setUploading(true);
    setError('');
    setSuccess(false);
    try {
      await uploadInvoice(file);
      setUploading(false);
      setSuccess(true);
      setTimeout(() => navigate('/invoices'), 1200);
    } catch (err) {
      setUploading(false);
      setError('Erreur lors de l\'importation du fichier.');
    }
  };

  return (
    <Paper elevation={4} sx={{ p: { xs: 2, sm: 5 }, mt: 3, maxWidth: 600, mx: 'auto', borderRadius: 5, boxShadow: '0 6px 32px 0 rgba(25,118,210,0.10)' }}>
      <Box sx={{ textAlign: 'center', mb: 3 }}>
        <UploadFileOutlinedIcon sx={{ fontSize: 64, color: '#1976d2', mb: 1 }} />
        <Typography variant="h4" fontWeight={800} gutterBottom>
          Importer une redevance électrique
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 2 }}>
          Glissez-déposez votre fichier PDF ou image ici, ou cliquez pour sélectionner un fichier à importer.
        </Typography>
      </Box>
      <Box
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        sx={{
          border: dragActive ? '2px dashed #43a047' : '2px dashed #b0bec5',
          borderRadius: 4,
          py: 6,
          px: 2,
          background: dragActive ? 'rgba(67,160,71,0.07)' : 'rgba(197,225,165,0.04)',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'border 0.2s, background 0.2s',
          mb: 3,
          position: 'relative',
        }}
        onClick={() => document.getElementById('fileInput').click()}
      >
        {file ? (
          <Fade in={!!file}>
            <Box display="flex" alignItems="center" justifyContent="center" gap={2}>
              <InsertDriveFileOutlinedIcon sx={{ fontSize: 36, color: '#43a047' }} />
              <Typography fontWeight={600}>{file.name}</Typography>
            </Box>
          </Fade>
        ) : (
          <Typography color="text.secondary">Déposez un fichier ici ou cliquez pour parcourir</Typography>
        )}
        <input
          id="fileInput"
          type="file"
          hidden
          onChange={handleFileChange}
          accept=".pdf,image/*"
        />
      </Box>
      {uploading && <LinearProgress sx={{ my: 2 }} />}
      {success && <Alert severity="success" sx={{ mt: 2 }}>Importation réussie ! Redirection...</Alert>}
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      <Button
        variant="contained"
        color="secondary"
        fullWidth
        size="large"
        onClick={handleUpload}
        disabled={uploading}
        sx={{ mt: 2, fontWeight: 700, py: 1.5, fontSize: 18, boxShadow: '0 2px 8px 0 rgba(67,160,71,0.12)' }}
        startIcon={<CloudUploadIcon />}
      >
        Importer
      </Button>
    </Paper>
  );
}
