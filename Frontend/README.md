# AIENERGY Frontend

A modern React frontend for the AIENERGY project. Upload, view, and analyze your energy invoices with a beautiful, responsive interface.

## Features
- Upload PDF or image invoices
- View list of processed invoices (only those with full data)
- See detailed invoice extraction, analysis, and recommendations
- Responsive Material UI design
- Graceful handling of missing data and empty states
- Seamless integration with Flask backend

## Getting Started

### 1. Install dependencies
```bash
npm install
```

### 2. Run the app
```bash
npm start
```
The app will run at [http://localhost:3000](http://localhost:3000) by default.

> **Make sure your Flask backend is running at http://localhost:5000**

## Project Structure
- `src/components/` — React UI components (Dashboard, InvoiceList, InvoiceDetails, InvoiceUpload, etc.)
- `src/api/` — API integration with backend (`api.js`)
- `src/theme.js` — Material UI theme
- `src/App.js` — Main app and routing

## Environment Variables
- By default, API requests are proxied to `http://localhost:5000`. If your backend runs elsewhere, update the `proxy` field in `package.json` and/or API URLs in `src/api/api.js`.

## Troubleshooting
- If you see CORS errors, ensure the backend allows requests from the frontend origin.
- If invoices do not appear, check that the backend is running and that there are processed invoices with full data available.
- For any missing or unclear fields, the UI will display a placeholder and tooltip.

---

© 2025 AIENERGY
