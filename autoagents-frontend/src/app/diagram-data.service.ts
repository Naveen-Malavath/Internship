/**
 * Service to provide predefined diagram templates (HLD, LLD, DBD)
 * These diagrams are embedded directly in the component for simplicity
 */

export class DiagramDataService {
  static getHLDDiagram(): string {
    return `graph TD
    %% ============================================
    %% User Interface Layer
    %% ============================================
    User((👤 User))
    
    subgraph Frontend["🎨 Frontend - Angular SPA"]
        direction TB
        WebApp(🌐 Web Application)
        ChatUI(💬 Chat Interface)
        WorkspaceUI(📊 Workspace View)
        WizardUI(🧙 Project Wizard)
        FeatureForm(📝 Feature Form)
        StoryForm(📖 Story Form)
    end
    
    %% ============================================
    %% API Gateway Layer
    %% ============================================
    APIGateway{{🔌 FastAPI Backend<br/>API Gateway}}
    
    %% ============================================
    %% Service Layer
    %% ============================================
    subgraph BackendServices["⚙️ Backend Services"]
        direction TB
        AuthService[🔐 Authentication Service]
        ProjectService[📁 Project Service]
        StateService[🔄 State Management Service]
    end
    
    %% ============================================
    %% AI Agent Layer
    %% ============================================
    subgraph AIAgents["🤖 AI Agents"]
        direction TB
        Agent1(🤖 Agent 1<br/>Feature Generator)
        Agent2(📚 Agent 2<br/>Story Builder)
        Agent3(📈 Agent 3<br/>Diagram Visualizer)
    end
    
    %% ============================================
    %% Data Layer
    %% ============================================
    subgraph DataStorage["💾 Data Storage"]
        direction TB
        UserDB[(🗄️ User Database)]
        ProjectDB[(🗂️ Project Database)]
        ChatCache[(💭 Browser LocalStorage<br/>Chat History)]
        WorkspaceCache[(📦 Browser State<br/>Workspace Items)]
    end
    
    %% ============================================
    %% External Systems
    %% ============================================
    subgraph External["🌐 External Services"]
        direction TB
        LLMProvider(🧠 OpenAI / LLM Provider)
        StatusService(📡 Status Service<br/>Right Now Endpoint)
    end
    
    %% ============================================
    %% Connections - User to Frontend
    %% ============================================
    User -->|Interacts| WebApp
    WebApp --> ChatUI
    WebApp --> WorkspaceUI
    WebApp --> WizardUI
    ChatUI --> FeatureForm
    ChatUI --> StoryForm
    
    %% ============================================
    %% Connections - Frontend to Backend
    %% ============================================
    ChatUI -->|POST /agent/features| APIGateway
    ChatUI -->|POST /agent/stories| APIGateway
    ChatUI -->|POST /agent/visualizer| APIGateway
    WizardUI -->|POST /project/create| APIGateway
    WebApp -->|GET /status/right-now| APIGateway
    WebApp -->|POST /chat| APIGateway
    
    %% ============================================
    %% Connections - API Gateway to Services
    %% ============================================
    APIGateway -->|Route Request| AuthService
    APIGateway -->|Route Request| ProjectService
    APIGateway -->|Route Request| StateService
    
    %% ============================================
    %% Connections - Services to Agents
    %% ============================================
    ProjectService -->|Invoke| Agent1
    ProjectService -->|Invoke| Agent2
    ProjectService -->|Invoke| Agent3
    
    %% ============================================
    %% Connections - Agents to External
    %% ============================================
    Agent1 ==>|LLM API Call| LLMProvider
    Agent2 ==>|LLM API Call| LLMProvider
    Agent3 ==>|LLM API Call| LLMProvider
    
    %% ============================================
    %% Connections - Services to Data
    %% ============================================
    AuthService -->|CRUD Operations| UserDB
    ProjectService -->|CRUD Operations| ProjectDB
    StateService -->|Cache| WorkspaceCache
    
    %% ============================================
    %% Connections - Frontend to Local Storage
    %% ============================================
    ChatUI -.->|Store Messages| ChatCache
    ChatUI -.->|Retrieve History| ChatCache
    WorkspaceUI -.->|Store Items| WorkspaceCache
    WorkspaceUI -.->|Retrieve Items| WorkspaceCache
    
    %% ============================================
    %% Connections - Status Service
    %% ============================================
    APIGateway -->|Health Check| StatusService
    
    %% ============================================
    %% Styling with Enhanced Colors
    %% ============================================
    classDef userClass fill:#4a90e2,stroke:#2c5282,stroke-width:3px,color:#fff,font-weight:bold
    classDef uiLayer fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff,font-weight:500
    classDef apiLayer fill:#f59e0b,stroke:#d97706,stroke-width:3px,color:#fff,font-weight:bold
    classDef serviceLayer fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff,font-weight:500
    classDef agentLayer fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff,font-weight:500
    classDef dataLayer fill:#f97316,stroke:#ea580c,stroke-width:2px,color:#fff,font-weight:500
    classDef externalLayer fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff,font-weight:500
    classDef frontendSubgraph fill:#dbeafe,stroke:#3b82f6,stroke-width:2px
    classDef backendSubgraph fill:#d1fae5,stroke:#10b981,stroke-width:2px
    classDef agentSubgraph fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px
    classDef dataSubgraph fill:#fed7aa,stroke:#f97316,stroke-width:2px
    classDef externalSubgraph fill:#fee2e2,stroke:#ef4444,stroke-width:2px
    
    class User userClass
    class WebApp,ChatUI,WorkspaceUI,WizardUI,FeatureForm,StoryForm uiLayer
    class APIGateway apiLayer
    class AuthService,ProjectService,StateService serviceLayer
    class Agent1,Agent2,Agent3 agentLayer
    class UserDB,ProjectDB,ChatCache,WorkspaceCache dataLayer
    class LLMProvider,StatusService externalLayer
    
    style Frontend fill:#dbeafe,stroke:#3b82f6,stroke-width:2px,stroke-dasharray: 5 5
    style BackendServices fill:#d1fae5,stroke:#10b981,stroke-width:2px,stroke-dasharray: 5 5
    style AIAgents fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px,stroke-dasharray: 5 5
    style DataStorage fill:#fed7aa,stroke:#f97316,stroke-width:2px,stroke-dasharray: 5 5
    style External fill:#fee2e2,stroke:#ef4444,stroke-width:2px,stroke-dasharray: 5 5`;
  }

  static getLLDDiagram(features: any[] = [], stories: any[] = [], prompt: string = ''): string {
    // Escape text for Mermaid - ensure proper formatting
    const escapeMermaid = (text: string): string => {
      if (!text) return 'Untitled';
      // Remove special Mermaid characters and truncate
      const cleaned = text
        .replace(/[\[\](){}<>\"]/g, '')
        .replace(/\n/g, ' ')
        .replace(/\s+/g, ' ')
        .trim()
        .substring(0, 45);
      return cleaned || 'Untitled';
    };

    // Generate feature components based on actual features
    let featureComponents = '';
    let featureConnections = '';
    
    if (features.length > 0) {
      features.forEach((feature, idx) => {
        const featureId = `Feature${idx + 1}`;
        const featureName = escapeMermaid(feature.title || `Feature ${idx + 1}`);
        featureComponents += `        ${featureId}[${featureName}]\n`;
        featureConnections += `    AppRoot --> ${featureId}\n`;
      });
    } else {
      featureComponents = '        Feature1[Feature Component]\n';
      featureConnections = '    AppRoot --> Feature1\n';
    }

    // Generate story components based on actual stories
    let storyComponents = '';
    let storyConnections = '';
    
    if (stories.length > 0) {
      stories.forEach((story, idx) => {
        const storyId = `Story${idx + 1}`;
        const storyName = escapeMermaid(story.userStory || `Story ${idx + 1}`);
        storyComponents += `        ${storyId}[${storyName}]\n`;
        
        // Find parent feature
        if (features.length > 0) {
          const featureIdx = features.findIndex(f => f.title === story.featureTitle);
          if (featureIdx >= 0) {
            storyConnections += `    Feature${featureIdx + 1} --> ${storyId}\n`;
          } else {
            storyConnections += `    AppRoot --> ${storyId}\n`;
          }
        } else {
          storyConnections += `    Feature1 --> ${storyId}\n`;
        }
      });
    }

    // Build feature and story class names for styling
    let featureClassNames = '';
    let storyClassNames = '';
    
    if (features.length > 0) {
      featureClassNames = features.map((_, idx) => `Feature${idx + 1}`).join(',');
    }
    
    if (stories.length > 0) {
      storyClassNames = stories.map((_, idx) => `Story${idx + 1}`).join(',');
    }

    return `graph TD
    %% ============================================
    %% Root Component
    %% ============================================
    AppRoot["🏠 App Root Component<br/>State Management"]
    
    %% ============================================
    %% Main UI Components
    %% ============================================
    subgraph MainUI["🎨 Main User Interface"]
        direction TB
        ChatComponent("💬 Chat Component")
        WorkspaceComponent("📊 Workspace View")
        WizardComponent("🧙 Project Wizard")
    end
    
    %% ============================================
    %% Feature Components
    %% ============================================
    subgraph Features["✨ Feature Components"]
        direction TB
${featureComponents}    end
    
    %% ============================================
    %% Story Components
    %% ============================================
    subgraph Stories["📚 Story Components"]
        direction TB
${storyComponents}    end
    
    %% ============================================
    %% State Signals
    %% ============================================
    subgraph StateSignals["⚡ State Signals"]
        direction TB
        ChatState("💬 Chat Messages")
        FeaturesState("✨ Features")
        StoriesState("📚 Stories")
        DiagramsState("📈 Diagrams")
    end
    
    %% ============================================
    %% Services
    %% ============================================
    subgraph Services["🔧 Angular Services"]
        direction TB
        AgentService["🌐 Agent Service"]
        LocalStorageService["💾 LocalStorage Service"]
        StateService["🔄 State Service"]
    end
    
    %% ============================================
    %% Backend API
    %% ============================================
    BackendAPI["🚀 FastAPI Backend"]
    
    %% ============================================
    %% Component to Root Connections
    %% ============================================
    AppRoot --> ChatComponent
    AppRoot --> WorkspaceComponent
    AppRoot --> WizardComponent
    
    %% ============================================
    %% Feature and Story Connections
    %% ============================================
${featureConnections}${storyConnections}
    
    %% ============================================
    %% State Signal Connections
    %% ============================================
    AppRoot -.-> ChatState
    AppRoot -.-> FeaturesState
    AppRoot -.-> StoriesState
    AppRoot -.-> DiagramsState
    
    ChatComponent -.-> ChatState
    ChatComponent -.-> FeaturesState
    ChatComponent -.-> StoriesState
    
    WorkspaceComponent -.-> FeaturesState
    WorkspaceComponent -.-> StoriesState
    
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
    StateService -.-> ChatState
    StateService -.-> FeaturesState
    StateService -.-> StoriesState
    StateService -.-> DiagramsState
    
    %% ============================================
    %% API Connections
    %% ============================================
    AgentService --> BackendAPI
    AgentService -->|POST /agent/features| BackendAPI
    AgentService -->|POST /agent/stories| BackendAPI
    AgentService -->|POST /agent/visualizer| BackendAPI
    
    %% ============================================
    %% Enhanced Styling with Colors
    %% ============================================
    classDef rootComponent fill:#7c3aed,stroke:#5b21b6,stroke-width:4px,color:#fff,font-weight:bold
    classDef uiComponent fill:#3b82f6,stroke:#1e40af,stroke-width:2px,color:#fff,font-weight:500
    classDef featureComponent fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff,font-weight:500
    classDef storyComponent fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff,font-weight:500
    classDef stateSignal fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff,font-weight:500
    classDef service fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff,font-weight:500
    classDef api fill:#ef4444,stroke:#dc2626,stroke-width:3px,color:#fff,font-weight:bold
    
    class AppRoot rootComponent
    class ChatComponent,WorkspaceComponent,WizardComponent uiComponent
    ${featureClassNames ? `class ${featureClassNames} featureComponent` : ''}
    ${storyClassNames ? `class ${storyClassNames} storyComponent` : ''}
    class ChatState,FeaturesState,StoriesState,DiagramsState stateSignal
    class AgentService,LocalStorageService,StateService service
    class BackendAPI api
    
    style MainUI fill:#dbeafe,stroke:#3b82f6,stroke-width:2px,stroke-dasharray: 5 5
    style Features fill:#d1fae5,stroke:#10b981,stroke-width:2px,stroke-dasharray: 5 5
    style Stories fill:#fef3c7,stroke:#f59e0b,stroke-width:2px,stroke-dasharray: 5 5
    style StateSignals fill:#ede9fe,stroke:#8b5cf6,stroke-width:2px,stroke-dasharray: 5 5
    style Services fill:#d1fae5,stroke:#10b981,stroke-width:2px,stroke-dasharray: 5 5`;
  }

  static getDBDDiagram(): string {
    return `erDiagram
    USERS ||--o{ PROJECTS : "owns"
    PROJECTS ||--o{ FEATURES : "includes"
    PROJECTS ||--o{ STORIES : "contains"
    PROJECTS ||--o{ DIAGRAMS : "has"
    FEATURES ||--o{ STORIES : "contains"
    
    USERS {
        uuid id PK "🔑 Primary Key"
        varchar email UK "📧 Unique Email"
        varchar password_hash "🔒 Encrypted"
        varchar name "👤 Display Name"
        timestamp created_at "📅 Created"
        timestamp updated_at "🔄 Updated"
    }
    
    PROJECTS {
        uuid id PK "🔑 Primary Key"
        uuid owner_id FK "👤 Owner"
        varchar name "📁 Project Name"
        text idea_prompt "💡 Original Idea"
        varchar status "📊 Status"
        timestamp created_at "📅 Created"
        timestamp updated_at "🔄 Updated"
    }
    
    FEATURES {
        uuid id PK "🔑 Primary Key"
        uuid project_id FK "📁 Project"
        varchar title "📋 Feature Title"
        text description "📝 Description"
        text acceptance_criteria "✅ Criteria"
        varchar source "🤖 Source"
        varchar status "📊 Status"
        timestamp created_at "📅 Created"
        timestamp updated_at "🔄 Updated"
    }
    
    STORIES {
        uuid id PK "🔑 Primary Key"
        uuid feature_id FK "📋 Feature"
        uuid project_id FK "📁 Project"
        text user_story "👤 User Story"
        text acceptance_criteria "✅ Criteria"
        text implementation_notes "📝 Notes"
        varchar status "📊 Status"
        timestamp created_at "📅 Created"
        timestamp updated_at "🔄 Updated"
    }
    
    DIAGRAMS {
        uuid id PK "🔑 Primary Key"
        uuid project_id FK "📁 Project"
        text mermaid_source "📈 Mermaid Code"
        text svg_cache "🖼️ SVG Cache"
        timestamp created_at "📅 Created"
        timestamp updated_at "🔄 Updated"
    }`;
  }
}

