# Autoagents Workspace

## Prerequisites
- Node.js 18+ (already available: 24.11.0)
- Python 3.10+ (workspace uses 3.14.0)

## Start the FastAPI backend
```powershell
cd autoagents-backend
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

You should see a log entry similar to:
```
INFO:     Autoagents backend started on port 8000
```

## Start the Angular frontend
```powershell
cd autoagents-frontend
npm install
ye\npm start
```

When the browser opens:
- The devtools console logs `Connecting to backend at http://localhost:8000`.
- The **Right Now** panel displays the LangChain-generated status once the backend responds.
- Login, Sign Up, Gmail, and Microsoft Teams panels are available on the home screen.

## Endpoints
- `GET /` – health check
- `GET /status/right-now` – LangChain-powered status summary consumed by the frontend
- `POST /chat` – sends `{ "message": "..." }` and returns a LangChain-crafted reply

