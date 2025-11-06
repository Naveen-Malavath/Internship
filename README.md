# AI Chatbot (Angular + FastAPI)

This repository contains a modern **Angular 17** chat frontend paired with a lightweight **FastAPI** backend. The Angular UI provides a polished chat experience while the backend persists conversations to disk and generates deterministic placeholder responses. You can swap the placeholder logic for your preferred LLM provider (OpenAI, Anthropic, Azure AI, etc.).

## Project Layout

```
Internship/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── schemas.py           # Pydantic models / validators
│   │   └── storage.py           # JSON persistence helpers
│   ├── data/
│   │   └── .gitignore           # Keeps runtime conversations out of git
│   └── requirements.txt         # Backend dependencies
├── frontend/
│   ├── angular.json
│   ├── package.json / package-lock.json
│   ├── tsconfig.json / tsconfig.app.json
│   ├── src/
│   │   ├── app/components/…     # chat-area, login, sidebar, message-bubble
│   │   ├── app/services/…       # auth.service, chat.service
│   │   ├── app/config/api.config.ts
│   │   └── app/guards/auth.guard.ts
│   └── *.md                     # Reference guides and setup docs
└── README.md (this file)
```

## Key Features

### Frontend
- Angular 17 using standalone components and Signals
- Email/password login, collapsible sidebar, multiple conversations
- Message timestamps, loading indicators, keyboard shortcuts
- Responsive design with polished styling and onboarding prompts

### Backend
- FastAPI with permissive CORS for the Angular dev server
- REST endpoints for login, creating/listing/deleting conversations and messages
- JSON file persistence in `backend/data/`
- Deterministic simulated assistant response (replace with a real AI call when ready)

## Prerequisites

- **Node.js** 18+
- **Python** 3.10+

## Quick Start

### 1. Install Frontend Dependencies
```bash
cd Internship/frontend
npm install
```

### 2. Create a Python Virtual Environment & Install Backend Dependencies
```bash
cd ../backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Start the FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8000
```
Backend runs at `http://localhost:8000` with API routes under `/api/*`.

### 4. Start the Angular Frontend
```bash
cd ../frontend
npm start
```
Frontend runs at `http://localhost:4200` and communicates with the backend via `src/app/config/api.config.ts`.

## API Endpoints

| Method | Endpoint                                       | Description                                                   |
|--------|------------------------------------------------|---------------------------------------------------------------|
| GET    | `/api/health`                                  | Health check                                                  |
| POST   | `/api/auth/login`                              | Email/password login (mock – simply echoes the email back)    |
| GET    | `/api/conversations`                           | List all conversations                                        |
| POST   | `/api/conversations`                           | Create a new conversation                                     |
| GET    | `/api/conversations/{conversationId}`          | Retrieve a conversation and its messages                      |
| POST   | `/api/conversations/{conversationId}/messages` | Add a user message (backend also appends a simulated reply)   |
| DELETE | `/api/conversations/{conversationId}`          | Delete a single conversation                                  |
| DELETE | `/api/conversations`                           | Delete all conversations and create a fresh default chat      |

## Replacing the Mock AI Response

`backend/app/main.py` currently calls `_generate_response()` to craft a canned reply. Replace the body of that helper with calls to your AI provider and return the generated text to integrate a real model.

## Frontend Integration Highlights

- `AuthService` calls `POST /api/auth/login`, persists the returned user with Signals and localStorage, and performs navigation.
- `ChatService` orchestrates all chat API calls (list/create/send/delete/clear) and keeps Angular Signals in sync, showing optimistic updates while waiting for the backend.
- `src/app/config/api.config.ts` centralizes the backend base URL.
- Components (login, chat area, sidebar) await asynchronous service methods and expose loading states to the UI.

## Development Tips

- Update `API_BASE_URL` if you expose the backend on a different host/port.
- The backend stores data in JSON—delete `backend/data/conversations.json` (created at runtime) to reset.
- The frontend reference guides (`frontend/SETUP_GUIDE.md`, `frontend/FEATURES.md`, etc.) remain available inside the `frontend` folder.
- Consider Docker or process managers if you deploy both services together.

## Useful Scripts

| Command                                 | Description                             |
|-----------------------------------------|-----------------------------------------|
| `npm start` (run inside `frontend/`)    | Start Angular dev server                 |
| `npm run build` (inside `frontend/`)    | Build production bundle                  |
| `uvicorn app.main:app --reload`         | Start FastAPI with auto-reload           |
| `pip install -r backend/requirements.txt` | Install backend dependencies             |

## License

This codebase is supplied for educational and prototyping purposes. Add proper authentication, authorization, and secure AI provider calls before using it in production.
