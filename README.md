# AI Chatbot (Angular + FastAPI)

This project pairs a modern **Angular 17** chat frontend with a lightweight **FastAPI** backend. The frontend provides a polished chat experience, while the backend persists conversations to disk and simulates AI responses. The codebase is ready for you to replace the placeholder AI logic with calls to your preferred LLM provider (OpenAI, Anthropic, Azure AI, etc.).

## Architecture Overview

```
Internship/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── schemas.py           # Pydantic models / validators
│   │   └── storage.py           # JSON persistence helpers
│   ├── data/
│   │   └── conversations.json   # Conversation store
│   └── requirements.txt         # Backend dependencies
└── src/
    └── app/
        ├── components/
        │   ├── chat-area/
        │   ├── login/
        │   ├── message-bubble/
        │   └── sidebar/
        ├── config/api.config.ts # Frontend → backend base URL
        ├── guards/auth.guard.ts
        ├── models/message.model.ts
        └── services/
            ├── auth.service.ts
            └── chat.service.ts
```

## Key Features

### Frontend
- Angular 17 standalone components with Signals
- Email/password login, collapsible sidebar, multiple conversations
- Message timestamps, loading indicators, keyboard shortcuts
- Responsive layout with custom styling

### Backend
- FastAPI application with CORS enabled for Angular dev server
- Endpoints for login, CRUD conversations, and message exchange
- JSON file persistence (`backend/data/conversations.json`)
- Deterministic simulated assistant response (easy to replace with real AI call)

## Prerequisites

- **Node.js** 18+
- **Python** 3.10+

## Quick Start

### 1. Clone & Install Frontend Dependencies
```bash
cd Internship
npm install
```

### 2. Create Python Virtual Environment & Install Backend Dependencies
```bash
cd backend
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
cd ..
npm start
```
Frontend runs at `http://localhost:4200` and talks to the backend via the base URL defined in `src/app/config/api.config.ts`.

## API Endpoints

| Method | Endpoint                                     | Description                           |
|--------|----------------------------------------------|---------------------------------------|
| GET    | `/api/health`                                | Health check                          |
| POST   | `/api/auth/login`                            | Email/password login (mock)           |
| GET    | `/api/conversations`                         | List conversations                    |
| POST   | `/api/conversations`                         | Create new conversation               |
| GET    | `/api/conversations/{conversationId}`        | Retrieve conversation + messages      |
| POST   | `/api/conversations/{conversationId}/messages` | Add user message (backend simulates assistant reply) |
| DELETE | `/api/conversations/{conversationId}`        | Delete conversation                   |
| DELETE | `/api/conversations`                         | Delete all conversations (creates default chat) |

## Replacing the Mock AI Response

`backend/app/main.py` currently calls `_generate_response()` to craft a deterministic reply. To hook up a real AI service, replace the contents of that function with your API integration and return the generated text.

## Frontend Integration Details

- `AuthService` now calls `POST /api/auth/login` and stores the returned user in Signals + localStorage.
- `ChatService` calls the FastAPI endpoints to load conversations, send messages, create/delete chats, and keeps Signals in sync.
- `api.config.ts` centralizes the backend base URL.
- Components (login, chat area, sidebar) await asynchronous service methods and show loading states where appropriate.

## Development Tips

- Update `API_BASE_URL` if you expose the backend on a different host/port.
- The backend stores data in JSON—delete `backend/data/conversations.json` to reset.
- Use your preferred process manager or containerize both apps for production.

## Scripts

| Command                           | Description                             |
|-----------------------------------|-----------------------------------------|
| `npm start`                       | Start Angular dev server                 |
| `npm run build`                   | Build production bundle                  |
| `uvicorn app.main:app --reload`   | Start FastAPI with auto-reload           |
| `pip install -r requirements.txt` | Install backend dependencies             |

## License

This repository is provided for educational and prototyping purposes. Integrate authentication, authorization, and secure AI provider calls before using in production.
