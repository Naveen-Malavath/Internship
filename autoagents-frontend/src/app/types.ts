export type AgentFeatureSpec = {
  title: string;
  description: string;
  acceptanceCriteria: string[];
  detail?: AgentFeatureDetail;
};

export type AgentStorySpec = {
  featureTitle: string;
  userStory: string;
  acceptanceCriteria: string[];
  implementationNotes: string[];
};

export type ChatMessage = {
  sender: 'user' | 'assistant';
  text: string;
  agent?: 'agent1' | 'agent2';
  features?: AgentFeatureSpec[];
  stories?: AgentStorySpec[];
  runId?: string | null;
};

export type AgentFeatureRequestPayload = {
  prompt: string;
  decision?: Agent1Decision;
  run_id?: string;
  features?: AgentFeatureSpec[];
};

export type AgentFeatureResponse = {
  run_id: string;
  summary?: string | null;
  features: AgentFeatureSpec[];
  message: string;
  decision: 'generated' | 'kept';
};

export type AgentStoryRequestPayload = {
  prompt: string;
  features: AgentFeatureSpec[];
  stories?: AgentStorySpec[];
  decision?: Agent2Decision;
  run_id?: string;
};

export type AgentStoryResponse = {
  run_id: string;
  summary?: string | null;
  stories: AgentStorySpec[];
  message: string;
  decision: 'generated' | 'kept';
};

export type AgentVisualizationRequestPayload = {
  prompt?: string;
  features?: AgentFeatureSpec[];
  stories?: AgentStorySpec[];
  diagramType?: string; // 'hld' | 'lld' | 'database'
};

export type AgentVisualizationResponse = {
  run_id: string;
  summary: string;
  diagrams: {
    mermaid: string;
    dot: string;
    mermaidPath?: string | null;
    dotPath?: string | null;
    mermaidUpdatedAt?: string | null;
    dotUpdatedAt?: string | null;
  };
  callouts: string[];
  message: string;
};

export type MermaidAssetResponse = {
  mermaid: string;
  path?: string | null;
  updatedAt?: string | null;
};

export type MermaidAssetUpdatePayload = {
  mermaid: string;
};

export type Agent1Decision = 'again' | 'keep' | 'keep_all';
export type Agent2Decision = 'again' | 'keep';

export type HistoryEntry = {
  id: string;
  title: string;
  createdAt: number;
  messages: ChatMessage[];
  agentStage: 'agent1' | 'agent2';
  agent1RunId: string | null;
  agent2RunId: string | null;
  agent1AwaitingDecision: boolean;
  agent2AwaitingDecision: boolean;
  lastPrompt: string;
  latestFeatures: AgentFeatureSpec[];
  latestStories: AgentStorySpec[];
  project?: ProjectWizardSubmission | null;
};

export type ProjectWorkflowPreset = {
  id: string;
  name: string;
  description: string;
  issueTypes: string[];
  defaultBoard: 'scrum' | 'kanban' | 'mixed';
  recommendedSprintLength?: number;
  notes?: string;
};

export type ProjectTemplate = {
  id: string;
  name: string;
  summary: string;
  industry: string;
  methodology: 'scrum' | 'kanban' | 'hybrid';
  defaultWorkflow: ProjectWorkflowPreset['id'];
  focusAreas: string[];
  personaHints: string[];
  aiPrompts?: ProjectAISuggestion[];
};

export type ProjectAISuggestion = {
  id: string;
  title: string;
  category: 'summary' | 'epics' | 'stories' | 'acceptanceCriteria';
  prompt: string;
  sampleOutput?: string;
};

export type ProjectWizardDetails = {
  name: string;
  key: string;
  description: string;
  industry: string;
  methodology: 'scrum' | 'kanban' | 'hybrid';
  timezone: string;
  startDate: string | null;
  targetLaunch: string | null;
  teamSize: number | null;
};

export type ProjectWizardAISummary = {
  executiveSummary: string;
  epicIdeas: string[];
  riskNotes: string[];
  customPrompt: string;
};

export type ProjectWizardSubmission = {
  templateId: string | null;
  workflowId: string;
  details: ProjectWizardDetails;
  aiSummary: ProjectWizardAISummary;
  features: AgentFeatureDetail[];
  stories: AgentStorySpec[];
  createdAt: string;
};

export type ProjectWizardSubmissionPayload = {
  submission: ProjectWizardSubmission;
  files: File[];
};

export type AgentFeatureRisk = {
  description: string;
  mitigation: string;
};

export type AgentFeatureDetail = {
  summary: string;
  key: string;
  problemStatement: string;
  businessObjective: string;
  userPersona: string;
  description: string;
  acceptanceCriteria: string[];
  successMetrics: string[];
  stakeholders: string[];
  dependencies: string[];
  constraints: string[];
  risks: AgentFeatureRisk[];
  targetRelease: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  nonFunctionalRequirements: string[];
  status: string;
  team: string;
};

export type FeatureFormSubmission = {
  detail: AgentFeatureDetail;
  files: File[];
};

export type AISuggestionRequest = {
  suggestion_type: 'summary' | 'epics' | 'acceptanceCriteria' | 'stories';
  prompt: string;
  project_context?: {
    industry?: string;
    methodology?: string;
    name?: string;
    description?: string;
    focusAreas?: string[] | string;
  };
};

export type AISuggestionResponse = {
  run_id: string;
  output: string;
  type: string;
};

