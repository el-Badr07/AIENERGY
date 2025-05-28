# AIENERGY - Energy Invoice Analysis System

## Overview
AIENERGY is an AI-powered application for analyzing energy invoices. The system extracts information from uploaded invoices using OCR, displays the extracted data, identifies potential issues, and provides recommendations for energy optimization and cost savings.

## Features
- Invoice upload and processing
- OCR text extraction using Whisper
- Data analysis and problem detection using Groq LLM
- Recommendations for energy optimization
- User-friendly interface for viewing invoice data

## Project Structure
- `/backend` - Flask API server
- `/Frontend` - React frontend application (see instructions below)

## Technologies
- **Backend**: Python, Flask, Whisper (OCR), Groq (LLM)
- **Frontend**: React, Material UI, Axios
- **Data Processing**: PyPDF2, pandas

## Setup and Installation

### Backend (Flask API)
1. Clone the repository
2. Navigate to the backend directory:
   ```bash
   cd backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables (copy `.env.example` to `.env` and fill in as needed).
5. Run the backend server:
   ```bash
   python app.py
   ```
   The backend will start at [http://localhost:5000](http://localhost:5000).

### Frontend (React App)
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd Frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the frontend app:
   ```bash
   npm start
   ```
   The frontend will run at [http://localhost:3000](http://localhost:3000).

> Ensure the backend is running before using the frontend. The frontend is configured to proxy API requests to `http://localhost:5000` by default.

## API Endpoints
- `POST /api/upload` - Upload an invoice for processing
- `GET /api/invoices_all` - Get all invoices with full results (used by dashboard and list)
- `GET /api/invoice_full/<id>` - Get full results for a specific invoice (used by details page)
- `GET /api/invoices` - Get list of processed invoices (legacy)
- `GET /api/invoices/<id>` - Get details for a specific invoice (legacy)
- `GET /api/recommendations/<id>` - Get recommendations for a specific invoice