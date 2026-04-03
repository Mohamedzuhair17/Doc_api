# Document AI Frontend

This frontend is a custom React + Vite + TypeScript application for your Document AI service.

## Setup

1. Install dependencies:
   ```bash
   npm install
   ```
2. Configure backend URL and API key in `.env`:
   ```ini
   VITE_API_URL=https://doc-api-efwm.onrender.com
   VITE_API_KEY=hackathon_secret_123
   ```
3. Start application:
   ```bash
   npm run dev
   ```

## Backend requirements

- Document AI backend running on `https://doc-api-efwm.onrender.com` (or your own API host)
- Endpoint: `POST /api/document-analyze`
- Endpoint: `GET /api/task/{task_id}`
- Header: `x-api-key: <API_SECRET_KEY>`

## Features

- Upload document (PDF/PNG/TIFF/DOCX)
- Async task polling with status and progress UI
- Result display for AI summary, entities, sentiment
- Copy/download extracted data

