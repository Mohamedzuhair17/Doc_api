# Document AI Full Stack (Structured)

This repository contains:
- `backend/`  : FastAPI + Celery document AI API
- `frontend/` : React + Vite frontend UI

## Run with Docker Compose

1. From root:
   ```bash
   docker compose up --build
   ```
2. Backend API: http://localhost:8000
3. Frontend UI: http://localhost:5173

## Run locally without Docker

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

## API Endpoints

- `POST /api/document-analyze`
- `GET /api/task/{task_id}`
- `GET /health`

## Notes

- Frontend `src/services/apiClient.ts` uses `VITE_API_URL` & `VITE_API_KEY`.
- Backend expects `x-api-key` header with secret from `backend/.env`.
