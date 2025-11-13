# AutoAgents High-Level Design

## 1. Overview
AutoAgents is a simple assistant that turns a project idea into a basic delivery plan. The Angular web app guides the user through three AI steps:
- **Agent 1** turns the idea into feature concepts.
- **Agent 2** writes user stories for the features the user keeps.
- **Agent 3** creates diagrams that explain the scope.

Users can chat with the agents or follow a guided wizard. They can edit the AI output, approve the pieces they like, and add their own notes before sending everything to the workspace.

## 2. Architecture
- **Frontend**: Angular app in `src/app`. Uses signals to store state. Key pieces are the chat, workspace view, feature/story forms, and project wizard.
- **Backend**: FastAPI service (outside this repo) with `/agent/features`, `/agent/stories`, and `/agent/visualizer` endpoints. Each endpoint calls the matching agent and returns structured data.
- **State Sync**: Signals keep track of chat messages, selections, and workspace items. Approved work moves from chat → workspace → visualiser.
- **Storage**: Chat history lives in the browser for quick recall. Exporting workspace outputs is planned for later.

## 3. Key Frontend Modules
- `App` root component: Handles chat, agent stage changes, selections, and workspace updates.
- `workspace-view`: Shows approved features, stories, and diagrams. Lets users edit or remove items.
- `project/project-wizard`: Step-by-step project builder with AI help for templates, features, stories, and review.
- `features/feature-form` & `stories/story-form`: Pop-up forms for adding or editing content by hand.
- `docs/HLD.md`: This living design document.

## 4. Data Contracts
- **AgentFeatureSpec / AgentFeatureDetail**: Feature title, description, acceptance criteria, risks, and other notes.
- **AgentStorySpec**: User story text, acceptance criteria, implementation notes, and the feature it belongs to.
- **AgentFeatureResponse / AgentStoryResponse**: Data returned from the agents, including messages, generated content, and status flags such as `generated` or `approved`.
- **ProjectWizardSubmission**: Full project payload with template choice, workflow, project details, approved features/stories, and any uploads.

## 5. Interaction Flow
1. The user types a project idea in chat. Agent 1 returns a feature list and a run id.
2. The user keeps one or more features. The selection goes back to the backend.
3. The backend calls Agent 2 with the approved features. Agent 2 sends back user stories.
4. The user keeps the stories they like. Approved stories trigger Agent 3 to build Mermaid diagrams.
5. The workspace shows the selected features, stories, and diagrams. Users can still edit or remove them.
6. The project wizard follows the same logic and only enables “Next” when the user has kept something.

## 6. Deployment & Runtime
- **Dev**: Run `ng serve` and point it at a local FastAPI backend.
- **Prod build**: `ng build --configuration production` creates static files for hosting on a CDN or container.
- **Env configuration**: The backend URL is currently hardcoded (`http://localhost:8000`). Move this into environment files for different stages.

## 7. Security & Privacy Considerations
- Use HTTPS for all calls in production.
- Do not store credentials in the browser. Load tokens through secure configuration.
- Chat history stays on the device. Add clear/reset options and basic data policies.

## 8. Observability & Resilience
- Currently we log to the console. Plan to add structured logs with levels for production.
- Error handlers show assistant messages. Add retries or backoff hints where useful.
- The `rightNowStatus` banner can show backend health based on the `/status/right-now` endpoint.

## 9. Future Enhancements
- Add shared workspaces so multiple people can collaborate.
- Save approved items back to the backend for long-term storage.
- Track usage metrics to see how well the agents help.
- Grow automated tests to cover selection flows, the wizard, and error cases.

---
_Last updated: 2025-11-13_

