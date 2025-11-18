# AutoAgents Mermaid Diagrams

This directory contains comprehensive Mermaid diagrams for the AutoAgents system high-level design documentation.

## Diagram Overview

### 1. System Architecture Diagram (`01-system-architecture.md`)
Shows the complete system architecture including:
- Frontend Angular SPA components
- FastAPI backend services
- Three AI agents (Feature Generator, Story Builder, Diagram Visualizer)
- Data storage layers (Database, Browser Storage)
- External services (OpenAI/LLM Provider, Status Service)

### 2. User Journey Sequence Diagram (`02-user-journey-sequence.md`)
Illustrates the complete user interaction flow:
- Project idea input through chat
- Agent 1 feature generation and approval
- Agent 2 story generation and approval
- Agent 3 diagram generation
- Workspace view and editing

### 3. Component Interaction Diagram (`03-component-interaction.md`)
Details Angular frontend component relationships:
- Root App component and state management
- Main UI components (Chat, Workspace, Wizard)
- Form components (Feature Form, Story Form)
- State signals and service dependencies

### 4. State Flow Diagram (`04-state-flow.md`)
Shows state transitions for the approval workflow:
- Input phase → Feature approval → Story generation → Story approval → Diagram generation → Workspace

### 5. Project Wizard Flow Diagram (`05-project-wizard-flow.md`)
Step-by-step wizard flow:
- Template selection → Project details → AI assist → Features → Stories → Review → Submit

### 6. Data Flow Diagram (`06-data-flow.md`)
Data movement through the system:
- User input → Frontend processing → API communication → Backend processing → Agent processing → Storage → Display

## Usage

These diagrams can be:
1. Embedded directly in Markdown files (GitHub, GitLab, etc. support Mermaid)
2. Rendered using Mermaid Live Editor: https://mermaid.live/
3. Exported as images using Mermaid CLI or online tools
4. Integrated into documentation tools that support Mermaid

## Color Coding Legend

- **UI Layer** (Light Blue): User interface components
- **API Layer** (Light Yellow): API gateway and routing
- **Service Layer** (Light Green): Business logic services
- **Agent Layer** (Light Purple): AI agents
- **Data Layer** (Light Orange): Data storage
- **External Layer** (Light Red): External services

## Maintenance

When updating these diagrams:
1. Keep naming consistent with codebase
2. Update all related diagrams if architecture changes
3. Maintain color coding standards
4. Add comments for complex flows
5. Ensure diagrams remain readable at different zoom levels

