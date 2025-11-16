# AutoAgents Backend Low-Level Design (LLD)

---

## 1. Backend Architecture Overview

### Routers
- Split by domain under `app/routers/` (`auth.py`, `projects.py`, `features.py`, `stories.py`, `diagram.py`, `debug.py`).
- Each router defines URL prefix + tags and only contains HTTP handlers and request validation.

### Models (Pydantic)
- Request/response schemas stored in `app/models.py`.
- Separate internal schemas (Mongo documents) from response DTOs to avoid leaking ObjectIds.
- Use `ConfigDict` with `populate_by_name=True` for camelCase compatibility with Angular.

### Database layer (Motor + `get_database()`)
- `app/db.py` exposes:
  - `connect_to_mongo()` / `close_mongo_connection()` to lifecycle-manage `AsyncIOMotorClient`.
  - `get_database()` returning the active `AsyncIOMotorDatabase`.
- Collections: `users`, `projects`, `features`, `stories`, `diagrams`.
- Helper functions in `app/repositories/*.py` encapsulate CRUD logic per collection.

### Services for agents
- `app/services/agent_feature_service.py`, `agent_story_service.py`, `agent_diagram_service.py`.
- Each service orchestrates prompt building, LLM invocation, and Mongo persistence.
- Uses dependency-injected LLM client (OpenAI/Claude) for easy mocking.

### Middleware
- CORS middleware enabling `http://localhost:4200`.
- Authentication middleware (JWT) verifying bearer token, populating `request.state.user_id`.
- Logging middleware for request tracing (optional but recommended).

### Error Handling
- Custom exception classes (`AuthError`, `ValidationError`, `AgentError`, `DatabaseError`).
- Central `exception_handlers.py` maps domain exceptions to HTTP responses with consistent JSON:
  ```json
  { "error": { "code": "AUTH_INVALID", "message": "...", "details": {} } }
  ```
- Logging occurs at handler level before returning response.

---

## 2. API Endpoints (FULL list)

### Auth

#### 2.1 Login
- **Endpoint Template:** `/auth/login`
- **Verb:** POST
- **Purpose:** Authenticate a user and issue JWT access token.
- **MongoDB Collections Used:** `users`
- **Input:** `LoginRequest` `{ email, password }`
- **Process Logic:**
  1. Fetch user by email.
  2. Verify password hash (argon2/bcrypt).
  3. Generate JWT with user_id, expiry.
  4. Return token + user profile snippet.
- **Output:** `{ accessToken, user: { id, email, name } }`
- **Error Cases:** 401 invalid credentials; 422 malformed request.

#### 2.2 Register
- **Endpoint Template:** `/auth/register`
- **Verb:** POST
- **Purpose:** Create new user account.
- **MongoDB Collections Used:** `users`
- **Input:** `UserCreate` `{ email, password, name }`
- **Process Logic:**
  1. Ensure email uniqueness.
  2. Hash password.
  3. Insert user document with timestamps.
  4. Return created user (without password).
- **Output:** `{ id, email, name, createdAt }`
- **Error Cases:** 409 if email exists; 422 for validation.

### Projects

#### 2.3 Create Project
- **Endpoint Template:** `/projects`
- **Verb:** POST
- **Purpose:** Persist a new project seed from user prompt.
- **MongoDB Collections Used:** `projects`
- **Input:** `ProjectCreate` `{ title, prompt, methodology?, industry? }`
- **Process Logic:**
  1. Require authenticated user (from JWT).
  2. Build document with `status="created"` and `created_at`.
  3. Insert into Mongo; return inserted record.
- **Output:** `{ id, userId, title, prompt, status, createdAt }`
- **Error Cases:** 401 unauthenticated; 422 invalid payload.

#### 2.4 Get Project by ID
- **Endpoint Template:** `/projects/{project_id}`
- **Verb:** GET
- **Purpose:** Retrieve project details plus optionally computed aggregates.
- **MongoDB Collections Used:** `projects`, `features`, `stories`, `diagrams`
- **Input:** Path `project_id`
- **Process Logic:**
  1. Validate `project_id` belongs to requesting user.
  2. Fetch project document.
  3. Optionally load feature/story counts and recent diagram timestamp.
- **Output:** Project DTO with metadata.
- **Error Cases:** 404 if not found or unauthorized; 400 invalid id format.

#### 2.5 Get Projects by User
- **Endpoint Template:** `/projects/user/{user_id}`
- **Verb:** GET
- **Purpose:** List all projects for a given user.
- **MongoDB Collections Used:** `projects`
- **Input:** Path `user_id` (must equal JWT user or admin).
- **Process Logic:**
  1. Authorize access.
  2. Query projects sorted by `created_at desc`.
  3. Map to lightweight card DTOs.
- **Output:** `[ { id, title, status, createdAt } ]`
- **Error Cases:** 403 unauthorized; 404 none found (optional).

### Agent-1: Features

#### 2.6 Generate Features
- **Endpoint Template:** `/projects/{project_id}/features/generate`
- **Verb:** POST
- **Purpose:** Invoke Agent-1 to generate feature list for project.
- **MongoDB Collections Used:** `projects`, `features`
- **Input:** `{ promptOverride?, regenerate?, previousRunId? }`
- **Process Logic:**
  1. Confirm project ownership.
  2. Build effective prompt (project prompt + overrides).
  3. Call Agent-1 service -> returns feature specs + run metadata.
  4. Upsert features collection (mark previous ones obsolete if regenerate).
  5. Return generated features with run id.
- **Output:** `{ runId, features: [FeatureModel], message }`
- **Error Cases:** 409 agent busy; 503 LLM failure; 404 project missing.

#### 2.7 List Features
- **Endpoint Template:** `/projects/{project_id}/features`
- **Verb:** GET
- **Purpose:** Fetch approved features for project.
- **MongoDB Collections Used:** `features`
- **Input:** Path `project_id`, optional query `status`.
- **Process Logic:**
  1. Authorize user.
  2. Query `features` with filters, sorted by priority/index.
  3. Map to DTOs.
- **Output:** `[FeatureModel]`
- **Error Cases:** 404 project or features missing.

### Agent-2: Stories

#### 2.8 Generate Stories
- **Endpoint Template:** `/projects/{project_id}/stories/generate`
- **Verb:** POST
- **Purpose:** Produce user stories for approved features.
- **MongoDB Collections Used:** `features`, `stories`
- **Input:** `{ featureIds?, regenerate?, previousRunId? }`
- **Process Logic:**
  1. Verify project ownership.
  2. Determine target features (subset or all approved).
  3. Build prompt from feature specs.
  4. Invoke Agent-2 service → returns stories per feature.
  5. Persist stories (replace existing if regenerate).
  6. Return saved stories and run id.
- **Output:** `{ runId, stories: [StoryModel], message }`
- **Error Cases:** 422 if no eligible features; 503 LLM error.

#### 2.9 List Stories
- **Endpoint Template:** `/projects/{project_id}/stories`
- **Verb:** GET
- **Purpose:** Retrieve stories grouped by feature.
- **MongoDB Collections Used:** `stories`
- **Input:** Path `project_id`, optional feature filter.
- **Process Logic:**
  1. Authorize user.
  2. Query stories; group by `feature_id`.
  3. Return structured array.
- **Output:** `[StoryModel]`
- **Error Cases:** 404 if project missing.

### Agent-3: Diagram

#### 2.10 Generate Diagram
- **Endpoint Template:** `/projects/{project_id}/diagram/generate`
- **Verb:** POST
- **Purpose:** Create Mermaid diagram based on features & stories.
- **MongoDB Collections Used:** `features`, `stories`, `diagrams`
- **Input:** `{ regenerate?, previousRunId?, customPrompt? }`
- **Process Logic:**
  1. Authorize user.
  2. Load approved features + stories.
  3. Build prompt for Agent-3.
  4. Call service to generate mermaid (and optional callouts).
  5. Upsert `diagrams` collection storing mermaid text, optional SVG cache, timestamps.
  6. Return diagram metadata.
- **Output:** `{ runId, diagram: DiagramModel, message }`
- **Error Cases:** 422 if missing data; 503 LLM failure.

#### 2.11 Get Diagram
- **Endpoint Template:** `/projects/{project_id}/diagram`
- **Verb:** GET
- **Purpose:** Retrieve latest saved diagram.
- **MongoDB Collections Used:** `diagrams`
- **Input:** Path `project_id`
- **Process Logic:**
  1. Authorize user.
  2. Find latest diagram document.
  3. Return mermaid string + metadata.
- **Output:** `DiagramModel`
- **Error Cases:** 404 if not generated yet.

---

## 3. Data Models (Pydantic Schemas)

```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=2, max_length=120)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    prompt: str = Field(min_length=10)
    methodology: Optional[str] = None
    industry: Optional[str] = None

class FeatureModel(BaseModel):
    id: str
    projectId: str = Field(alias="project_id")
    title: str
    description: str
    acceptanceCriteria: List[str] = Field(default_factory=list, alias="acceptance_criteria")
    status: str
    runId: Optional[str] = Field(default=None, alias="run_id")
    createdAt: str = Field(alias="created_at")

    model_config = ConfigDict(populate_by_name=True)

class StoryModel(BaseModel):
    id: str
    projectId: str = Field(alias="project_id")
    featureId: str = Field(alias="feature_id")
    featureTitle: str = Field(alias="feature_title")
    userStory: str = Field(alias="user_story")
    acceptanceCriteria: List[str] = Field(default_factory=list, alias="acceptance_criteria")
    implementationNotes: List[str] = Field(default_factory=list, alias="implementation_notes")
    status: str
    runId: Optional[str] = Field(default=None, alias="run_id")
    createdAt: str = Field(alias="created_at")

    model_config = ConfigDict(populate_by_name=True)

class DiagramModel(BaseModel):
    id: str
    projectId: str = Field(alias="project_id")
    runId: Optional[str] = Field(default=None, alias="run_id")
    mermaid: str
    svg: Optional[str] = None
    updatedAt: str = Field(alias="updated_at")

    model_config = ConfigDict(populate_by_name=True)
```

---

## 4. Agent Services Logic (LLD)

### 4.1 Agent-1 (Feature Generation)
- **Input:** `project_id`, base prompt, optional overrides, user id.
- **Prompt building:**
  1. Fetch project prompt + metadata.
  2. Combine with user overrides (e.g., focus areas, constraints).
  3. Append instructions for JSON feature output (title, description, acceptance criteria).
- **LLM call:** Send prompt to OpenAI/Claude using client wrapper with retry/backoff.
- **Output structure:** `{ run_id, summary, features: [ { title, description, acceptance_criteria } ] }`
- **Insert into Mongo:**
  - For each feature, insert document `{ project_id, title, description, acceptance_criteria, status="generated", run_id, created_at }`.
  - Mark previous features from same project as `status="superseded"` if regenerate flag set.

### 4.2 Agent-2 (Story Generation)
- **Input:** `project_id`, list of feature IDs, user id.
- **Prompt:**
  1. Retrieve feature specs (title, description, criteria).
  2. Build structured prompt instructing LLM to output stories grouped by feature.
  3. Include acceptance criteria and implementation notes sections.
- **LLM call:** Invoke Agent-2 client, parse JSON response.
- **Save stories:**
  - For each feature, create multiple story documents `{ project_id, feature_id, feature_title, user_story, acceptance_criteria, implementation_notes, status="generated", run_id, created_at }`.
  - Replace old stories if regenerate = true.
- **Return:** run id + list of saved stories mapped to `StoryModel`.

### 4.3 Agent-3 (Diagram Generation)
- **Input:** `project_id`, optional custom prompt.
- **Prompt:**
  1. Fetch approved features and stories summaries.
  2. Construct prompt with requested notation (Mermaid flowchart) and layout guidelines.
- **LLM call:** Invoke Agent-3 client; expect mermaid code plus optional callouts.
- **Save:** Upsert `diagrams` collection for project with `{ mermaid, svg_cache=None, run_id, updated_at }`.
- **Return:** run id + `DiagramModel`.

---

## 5. Error Handling
- **Validation errors (400/422):** Missing fields, invalid IDs, no approved features for stories. Response:
  ```json
  { "error": { "code": "VALIDATION_ERROR", "message": "...", "details": {...} } }
  ```
- **Auth errors (401/403):** Invalid credentials, expired token, accessing another user’s project.
- **Not Found (404):** Project/feature/story not owned by user.
- **Agent errors (502/503):** LLM failure, timeout. Response includes user-friendly retry message.
- **Database errors (500):** Connection issues surfaced with generic message, logged internally.

---

## 6. Security (JWT / Password Hashing)
- **Password hashing:** Use `passlib` or `bcrypt` when storing passwords. Never store plaintext.
- **JWT issuance:** On login/register, issue access token with:
  - `sub` = user id
  - `exp` = current time + configurable TTL (e.g., 1 hour)
  - Signed using HS256 and secret from environment.
- **Auth middleware:** Parse `Authorization: Bearer <token>`:
  1. Decode JWT; verify signature and expiry.
  2. Attach user id to request state for downstream handlers.
  3. Reject missing/invalid tokens with 401.
- **Endpoint protection:** All project/agent routes require valid JWT; only `/auth/*` and health/debug endpoints remain public (debug may be disabled in production).
- **Role handling:** Extend JWT payload with `role` if admin endpoints added later.

---

_Last updated: 2025-11-13_

