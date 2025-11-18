# Autoagents Workspace

This repository contains a modern **Angular 17** frontend paired with a **FastAPI** backend for AI-powered project design generation. The system generates High-Level Design (HLD), Low-Level Design (LLD), and Database Design (DBD) diagrams using Claude AI.

## Prerequisites
- Node.js 18+ (already available: 24.11.0)
- Python 3.10+ (workspace uses 3.14.0)
- An Anthropic API key with access to Claude (set as `ANTHROPIC_API_KEY`)

## Project Layout

```
Internship/
├── autoagents-backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entrypoint
│   │   ├── routers/             # API routes
│   │   ├── services/            # Agent services (agent1, agent2, agent3)
│   │   ├── schemas/             # Pydantic models
│   │   └── db.py                # MongoDB connection
│   └── requirements.txt         # Backend dependencies
├── autoagents-frontend/
│   ├── src/app/
│   │   ├── workspace/           # Workspace components
│   │   ├── project/             # Project wizard
│   │   ├── features/            # Feature components
│   │   └── stories/             # Story components
│   └── package.json
└── docs/                        # Documentation
```

## Quick Start

### Start the FastAPI Backend

```bash
cd Internship/autoagents-backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Autoagents backend started on port 8000
```

### Start the Angular Frontend

```bash
cd Internship/autoagents-frontend
npm install
npm start
```

When the browser opens:
- The frontend runs at `http://localhost:4200`
- The backend API is available at `http://localhost:8000`
- API documentation is available at `http://localhost:8000/docs`

## Key Features

### Backend
- FastAPI with MongoDB for data persistence
- Three AI agents:
  - **Agent-1**: Generates project features
  - **Agent-2**: Generates user stories
  - **Agent-3**: Generates HLD/LLD/DBD Mermaid diagrams
- REST endpoints for projects, features, stories, and designs

### Frontend
- Angular 17 using standalone components and Signals
- Project wizard for creating new projects
- Workspace view with Mermaid diagram editor
- Design view with HLD/LLD/DBD tab switching

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List all projects |
| POST | `/projects` | Create a new project |
| GET | `/projects/{project_id}` | Get project details |
| POST | `/projects/{project_id}/designs/generate` | Generate HLD/LLD/DBD designs |
| GET | `/projects/{project_id}/designs` | Get latest designs |
| GET | `/projects/{project_id}/features` | List project features |
| GET | `/projects/{project_id}/stories` | List project stories |

## Environment Setup

Set the following environment variables:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export MONGO_URI="mongodb://localhost:27017"
export MONGO_DB_NAME="autoagents"
```

## Development

- Backend auto-reloads on code changes when run with `--reload`
- Frontend hot-reloads in development mode
- Both servers run simultaneously for full-stack development

## License

This codebase is supplied for educational and prototyping purposes.
