# Frontend Component Interaction Diagram

This diagram shows how Angular components interact and share state using signals.

```mermaid
graph TD
    %% ============================================
    %% Root Component
    %% ============================================
    AppRoot[App Root Component<br/>State Management with Signals]
    
    %% ============================================
    %% Main UI Components
    %% ============================================
    subgraph MainUI["Main User Interface"]
        ChatComponent[Chat Component<br/>Message Display & Input]
        WorkspaceComponent[Workspace View Component<br/>Features, Stories, Diagrams]
        WizardComponent[Project Wizard Component<br/>Step-by-Step Builder]
    end
    
    %% ============================================
    %% Form Components
    %% ============================================
    subgraph Forms["Form Components"]
        FeatureForm[Feature Form Component<br/>Create/Edit Features]
        StoryForm[Story Form Component<br/>Create/Edit Stories]
    end
    
    %% ============================================
    %% State Signals
    %% ============================================
    subgraph StateSignals["State Signals"]
        ChatState[Chat Messages Signal<br/>chatMessages()]
        FeaturesState[Features Signal<br/>approvedFeatures()]
        StoriesState[Stories Signal<br/>approvedStories()]
        DiagramsState[Diagrams Signal<br/>generatedDiagrams()]
        AgentStageState[Agent Stage Signal<br/>currentAgentStage()]
        WorkspaceState[Workspace Items Signal<br/>workspaceItems()]
    end
    
    %% ============================================
    %% Services
    %% ============================================
    subgraph Services["Angular Services"]
        AgentService[Agent Service<br/>HTTP Client]
        LocalStorageService[LocalStorage Service<br/>Browser Storage]
        StateService[State Service<br/>Signal Management]
    end
    
    %% ============================================
    %% Backend API
    %% ============================================
    BackendAPI[(FastAPI Backend<br/>REST Endpoints)]
    
    %% ============================================
    %% Component to Root Connections
    %% ============================================
    AppRoot --> ChatComponent
    AppRoot --> WorkspaceComponent
    AppRoot --> WizardComponent
    
    %% ============================================
    %% Component to Form Connections
    %% ============================================
    ChatComponent -->|Open Edit| FeatureForm
    ChatComponent -->|Open Edit| StoryForm
    WorkspaceComponent -->|Edit Item| FeatureForm
    WorkspaceComponent -->|Edit Item| StoryForm
    WizardComponent -->|Add Feature| FeatureForm
    
    %% ============================================
    %% State Signal Connections
    %% ============================================
    AppRoot -.->|Reads/Writes| ChatState
    AppRoot -.->|Reads/Writes| FeaturesState
    AppRoot -.->|Reads/Writes| StoriesState
    AppRoot -.->|Reads/Writes| DiagramsState
    AppRoot -.->|Reads/Writes| AgentStageState
    AppRoot -.->|Reads/Writes| WorkspaceState
    
    ChatComponent -.->|Reads| ChatState
    ChatComponent -.->|Triggers Updates| FeaturesState
    ChatComponent -.->|Triggers Updates| StoriesState
    
    WorkspaceComponent -.->|Reads| WorkspaceState
    WorkspaceComponent -.->|Updates| WorkspaceState
    
    WizardComponent -.->|Reads/Writes| FeaturesState
    WizardComponent -.->|Reads/Writes| StoriesState
    
    FeatureForm -.->|Writes| FeaturesState
    StoryForm -.->|Writes| StoriesState
    
    %% ============================================
    %% Service Connections
    %% ============================================
    AppRoot --> AgentService
    ChatComponent --> AgentService
    WizardComponent --> AgentService
    
    AppRoot --> LocalStorageService
    ChatComponent --> LocalStorageService
    WorkspaceComponent --> LocalStorageService
    
    AppRoot --> StateService
    StateService -.->|Manages| ChatState
    StateService -.->|Manages| FeaturesState
    StateService -.->|Manages| StoriesState
    StateService -.->|Manages| DiagramsState
    StateService -.->|Manages| AgentStageState
    StateService -.->|Manages| WorkspaceState
    
    %% ============================================
    %% API Connections
    %% ============================================
    AgentService -->|POST /agent/features| BackendAPI
    AgentService -->|POST /agent/stories| BackendAPI
    AgentService -->|POST /agent/visualizer| BackendAPI
    AgentService -->|POST /project/create| BackendAPI
    AgentService -->|GET /status/right-now| BackendAPI
    AgentService -->|POST /chat| BackendAPI
    
    %% ============================================
    %% Data Flow Annotations
    %% ============================================
    ChatComponent ==>|User Input| AppRoot
    ChatComponent ==>|Agent Response| AppRoot
    AppRoot ==>|Approved Items| WorkspaceComponent
    WizardComponent ==>|Completed Wizard| AppRoot
    FeatureForm ==>|Saved Feature| AppRoot
    StoryForm ==>|Saved Story| AppRoot
    
    %% ============================================
    %% Styling
    %% ============================================
    classDef rootComponent fill:#4a148c,stroke:#fff,stroke-width:3px,color:#fff
    classDef uiComponent fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef formComponent fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    classDef stateSignal fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef service fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef api fill:#ffebee,stroke:#b71c1c,stroke-width:2px
    
    class AppRoot rootComponent
    class ChatComponent,WorkspaceComponent,WizardComponent uiComponent
    class FeatureForm,StoryForm formComponent
    class ChatState,FeaturesState,StoriesState,DiagramsState,AgentStageState,WorkspaceState stateSignal
    class AgentService,LocalStorageService,StateService service
    class BackendAPI api
```

