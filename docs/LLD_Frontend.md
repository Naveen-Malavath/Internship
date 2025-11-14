# AutoAgents Frontend Low-Level Design (Angular)

---

## 1. Angular Application Architecture

### AppModule
- Root module bootstrapping `AppComponent`.
- Imports `BrowserModule`, `AppRoutingModule`, `HttpClientModule`, `AuthModule`, `ProjectModule`, `SharedModule`.
- Provides HTTP interceptors (JWT, error) and global services (AuthService, ProjectService, etc.).

### AppRoutingModule
- Defines top-level routes (lazy loads feature modules where applicable).
- Guards protected routes using `AuthGuard`.
- Redirects unknown paths to `/dashboard` (if authenticated) or `/login`.

### AuthModule
- Contains authentication components (`LoginComponent`, `RegisterComponent`) and related services.
- Imports `ReactiveFormsModule`, `SharedModule`.
- Exports components for router outlets.

### ProjectModule
- Houses project-related components (Dashboard, Chat, ProjectView, FeatureList, StoryList, DiagramView).
- Imports `CommonModule`, `ReactiveFormsModule`, `SharedModule`, `RouterModule`.
- Provides project-scoped services (FeatureService, StoryService, DiagramService) if needed.

### SharedModule
- Reusable UI elements: buttons, cards, layout components, toast service, loading spinner.
- Declares Tailwind utility wrappers (e.g., layout containers).
- Exports common directives/pipes (e.g., `RelativeTimePipe`).

---

## 2. Angular Routing Plan

| Route | Component | Guard |
|-------|-----------|-------|
| `/login` | `LoginComponent` | `AnonGuard` (redirect authenticated users) |
| `/register` | `RegisterComponent` | `AnonGuard` |
| `/dashboard` | `DashboardComponent` | `AuthGuard` |
| `/project/:id` | `ProjectViewComponent` (wrapper) | `AuthGuard` |
| `/project/:id/features` | `FeatureListComponent` | `AuthGuard` |
| `/project/:id/stories` | `StoryListComponent` | `AuthGuard` |
| `/project/:id/diagram` | `DiagramViewComponent` | `AuthGuard` |

Router lazily loads `ProjectModule` for `/dashboard` and `/project/:id/**` routes.

---

## 3. Components (FULL Detail)

### Auth

#### LoginComponent
- **Component Template:** `app-auth-login`
- **Purpose:** Authenticate user and navigate to dashboard.
- **Inputs:** None
- **Outputs:** Emits successful login event (optional) or navigates.
- **UI Elements:** Reactive form (email/password), submit button, link to register, error alert.
- **API Calls:** `AuthService.login(credentials)`
- **Interactions:** On submit → validates form → calls service → stores token → navigates.
- **Displayed Data:** Validation errors, API error messages.

#### RegisterComponent
- **Component Template:** `app-auth-register`
- **Purpose:** Register new user account.
- **Inputs:** None
- **Outputs:** Optionally emit `registered` event; auto-login or redirect to login.
- **UI Elements:** Reactive form (name, email, password, confirm password), submit button, link to login, success message.
- **API Calls:** `AuthService.register(payload)`
- **Interactions:** On submit → call service → show toast → navigate to login (or auto-login).
- **Displayed Data:** Form validation errors, API errors.

### Dashboard

#### DashboardComponent
- **Component Template:** `app-dashboard`
- **Purpose:** Display user projects and provide entry to chat/project creation.
- **Inputs:** None
- **Outputs:** `selectProject(projectId)` event.
- **UI Elements:** Header, “New Project” button, project cards list, chat panel toggle.
- **API Calls:** `ProjectService.getProjectsByUser(userId)`
- **Interactions:** Loads projects on init; clicking a project navigates to `/project/:id`.
- **Displayed Data:** Project title, status, created date. Empty state when no projects.

### Chat Input + Project Creation

#### ChatComponent
- **Component Template:** `app-chat`
- **Purpose:** Capture project prompt and coordinate generation pipeline.
- **Inputs:** Optional existing project context (for regenerate).
- **Outputs:** Emits project creation completion `{ projectId }`.
- **UI Elements:** Textarea for prompt, send button, messaging history area.
- **API Calls:** 
  - `ProjectService.createProject(prompt)`
  - `FeatureService.generateFeatures(projectId)`
  - `StoryService.generateStories(projectId)`
  - `DiagramService.generateDiagram(projectId)`
- **Interactions:**
  1. User enters prompt, hits send.
  2. Call create project → push message to chat history (statuses).
  3. Sequentially trigger features → stories → diagram services; update UI after each step.
  4. On completion, emit event and show success toast.
- **Displayed Data:** Chat transcripts (user prompt, agent status updates), progress spinner, errors.

### Project Details

#### ProjectViewComponent
- **Component Template:** `app-project-view`
- **Purpose:** Container for project details with tabs/navigation.
- **Inputs:** `projectId` from route.
- **Outputs:** None
- **UI Elements:** Breadcrumb, project summary header (title, status, created date), nav tabs for Features, Stories, Diagram, Chat.
- **API Calls:** `ProjectService.getProject(projectId)`
- **Interactions:** On init load project data; handles nav between child routes.
- **Displayed Data:** Project metadata, status badges, last updated info.

#### FeatureListComponent
- **Component Template:** `app-feature-list`
- **Purpose:** Display generated features with approval controls.
- **Inputs:** `projectId`
- **Outputs:** Events for `regenerate`, `approveFeature`, `dismissFeature`.
- **UI Elements:** List/grid of feature cards (title, description, acceptance criteria), approve/dismiss buttons, regenerate button.
- **API Calls:** 
  - `FeatureService.getFeatures(projectId)`
  - `FeatureService.generateFeatures(projectId)` (regenerate)
  - `FeatureService.approveFeature(featureId)` (future)
- **Interactions:** Fetch features on init; user can trigger regenerate; selection updates state.
- **Displayed Data:** Features grouped by status, run id, timestamps.

#### StoryListComponent
- **Component Template:** `app-story-list`
- **Purpose:** Display stories grouped by feature with approval UI.
- **Inputs:** `projectId`
- **Outputs:** Events for `regenerateStories`, `markApproved`, `dismissStory`.
- **UI Elements:** Accordion per feature, story cards (user story, acceptance criteria, implementation notes), regenerate button.
- **API Calls:** 
  - `StoryService.getStories(projectId)`
  - `StoryService.generateStories(projectId)` (regenerate)
- **Interactions:** Loads stories; buttons allow re-generation/approval.
- **Displayed Data:** Story copy, associated feature, status badges.

#### DiagramViewComponent
- **Component Template:** `app-diagram-view`
- **Purpose:** Show Mermaid diagram with regenerate/edit options.
- **Inputs:** `projectId`
- **Outputs:** `regenerateDiagram`, `saveEdits(mermaid)`
- **UI Elements:** Rendered mermaid (via `ngx-mermaid` or custom renderer), raw mermaid editor textarea, regenerate button, save button.
- **API Calls:** 
  - `DiagramService.getDiagram(projectId)`
  - `DiagramService.generateDiagram(projectId)`
  - `DiagramService.saveDiagram(projectId, mermaid)`
- **Interactions:** On init load diagram; allow user to edit; on regenerate call service and refresh view.
- **Displayed Data:** Mermaid diagram, updated timestamp, run id.

---

## 4. Angular Services (FULL Detail)

### AuthService
- **Purpose:** Handle authentication & token storage.
- **Methods:**
  - `login(request: LoginRequest): Observable<LoginResponse>` → `POST /auth/login`
  - `register(payload: UserCreate): Observable<User>` → `POST /auth/register`
  - `logout()` → clears token/local storage.
  - `getCurrentUser(): Observable<User | null>` → returns from cache or API.
- **Input/Output Models:** `LoginRequest`, `UserCreate`, `User`, `LoginResponse`.
- **Error Handling:** Catch errors, map to readable messages (`throwError(() => new AuthError(...))`).

### ProjectService
- **Purpose:** CRUD/project orchestration.
- **Methods:**
  - `createProject(prompt: string): Observable<Project>` → `POST /projects`
  - `getProject(id: string): Observable<Project>` → `GET /projects/{id}`
  - `getProjectsByUser(userId: string): Observable<Project[]>` → `GET /projects/user/{userId}`
- **Error Handling:** Use `catchError` to emit toast notifications and propagate error to components.

### FeatureService
- **Purpose:** Manage feature lifecycle.
- **Methods:**
  - `generateFeatures(projectId: string, options?): Observable<Feature[]>` → `POST /projects/{id}/features/generate`
  - `getFeatures(projectId: string): Observable<Feature[]>` → `GET /projects/{id}/features`
  - `(optional) approveFeature(featureId: string)`
- **Error Handling:** Provide fallback messages; use `retry` for transient errors if necessary.

### StoryService
- **Purpose:** Handle story generation and retrieval.
- **Methods:**
  - `generateStories(projectId: string, featureIds?): Observable<Story[]>` → `POST /projects/{id}/stories/generate`
  - `getStories(projectId: string): Observable<Story[]>` → `GET /projects/{id}/stories`
- **Error Handling:** Map backend error to user-friendly toast, log for debugging.

### DiagramService
- **Purpose:** Manage diagram generation and persistence.
- **Methods:**
  - `generateDiagram(projectId: string): Observable<Diagram>` → `POST /projects/{id}/diagram/generate`
  - `getDiagram(projectId: string): Observable<Diagram>` → `GET /projects/{id}/diagram`
  - `saveDiagram(projectId: string, mermaid: string): Observable<Diagram>` → `POST /projects/{id}/diagram` (if editing endpoint exists).
- **Error Handling:** Show error toast; optionally fallback to last known diagram.

---

## 5. Data Models (TypeScript Interfaces)

```ts
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Project {
  id: string;
  user_id: string;
  title: string;
  prompt: string;
  status: string;
  created_at: string;
  updated_at?: string;
}

export interface Feature {
  id: string;
  project_id: string;
  title: string;
  description: string;
  acceptance_criteria: string[];
  status: string;
  run_id?: string;
  created_at: string;
}

export interface Story {
  id: string;
  project_id: string;
  feature_id: string;
  feature_title: string;
  user_story: string;
  acceptance_criteria: string[];
  implementation_notes: string[];
  status: string;
  run_id?: string;
  created_at: string;
}

export interface Diagram {
  id: string;
  project_id: string;
  mermaid: string;
  svg?: string;
  run_id?: string;
  updated_at: string;
}
```

---

## 6. Component-by-Component Data Flow

1. **ChatComponent → ProjectService**
   - User enters prompt, clicks “Create”.
   - `ProjectService.createProject(prompt)` returns new `Project`.
   - Chat appends message “Project created”.

2. **ProjectService → FeatureService**
   - Chat triggers `FeatureService.generateFeatures(project.id)`.
   - Once resolved, chat updates UI and emits event to FeatureListComponent.

3. **FeatureService → StoryService**
   - After features ready, auto-call `StoryService.generateStories(project.id)`.
   - Update story list; handle partial failures.

4. **StoryService → DiagramService**
   - When stories generated, call `DiagramService.generateDiagram(project.id)`.
   - Diagram view updates with new mermaid graph.

5. **Shared state updates**
   - Use `ProjectStore` (RxJS `BehaviorSubject`) to broadcast updates to FeatureListComponent, StoryListComponent, DiagramViewComponent.
   - Each component subscribes and refreshes view.

---

## 7. Error Handling & UI States

| Page | Loading State | Error Handling | Empty State | Disabled Buttons |
|------|---------------|----------------|-------------|------------------|
| Login/Register | Spinner on submit | Show inline error (`mat-error`/Tailwind alert) | n/a | Submit disabled until form valid |
| Dashboard | Skeleton cards while loading | Toast + retry button | “No projects yet” card | “New Project” disabled while API pending |
| Chat | Spinner/typing indicator when backend processing | Toast + message appended “Failed to generate ...” | Placeholder “Start a conversation” | Send disabled when textarea empty |
| ProjectView | Skeleton header, tabs disabled until data load | Toast + navigate back | “Project not found” with back button | Tabs disabled until load |
| FeatureList | Loading cards / shimmer | Toast + show last known data | “No features generated” message | Regenerate button disabled while request pending |
| StoryList | Loading accordion | Toast | “No stories yet” message | Generate button disabled until features approved |
| DiagramView | Spinner + placeholder | Toast | “Diagram not generated” message | Regenerate disabled until stories exist |

All API errors should funnel through a centralized `NotificationService` displaying Tailwind-styled toasts.

---

## 8. Frontend–Backend Integration Checklist

- `POST /auth/login` – handled by `AuthService.login`
- `POST /auth/register` – `AuthService.register`
- `POST /projects` – `ProjectService.createProject`
- `GET /projects/{id}` – `ProjectService.getProject`
- `GET /projects/user/{userId}` – `ProjectService.getProjectsByUser`
- `POST /projects/{id}/features/generate` – `FeatureService.generateFeatures`
- `GET /projects/{id}/features` – `FeatureService.getFeatures`
- `POST /projects/{id}/stories/generate` – `StoryService.generateStories`
- `GET /projects/{id}/stories` – `StoryService.getStories`
- `POST /projects/{id}/diagram/generate` – `DiagramService.generateDiagram`
- `GET /projects/{id}/diagram` – `DiagramService.getDiagram`
- Optional: `POST /projects/{id}/diagram` (save edits)

Ensure JWT interceptor attaches tokens to all protected endpoints. Handle 401 responses by refreshing token or redirecting to `/login`.

---

_Last updated: 2025-11-13_

