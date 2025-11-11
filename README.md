# AutoAgents Full-Stack Workspace

This branch aggregates every feature branch into one cohesive workspace. It contains:

- **FastAPI backend** in `autoagents-backend/` (workspace-first API consumed by the agents).
- **Workspace Angular app** in `autoagents-frontend/` (feature planning UI produced by Agent‑1 and Agent‑2).
- **FEBE Angular 17 chat experience** at the repository root (`src/`, `angular.json`, etc.).
- Extensive documentation, guides, and scripts authored across branches.

Use this document as your single reference when working from `A2-stories`.

---

## Prerequisites

| Tool | Version |
| --- | --- |
| Node.js | 18+ (devcontainer currently exposes 24.11.0) |
| npm | 9+ |
| Python | 3.10+ (workspace image ships with 3.14.0) |
| PowerShell | 7+ on Windows (required for helper scripts) |

---

## Backend – FastAPI (`autoagents-backend/`)

```powershell
cd autoagents-backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

Key endpoints used by the frontends:

- `GET /` – Health check
- `GET /status/right-now` – LangChain-generated status summary
- `POST /chat` – Accepts `{ "message": "..." }` and streams an AI-crafted reply

On successful startup you should see:

```
INFO:     Autoagents backend started on port 8000
```

---

## Frontend Option 1 – Workspace UI (`autoagents-frontend/`)

This Angular workspace powers feature planning: project wizard, workspace views, and Agent‑1/Agent‑2 forms.

```powershell
cd autoagents-frontend
npm install
npm start
```

When the server opens (`http://localhost:4200`):

- The devtools console logs `Connecting to backend at http://localhost:8000`.
- The **Right Now** panel renders LangChain responses from `/status/right-now`.
- Panels for Login, Sign Up, Gmail, Microsoft Teams, etc. appear on the landing view.

---

## Frontend Option 2 – FEBE Chat Experience (root Angular app)

The FEBE branch contributes a standalone Angular 17 chatbot with a polished UI.

```powershell
cd Internship        # repository root
npm install          # installs dependencies defined in package.json
npm start            # launches Angular dev server on http://localhost:4200
```

### Highlighted Features

- 🔐 **Authentication UX** – email/password login, password toggle, Google sign-in ready UI, persistent sessions (localStorage).
- 💬 **Conversation Management** – multiple chats, history, timestamps, loading indicators, auto-scroll.
- 🎨 **Modern Design** – gradient theme, responsive layout, smooth animations, collapsible sidebar, suggestion chips.
- 🧩 **Extensible Services** – `AuthService` and `ChatService` use localStorage today but can be swapped for real APIs.

To connect to a real AI endpoint, edit `src/app/services/chat.service.ts` and replace the `generateResponse()` placeholder with HTTP calls to your provider (OpenAI, Anthropic, etc.).

---

## Documentation & Scripts (from FEBE branch)

The root directory now includes comprehensive onboarding material:

- `START_HERE.md`, `SETUP_GUIDE.md`, `INSTALLATION_GUIDE.md` – environment setup walkthroughs.
- `FEATURES.md`, `QUICK_REFERENCE.md`, `AI_AGENTS_ECOMMERCE_STACK.md` – architecture and capability overviews.
- `CHANGELOG.md`, `DEBUG_GUIDE.md` – change history and troubleshooting.
- `install-angular-fastapi-stack.ps1`, `install-enterprise-stack.ps1` – scripted installers.

Refer to these files whenever you need deeper context or automation.

---

## Repository Structure

```
Internship/
├── autoagents-backend/
│   └── app/
│       ├── agents.py
│       ├── main.py
│       ├── storage.py
│       └── data/
│           ├── agent1_features.json
│           ├── agent_snapshot.json
│           ├── visualization.dot
│           └── visualization.mermaid
│
├── autoagents-frontend/
│   └── src/app/...   # Workspace/project wizard UI
│
├── src/              # FEBE chat application (Angular 17)
│   └── app/
│       ├── components/
│       ├── services/
│       ├── guards/
│       └── models/
│
├── docs & scripts    # START_HERE.md, QUICK_REFERENCE.md, etc.
└── README.md         # You are here
```

Both Angular projects manage their own dependencies (`autoagents-frontend/package.json` and root `package.json`). Install dependencies in the directory you plan to run.

---

## Working With Multiple Frontends

You can run both Angular apps simultaneously:

1. Start the FastAPI backend.
2. Terminal A: `cd autoagents-frontend && npm start`.
3. Terminal B: from the repo root `npm start` to launch the FEBE chat UI.

Each project listens on its own dev server and may call the backend on `http://localhost:8000`.

---

## Branch Reference

| Branch | Purpose |
| --- | --- |
| `main` | Workspace-first stack (backend + workspace frontend) |
| `A1features`, `Agent-2-stories`, `FE&BE`, `FEBE` | Original agent branches |
| `A2-stories` | Aggregation branch that merges everything (current branch) |

Create future work off `A2-stories` so you inherit every component by default. Always commit merged results and update documentation (e.g., append to `CHANGELOG.md`).

---

## Support & Ownership

- **Agent‑1** – feature definitions and workspace wizard (`FEATURES.md`, `autoagents-frontend/`).
- **Agent‑2** – story documentation and technical tasks (`autoagents-frontend/`, docs).
- **FEBE Team** – standalone chat UI, setup scripts, onboarding guides.
- **Backend** – shared FastAPI services in `autoagents-backend/`.

Consult the documentation bundle or reach out to the respective owners if questions arise. Enjoy building the AutoAgents ecosystem!
