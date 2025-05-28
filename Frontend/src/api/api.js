import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const uploadInvoice = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return axios.post(`${API_BASE}/upload`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getInvoices = () => axios.get(`${API_BASE}/invoices`);

export const getInvoiceById = (id) => axios.get(`${API_BASE}/invoices/${id}`);

export const getRecommendations = (id) => axios.get(`${API_BASE}/recommendations/${id}`);

export const getAnalysis = (id) => axios.get(`${API_BASE}/analysis/${id}`);

// New endpoints for full invoice data
export const getAllFullInvoices = () => axios.get(`${API_BASE}/invoices_all`);

export const getFullInvoiceById = (id) => axios.get(`${API_BASE}/invoice_full/${id}`);

