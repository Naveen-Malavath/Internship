import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface GenerateRequest {
  type: 'summary' | 'epics' | 'acceptance' | 'risks';
  projectName: string;
  industry: string;
  methodology: string;
  promptSummary: string;
  focusAreas?: string;
}

export interface GenerateResponse {
  content: string;
}

export interface Feature {
  title: string;
  reason: string;
  acceptanceCriteria: string;
  problemStatement: string;
  businessObjective: string;
  userPersona: string;
  detailedDescription: string;
  successMetrics: string;
  dependencies: string;
  approved?: boolean;
}

export interface FeaturesRequest {
  prompt: string;
  previousFeatures?: string;
}

export interface FeaturesResponse {
  features: Feature[];
}

export interface Story {
  title: string;
  description: string;
  featureRef: string;
  approved?: boolean;
}

export interface StoriesRequest {
  features: string[];
  projectContext?: string;
  previousStories?: string;
}

export interface StoriesResponse {
  stories: Story[];
}

// Design Types for all diagram types
export type DesignType = 
  | 'hld' 
  | 'dbd' 
  | 'api' 
  | 'lld' 
  | 'dfd' 
  | 'component' 
  | 'security' 
  | 'infrastructure' 
  | 'state' 
  | 'journey'
  | 'sequence'
  | 'mindmap'
  | 'gantt'
  | 'gitflow'
  | 'wireframe';

export interface DesignRequest {
  project_summary: string;
  features_summary?: string;
  stories_summary?: string;
  hld_summary?: string;
  dbd_summary?: string;
  api_summary?: string;
  lld_summary?: string;
  dfd_summary?: string;
  component_summary?: string;
  security_summary?: string;
  infrastructure_summary?: string;
  state_summary?: string;
  journey_summary?: string;
  sequence_summary?: string;
  mindmap_summary?: string;
  gantt_summary?: string;
  gitflow_summary?: string;
}

export interface DesignResponse {
  design_type: string;
  diagram: string;
  summary: string;
  status: string;
  tokens_used?: { [key: string]: number };
}

export interface SummarizeProjectRequest {
  project_context: string;
  features: Feature[];
  stories: Story[];
}

export interface SummarizeProjectResponse {
  summary: string;
  status: string;
}

export interface SummarizeDiagramRequest {
  diagram_type: string;
  diagram: string;
}

export interface SummarizeDiagramResponse {
  diagram_type: string;
  summary: string;
  status: string;
}

export interface DesignChainRequest {
  project_context: string;
  features: Feature[];
  stories: Story[];
}

export interface DesignChainResponse {
  designs: { [key: string]: string };
  summaries: { [key: string]: string };
  status: string;
  total_tokens: { [key: string]: string };
}

// Design metadata for UI
export interface DesignTypeInfo {
  value: DesignType;
  label: string;
  icon: string;
  description: string;
  order: number;
  dependencies: DesignType[];
}

// Wireframe Types
export interface WireframePage {
  id: string;
  name: string;
  type: string;
  html: string;
  description?: string;
  error?: string;
}

export interface WireframeData {
  pages: WireframePage[];
  shared_components: {
    sidebar?: string;
    header?: string;
    page_wrapper?: string;
  };
  plan: {
    pages?: any[];
    navigation?: any;
    theme?: any;
  };
  metadata: {
    total_pages: number;
    generation_time?: number;
  };
}

export interface WireframePagesRequest {
  project_summary: string;
  features_summary?: string;
  hld_summary?: string;
  api_summary?: string;
}

export interface WireframePagesResponse {
  pages: WireframePage[];
  shared_components: any;
  plan: any;
  status: string;
  metadata: any;
}

export interface RegeneratePageRequest {
  page_id: string;
  page_name: string;
  page_type: string;
  project_context: string;
  shared_components?: any;
}

export const DESIGN_TYPES: DesignTypeInfo[] = [
  { value: 'hld', label: 'High Level Design', icon: 'architecture', description: 'System architecture overview', order: 1, dependencies: [] },
  { value: 'dbd', label: 'Database Design', icon: 'storage', description: 'Database schema and relationships', order: 2, dependencies: ['hld'] },
  { value: 'api', label: 'API Design', icon: 'api', description: 'API endpoints and contracts', order: 3, dependencies: ['hld', 'dbd'] },
  { value: 'lld', label: 'Low Level Design', icon: 'code', description: 'Detailed component design', order: 4, dependencies: ['hld', 'dbd', 'api'] },
  { value: 'dfd', label: 'Data Flow Diagram', icon: 'swap_horiz', description: 'Data flow between components', order: 5, dependencies: ['hld', 'dbd'] },
  { value: 'component', label: 'Component Diagram', icon: 'widgets', description: 'Component structure and dependencies', order: 6, dependencies: ['hld', 'lld'] },
  { value: 'security', label: 'Security Architecture', icon: 'security', description: 'Security layers and controls', order: 7, dependencies: ['hld', 'api'] },
  { value: 'infrastructure', label: 'Infrastructure Design', icon: 'cloud', description: 'Deployment and infrastructure', order: 8, dependencies: ['hld', 'security'] },
  { value: 'state', label: 'State Diagram', icon: 'timeline', description: 'State transitions and flows', order: 9, dependencies: ['hld', 'api'] },
  { value: 'journey', label: 'User Journey', icon: 'route', description: 'User experience flows', order: 10, dependencies: ['hld', 'api'] },
  { value: 'sequence', label: 'Sequence Diagram', icon: 'sync_alt', description: 'API interaction flows', order: 11, dependencies: ['hld', 'api'] },
  { value: 'mindmap', label: 'Feature Mindmap', icon: 'hub', description: 'Feature visualization', order: 12, dependencies: ['hld'] },
  { value: 'gantt', label: 'Project Timeline', icon: 'date_range', description: 'Development schedule', order: 13, dependencies: ['hld'] },
  { value: 'gitflow', label: 'Git Workflow', icon: 'account_tree', description: 'Branching strategy', order: 14, dependencies: ['infrastructure'] }
  // Wireframe is now a separate section with HTML/CSS rendering, not Mermaid
];

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  generateContent(request: GenerateRequest): Observable<GenerateResponse> {
    return this.http.post<GenerateResponse>(`${this.apiUrl}/api/generate`, request);
  }

  generateFeatures(request: FeaturesRequest): Observable<FeaturesResponse> {
    return this.http.post<FeaturesResponse>(`${this.apiUrl}/api/generate-features`, request);
  }

  generateStories(request: StoriesRequest): Observable<StoriesResponse> {
    return this.http.post<StoriesResponse>(`${this.apiUrl}/api/generate-stories`, request);
  }

  // Design Generation APIs
  generateDesign(designType: DesignType, request: DesignRequest): Observable<DesignResponse> {
    return this.http.post<DesignResponse>(`${this.apiUrl}/api/designs/${designType}`, request);
  }

  summarizeProject(request: SummarizeProjectRequest): Observable<SummarizeProjectResponse> {
    return this.http.post<SummarizeProjectResponse>(`${this.apiUrl}/api/designs/summarize`, request);
  }

  summarizeDiagram(request: SummarizeDiagramRequest): Observable<SummarizeDiagramResponse> {
    return this.http.post<SummarizeDiagramResponse>(`${this.apiUrl}/api/designs/summarize-diagram`, request);
  }

  generateAllDesigns(request: DesignChainRequest): Observable<DesignChainResponse> {
    return this.http.post<DesignChainResponse>(`${this.apiUrl}/api/designs/generate-all`, request);
  }

  getDesignConfig(): Observable<{ designs: any, order: string[] }> {
    return this.http.get<{ designs: any, order: string[] }>(`${this.apiUrl}/api/designs/config`);
  }

  // Fix invalid Mermaid diagram
  fixDiagram(diagram: string, diagramType: string, errorMessage: string): Observable<{
    fixed_diagram: string;
    was_fixed: boolean;
    fix_description: string;
  }> {
    return this.http.post<{
      fixed_diagram: string;
      was_fixed: boolean;
      fix_description: string;
    }>(`${this.apiUrl}/api/designs/fix-diagram`, {
      diagram,
      diagram_type: diagramType,
      error_message: errorMessage
    });
  }

  // Wireframe Multi-Page Generation
  generateWireframePages(request: WireframePagesRequest): Observable<WireframePagesResponse> {
    return this.http.post<WireframePagesResponse>(`${this.apiUrl}/api/designs/wireframe-pages`, request);
  }

  // Regenerate single wireframe page
  regenerateWireframePage(request: RegeneratePageRequest): Observable<{ page: WireframePage; status: string }> {
    return this.http.post<{ page: WireframePage; status: string }>(
      `${this.apiUrl}/api/designs/wireframe-page/regenerate`, 
      request
    );
  }

  checkHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
}
