import { Component, Input, signal, OnInit, AfterViewInit, ElementRef, ViewChild, OnDestroy, computed, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSelectModule } from '@angular/material/select';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { Feature, Story, ApiService, DesignType, DesignResponse, DESIGN_TYPES, DesignTypeInfo, WireframeData, WireframePage } from '../../services/api.service';
import { WireframeViewerComponent } from '../wireframe-viewer/wireframe-viewer.component';
import { DevModeService } from '../../services/dev-mode.service';
import { MOCK_WIREFRAME_DATA } from '../../services/dev-data';
import mermaid from 'mermaid';

export interface ProjectData {
  projectName: string;
  projectKey: string;
  industry: string;
  methodology: string;
  teamSize: string;
  executiveSummary: string;
  promptSummary: string;
  finalPrompt: string;
  features: Feature[];
  stories: Story[];
  epicIdeas: string[];
  riskHighlights: string[];
  generatedRisks: string;
}

interface DesignState {
  type: DesignType;
  status: 'locked' | 'available' | 'generating' | 'completed' | 'error';
  mermaidCode?: string;
  summary?: string;
  error?: string;
  timestamp?: string;
}

@Component({
  selector: 'app-project-workspace',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatSelectModule,
    MatTooltipModule,
    MatProgressSpinnerModule,
    WireframeViewerComponent
  ],
  templateUrl: './project-workspace.component.html',
  styleUrls: ['./project-workspace.component.scss']
})
export class ProjectWorkspaceComponent implements OnInit, AfterViewInit, OnDestroy {
  @Input() project!: ProjectData;
  @ViewChild('mermaidContainer') mermaidContainer!: ElementRef;
  @ViewChild('fullscreenMermaidContainer') fullscreenMermaidContainer!: ElementRef;
  @ViewChild(WireframeViewerComponent) wireframeViewer!: WireframeViewerComponent;
  
  private apiService = inject(ApiService);
  private devModeService = inject(DevModeService);
  
  // Design types metadata
  designTypes = DESIGN_TYPES;
  
  // Track state for each design type
  designStates = signal<Map<DesignType, DesignState>>(new Map());
  
  // Currently selected design
  selectedDesignType = signal<DesignType>('hld');
  
  // Current generation status
  isGenerating = signal(false);
  generatingDesignType = signal<DesignType | null>(null);
  generationProgress = signal<string>('');
  isFixingDiagram = signal(false);
  isGeneratingAll = signal(false);  // Flag to track "Generate All" mode
  isViewingDuringGeneration = signal(false);  // Flag to track if user is viewing a completed design during "Generate All"
  private generateAllInProgress = false;  // Internal flag to track if generation loop is running
  
  // Summaries for chaining
  designSummaries = signal<Map<DesignType, string>>(new Map());
  
  isDarkTheme = signal(true);
  
  // Mermaid code for current diagram - empty by default, show message instead
  mermaidCode = signal('');
  
  // Wireframe specific state
  wireframeData = signal<WireframeData | null>(null);
  isGeneratingWireframes = signal(false);
  wireframeProgress = signal<string>('');
  
  // Wireframe generation settings
  wireframePageMode = signal<'auto' | 'manual'>('auto');  // 'auto' = LLM decides, 'manual' = user specifies
  wireframePageCount = signal<number>(5);  // Default page count when manual
  pageCountOptions = [2, 3, 4, 5, 6, 8, 10, 12];  // Available options
  
  // Handler for page count changes
  onPageCountChange(count: number) {
    console.log('[ProjectWorkspace] Received page count change:', count);
    this.wireframePageCount.set(count);
    console.log('[ProjectWorkspace] wireframePageCount is now:', this.wireframePageCount());
  }
  
  // Flag to show placeholder message instead of diagram
  showPlaceholder = signal(true);
  
  // Fullscreen mode
  isFullscreen = signal(false);
  fullscreenDiagramSvg = signal('');
  
  // Zoom and Pan for fullscreen
  zoomLevel = signal(1);
  panX = signal(0);
  panY = signal(0);
  isPanning = signal(false);
  private panStartX = 0;
  private panStartY = 0;
  private lastPanX = 0;
  private lastPanY = 0;
  
  diagramLineCount = signal(0);
  diagramCharCount = signal(0);
  
  // Chat panel
  isChatOpen = signal(false);
  
  // Auto-start flag
  private autoStarted = false;
  
  private mermaidInitialized = false;
  
  // Computed: get current design state
  currentDesignState = computed(() => {
    const states = this.designStates();
    return states.get(this.selectedDesignType()) || { type: this.selectedDesignType(), status: 'available' as const };
  });
  
  // Computed: check if current design can be generated
  canGenerateCurrentDesign = computed(() => {
    const state = this.currentDesignState();
    return state.status === 'available' || state.status === 'error';
  });
  
  ngOnInit() {
    console.log('[DEBUG] ProjectWorkspace initializing...');
    console.log('[DEBUG] Project data:', this.project);
    
    // Initialize mermaid with professional dark theme config
    mermaid.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
      suppressErrorRendering: true,
      themeVariables: {
        // Professional dark color scheme
        primaryColor: '#3b82f6',
        primaryTextColor: '#ffffff',
        primaryBorderColor: '#60a5fa',
        secondaryColor: '#1e3a5f',
        secondaryTextColor: '#e2e8f0',
        secondaryBorderColor: '#475569',
        tertiaryColor: '#0f172a',
        tertiaryTextColor: '#cbd5e1',
        tertiaryBorderColor: '#334155',
        // Background colors
        background: '#0f172a',
        mainBkg: '#1e293b',
        secondBkg: '#334155',
        // Line and border colors
        lineColor: '#60a5fa',
        border1: '#3b82f6',
        border2: '#475569',
        // Text colors
        textColor: '#e2e8f0',
        nodeTextColor: '#ffffff',
        // Note colors
        noteBkgColor: '#1e3a5f',
        noteTextColor: '#e2e8f0',
        noteBorderColor: '#3b82f6',
        // Flowchart specific
        nodeBorder: '#3b82f6',
        clusterBkg: '#1e293b',
        clusterBorder: '#475569',
        // State diagram
        labelColor: '#e2e8f0',
        // Sequence diagram
        actorBkg: '#1e3a5f',
        actorBorder: '#3b82f6',
        actorTextColor: '#ffffff',
        signalColor: '#60a5fa'
      },
      flowchart: {
        useMaxWidth: true,
        htmlLabels: true,
        curve: 'basis',
        padding: 15
      },
      sequence: {
        useMaxWidth: true,
        boxMargin: 10,
        mirrorActors: false
      },
      er: {
        useMaxWidth: true
      }
    });
    
    // Initialize design states
    this.initializeDesignStates();
    
    // Add event listener for retry fix button
    window.addEventListener('retry-diagram-fix', this.handleRetryFix);
    
    // Wireframes will only be generated when user clicks "Generate All"
    // No auto-loading - show empty state by default
  }
  
  ngAfterViewInit() {
    setTimeout(() => {
      this.renderDiagram();
      
      // NO AUTO-START - User must click manually to generate designs
      // Removed auto HLD generation
    }, 100);
  }
  
  ngOnDestroy() {
    // Cleanup event listener
    window.removeEventListener('retry-diagram-fix', this.handleRetryFix);
  }
  
  // Bound handler for retry fix event
  private handleRetryFix = () => {
    console.log('[DEBUG] Retry fix triggered');
    this.fixAttempts = 0;
    this.renderDiagram(false);
  };
  
  private initializeDesignStates() {
    const states = new Map<DesignType, DesignState>();
    
    for (const designType of this.designTypes) {
      // HLD is always available first
      const status = designType.value === 'hld' ? 'available' : 'locked';
      states.set(designType.value, {
        type: designType.value,
        status
      });
    }
    
    this.designStates.set(states);
    console.log('[DEBUG] Initialized design states:', states);
  }
  
  private updateDesignState(type: DesignType, update: Partial<DesignState>) {
    const states = new Map(this.designStates());
    const current = states.get(type) || { type, status: 'available' as const };
    const newState = { ...current, ...update };
    
    // SERIOUS DEBUG: Log every state update with diagram info
    console.log(`%c[STATE] ${type}: ${current.status} -> ${newState.status}`, 'color: #00ff00; font-weight: bold; font-size: 12px');
    if (update.mermaidCode) {
      const diagramType = update.mermaidCode.trim().split('\n')[0].substring(0, 40);
      console.log(`  Storing diagram: "${diagramType}..." (${update.mermaidCode.length} chars)`);
      
      // VALIDATION: Check if diagram type matches design type
      const expectedStart: Record<string, string[]> = {
        'hld': ['graph', 'flowchart'],
        'dbd': ['erDiagram'],
        'api': ['sequenceDiagram', 'graph', 'flowchart'],
        'lld': ['classDiagram'],
        'dfd': ['graph', 'flowchart'],
        'state': ['stateDiagram'],
        'journey': ['journey'],
        'sequence': ['sequenceDiagram'],
        'mindmap': ['mindmap'],
        'gantt': ['gantt'],
        'gitflow': ['gitGraph']
      };
      const expected = expectedStart[type] || [];
      const actualStart = diagramType.toLowerCase();
      const isValid = expected.some(e => actualStart.startsWith(e.toLowerCase()));
      if (!isValid && expected.length > 0) {
        console.error(`%c[WRONG DIAGRAM!] ${type} should start with ${expected.join('/')} but got "${diagramType}"`, 'color: red; font-size: 14px; font-weight: bold');
      }
    }
    
    states.set(type, newState);
    this.designStates.set(states);
  }
  
  private unlockDependentDesigns(completedType: DesignType) {
    console.log('[DEBUG] Unlocking designs dependent on:', completedType);
    
    const states = new Map(this.designStates());
    const completedTypes = new Set<DesignType>();
    
    // Gather all completed designs
    states.forEach((state, type) => {
      if (state.status === 'completed') {
        completedTypes.add(type);
      }
    });
    completedTypes.add(completedType);
    
    // Check each design type to see if its dependencies are met
    for (const designType of this.designTypes) {
      const state = states.get(designType.value);
      if (state?.status === 'locked') {
        // Check if all dependencies are completed
        const allDepsCompleted = designType.dependencies.every(dep => completedTypes.has(dep));
        if (allDepsCompleted) {
          console.log('[DEBUG] Unlocking:', designType.value);
          states.set(designType.value, { ...state, status: 'available' });
        }
      }
    }
    
    this.designStates.set(states);
  }
  
  getDesignTypeInfo(type: DesignType): DesignTypeInfo | undefined {
    return this.designTypes.find(d => d.value === type);
  }
  
  getDesignState(type: DesignType): DesignState {
    return this.designStates().get(type) || { type, status: 'locked' };
  }
  
  isDesignLocked(type: DesignType): boolean {
    return this.getDesignState(type).status === 'locked';
  }
  
  isDesignCompleted(type: DesignType): boolean {
    return this.getDesignState(type).status === 'completed';
  }
  
  isDesignGenerating(type: DesignType): boolean {
    return this.getDesignState(type).status === 'generating';
  }
  
  // Store project summary for design generation
  projectSummary = signal<string>('');
  
  async generateDesign(type: DesignType) {
    if (this.isGenerating()) {
      console.log('[DEBUG] Already generating, skipping:', type);
      return;
    }
    
    console.log('[DEBUG] Starting generation for:', type);
    
    this.isGenerating.set(true);
    this.generatingDesignType.set(type);
    this.generationProgress.set(`Generating ${this.getDesignTypeInfo(type)?.label}...`);
    this.updateDesignState(type, { status: 'generating' });
    
    try {
      // First, check if we have a project summary
      if (!this.projectSummary()) {
        console.log('[DEBUG] No project summary, generating first...');
        this.generationProgress.set('Summarizing project...');
        
        const summaryResponse = await this.apiService.summarizeProject({
          project_context: this.project.finalPrompt,
          features: this.project.features,
          stories: this.project.stories
        }).toPromise();
        
        if (summaryResponse) {
          this.projectSummary.set(summaryResponse.summary);
          console.log('[DEBUG] Project summary generated, length:', summaryResponse.summary.length);
        }
      }
      
      // Build request with previous summaries
      const summaries = this.designSummaries();
      const request: any = {
        project_summary: this.projectSummary()
      };
      
      // Add available summaries based on design type dependencies
      const typeInfo = this.getDesignTypeInfo(type);
      if (typeInfo) {
        for (const dep of typeInfo.dependencies) {
          const summaryKey = `${dep}_summary`;
          if (summaries.has(dep)) {
            request[summaryKey] = summaries.get(dep);
          }
        }
      }
      
      console.log(`%c[API-SINGLE] Calling API for: ${type}`, 'color: #ffff00; font-weight: bold; font-size: 14px');
      console.log('[API-SINGLE] Request summaries:', Object.keys(request).filter(k => k.endsWith('_summary')));
      
      this.generationProgress.set(`Generating ${this.getDesignTypeInfo(type)?.label}...`);
      
      const response = await this.apiService.generateDesign(type, request).toPromise();
      
      if (response) {
        const diagramStart = response.diagram?.trim().split('\n')[0].substring(0, 50) || 'EMPTY';
        console.log(`%c[API-SINGLE RESPONSE] ${type}`, 'color: #00ffff; font-weight: bold; font-size: 14px');
        console.log(`  Response.design_type: "${response.design_type}"`);
        console.log(`  Diagram starts: "${diagramStart}"`);
        console.log(`  Diagram length: ${response.diagram?.length || 0}`);
        
        if (response.design_type !== type) {
          console.error(`%c[MISMATCH!] Requested ${type} but got ${response.design_type}`, 'color: red; font-size: 16px');
        }
        
        // Update design state
        this.updateDesignState(type, {
          status: 'completed',
          mermaidCode: response.diagram,
          summary: response.summary,
          timestamp: new Date().toLocaleString()
        });
        
        // Store summary for chaining
        if (response.summary) {
          const newSummaries = new Map(this.designSummaries());
          newSummaries.set(type, response.summary);
          this.designSummaries.set(newSummaries);
        }
        
        // Unlock dependent designs
        this.unlockDependentDesigns(type);
        
        // If this is the selected design, update the display
        if (this.selectedDesignType() === type) {
          this.mermaidCode.set(response.diagram);
          this.showPlaceholder.set(false);
          // Wait for DOM to update before rendering
          setTimeout(() => this.renderDiagram(), 50);
        }
        
        this.generationProgress.set(`${this.getDesignTypeInfo(type)?.label} completed!`);
      }
    } catch (error: any) {
      console.error('[DEBUG] Error generating design:', type, error);
      this.updateDesignState(type, {
        status: 'error',
        error: error.message || 'Generation failed'
      });
      this.generationProgress.set(`Error: ${error.message || 'Generation failed'}`);
    } finally {
      this.isGenerating.set(false);
      this.generatingDesignType.set(null);
      
      // Clear progress after delay
      setTimeout(() => {
        this.generationProgress.set('');
      }, 3000);
    }
  }
  
  // Generate all designs in dependency order
  async generateAllDesigns() {
    if (this.isGenerating()) {
      return;
    }
    
    // Define generation groups based on dependencies
    // Each group can run in parallel, but groups must run sequentially
    const generationGroups: DesignType[][] = [
      ['hld'],                                    // Group 1: HLD first (no deps)
      ['dbd', 'mindmap', 'gantt'],               // Group 2: Only need HLD
      ['api'],                                    // Group 3: Needs HLD + DBD
      ['lld', 'dfd', 'journey', 'sequence', 'state'], // Group 4: Need HLD + API
      ['component', 'security'],                  // Group 5: Need HLD + API
      ['infrastructure'],                         // Group 6: Needs HLD
      ['gitflow']                                 // Group 7: Needs Infrastructure
    ];
    
    // Flatten for total count, excluding already completed
    const allDesigns = generationGroups.flat();
    const designsToGenerate = allDesigns.filter(type => !this.isDesignCompleted(type));
    
    if (designsToGenerate.length === 0) {
      return;
    }
    
    // Set "Generate All" mode
    this.isGeneratingAll.set(true);
    this.generateAllInProgress = true;
    this.isViewingDuringGeneration.set(false);
    this.showPlaceholder.set(false);
    
    console.log('[DEBUG-GENALL] Starting Parallel Generate All');
    
    // Clear the mermaid code to show loading state
    this.mermaidCode.set('');
    
    // Track progress
    this.totalDesignsToGenerate = designsToGenerate.length;
    this.completedDesignCount = 0;
    
    // Check if we need to summarize first
    if (!this.projectSummary()) {
      this.generationProgress.set(`Summarizing project... (0/${this.totalDesignsToGenerate})`);
      
      try {
        const summaryResponse = await this.apiService.summarizeProject({
          project_context: this.project.finalPrompt,
          features: this.project.features,
          stories: this.project.stories
        }).toPromise();
        
        if (summaryResponse) {
          this.projectSummary.set(summaryResponse.summary);
        }
      } catch (error) {
        console.error('[ERROR] Failed to summarize project:', error);
        this.isGeneratingAll.set(false);
        this.generateAllInProgress = false;
        this.generationProgress.set('Failed to summarize project');
        return;
      }
    }
    
    let lastGeneratedType: DesignType | null = null;
    
    // Process each group
    for (let groupIndex = 0; groupIndex < generationGroups.length; groupIndex++) {
      const group = generationGroups[groupIndex];
      
      // Filter to only designs that need generating in this group
      const groupToGenerate = group.filter(type => !this.isDesignCompleted(type));
      
      if (groupToGenerate.length === 0) {
        continue; // Skip empty groups
      }
      
      console.log(`[DEBUG-GENALL] Processing group ${groupIndex + 1}: ${groupToGenerate.join(', ')}`);
      
      // Update progress to show all generating designs in this group
      const groupLabels = groupToGenerate.map(t => this.getDesignTypeInfo(t)?.label).join(', ');
      this.generationProgress.set(`Generating ${groupLabels}... (${this.completedDesignCount}/${this.totalDesignsToGenerate})`);
      
      // Generate all designs in this group in parallel
      const promises = groupToGenerate.map(type => this.generateDesignParallel(type));
      const results = await Promise.allSettled(promises);
      
      // Check results and update last generated
      results.forEach((result, index) => {
        if (result.status === 'fulfilled' && result.value) {
          lastGeneratedType = groupToGenerate[index];
        }
      });
      
      // Small delay between groups
      if (groupIndex < generationGroups.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 200));
      }
    }
    
    // Generation complete
    this.isGeneratingAll.set(false);
    this.generateAllInProgress = false;
    this.isViewingDuringGeneration.set(false);
    
    if (lastGeneratedType) {
      this.selectDesignType(lastGeneratedType);
      this.generationProgress.set(`All ${this.completedDesignCount} designs generated successfully!`);
    }
    
    // Clear progress after delay
    setTimeout(() => {
      this.generationProgress.set('');
    }, 3000);
  }
  
  // Track completed designs for progress
  private completedDesignCount = 0;
  private totalDesignsToGenerate = 0;
  private currentDesignIndex = 0;
  
  // Generate a design for parallel execution (doesn't block other designs)
  private async generateDesignParallel(type: DesignType): Promise<boolean> {
    console.log('[DEBUG-PARALLEL] Starting parallel generation for:', type);
    
    // Set this design to generating state (individual, not global)
    this.updateDesignState(type, { status: 'generating' });
    
    try {
      // Build request with previous summaries
      const summaries = this.designSummaries();
      const request: any = {
        project_summary: this.projectSummary()
      };
      
      // Add available summaries based on design type dependencies
      const typeInfo = this.getDesignTypeInfo(type);
      if (typeInfo) {
        for (const dep of typeInfo.dependencies) {
          const summaryKey = `${dep}_summary`;
          if (summaries.has(dep)) {
            request[summaryKey] = summaries.get(dep);
          }
        }
      }
      
      console.log(`%c[API-PARALLEL] Calling API for: ${type}`, 'color: #ff9900; font-weight: bold; font-size: 14px');
      const response = await this.apiService.generateDesign(type, request).toPromise();
      
      if (response) {
        const diagramStart = response.diagram?.trim().split('\n')[0].substring(0, 50) || 'EMPTY';
        console.log(`%c[API-PARALLEL RESPONSE] ${type}`, 'color: #00ff99; font-weight: bold; font-size: 14px');
        console.log(`  Response.design_type: "${response.design_type}"`);
        console.log(`  Diagram starts: "${diagramStart}"`);
        console.log(`  Diagram length: ${response.diagram?.length || 0}`);
        
        if (response.design_type !== type) {
          console.error(`%c[MISMATCH!] Requested ${type} but got ${response.design_type}`, 'color: red; font-size: 16px');
        }
        
        // Update design state
        this.updateDesignState(type, {
          status: 'completed',
          mermaidCode: response.diagram,
          summary: response.summary,
          timestamp: new Date().toLocaleString()
        });
        
        // Store summary for chaining
        if (response.summary) {
          const newSummaries = new Map(this.designSummaries());
          newSummaries.set(type, response.summary);
          this.designSummaries.set(newSummaries);
        }
        
        // Unlock dependent designs
        this.unlockDependentDesigns(type);
        
        // Increment completed count and update progress
        this.completedDesignCount++;
        this.generationProgress.set(`Generated ${this.completedDesignCount}/${this.totalDesignsToGenerate} designs...`);
        
        console.log(`[PARALLEL-DONE] ${type} (${this.completedDesignCount}/${this.totalDesignsToGenerate})`);
        
        return true;
      }
      
      return false;
    } catch (error: any) {
      console.error('[DEBUG-PARALLEL] Error generating:', type, error);
      this.updateDesignState(type, {
        status: 'error',
        error: error.message || 'Generation failed'
      });
      
      // Still increment to keep progress accurate
      this.completedDesignCount++;
      this.generationProgress.set(`Generated ${this.completedDesignCount}/${this.totalDesignsToGenerate} designs...`);
      
      return false;
    }
  }
  
  // Generate a design without updating the editor (for "Generate All" mode)
  private async generateDesignSilent(type: DesignType): Promise<boolean> {
    console.log('[DEBUG] Silent generation for:', type);
    
    this.isGenerating.set(true);
    this.generatingDesignType.set(type);
    this.updateDesignState(type, { status: 'generating' });
    
    try {
      // First, check if we have a project summary
      if (!this.projectSummary()) {
        console.log('[DEBUG] No project summary, generating first...');
        // Show summarizing progress with 0/total
        this.generationProgress.set(`Summarizing project... (0/${this.totalDesignsToGenerate})`);
        
        const summaryResponse = await this.apiService.summarizeProject({
          project_context: this.project.finalPrompt,
          features: this.project.features,
          stories: this.project.stories
        }).toPromise();
        
        if (summaryResponse) {
          this.projectSummary.set(summaryResponse.summary);
        }
        
        // After summarizing, restore progress to show current design
        this.generationProgress.set(`Generating ${this.getDesignTypeInfo(type)?.label}... (${this.currentDesignIndex}/${this.totalDesignsToGenerate})`);
      }
      
      // Build request with previous summaries
      const summaries = this.designSummaries();
      const request: any = {
        project_summary: this.projectSummary()
      };
      
      // Add available summaries based on design type dependencies
      const typeInfo = this.getDesignTypeInfo(type);
      if (typeInfo) {
        for (const dep of typeInfo.dependencies) {
          const summaryKey = `${dep}_summary`;
          if (summaries.has(dep)) {
            request[summaryKey] = summaries.get(dep);
          }
        }
      }
      
      const response = await this.apiService.generateDesign(type, request).toPromise();
      
      if (response) {
        // Update design state
        this.updateDesignState(type, {
          status: 'completed',
          mermaidCode: response.diagram,
          summary: response.summary,
          timestamp: new Date().toLocaleString()
        });
        
        // Store summary for chaining
        if (response.summary) {
          const newSummaries = new Map(this.designSummaries());
          newSummaries.set(type, response.summary);
          this.designSummaries.set(newSummaries);
        }
        
        // Unlock dependent designs
        this.unlockDependentDesigns(type);
        
        return true;
      }
      
      return false;
    } catch (error: any) {
      console.error('[DEBUG] Error generating design:', type, error);
      this.updateDesignState(type, {
        status: 'error',
        error: error.message || 'Generation failed'
      });
      return false;
    } finally {
      this.isGenerating.set(false);
      this.generatingDesignType.set(null);
    }
  }
  
  // Handle design card click - select and auto-generate if not completed
  onDesignCardClick(type: DesignType) {
    console.log('[DEBUG-CLICK] Card clicked:', type, 'generateAllInProgress:', this.generateAllInProgress, 'isGeneratingAll:', this.isGeneratingAll(), 'isViewingDuringGeneration:', this.isViewingDuringGeneration());
    console.log('[DEBUG-CLICK] isLocked:', this.isDesignLocked(type), 'isCompleted:', this.isDesignCompleted(type), 'isGenerating:', this.isDesignGenerating(type));
    
    // Ignore if locked
    if (this.isDesignLocked(type)) {
      console.log('[DEBUG-CLICK] Ignored - locked');
      return;
    }
    
    // During "Generate All" mode (generation loop is running)
    if (this.generateAllInProgress) {
      console.log('[DEBUG-CLICK] In generateAllInProgress mode');
      if (this.isDesignCompleted(type)) {
        console.log('[DEBUG-CLICK] Viewing completed design:', type);
        // View the completed design
        this.viewCompletedDesignDuringGeneration(type);
      } else if (this.isDesignGenerating(type)) {
        console.log('[DEBUG-CLICK] Clicked generating design - back to loading view');
        // Clicked on the currently generating design - go back to loading view
        this.isViewingDuringGeneration.set(false);
      }
      return;
    }
    
    // Normal mode: ignore if already generating
    if (this.isGenerating()) {
      return;
    }
    
    // Select the design type
    this.selectDesignType(type);
    
    // If not completed, start generating
    if (!this.isDesignCompleted(type)) {
      this.generateDesign(type);
    }
  }
  
  // View a completed design while "Generate All" is still running
  private viewCompletedDesignDuringGeneration(type: DesignType) {
    console.log(`%c[VIEW-DURING-GEN] Viewing: ${type}`, 'color: #ff66ff; font-weight: bold; font-size: 14px');
    this.selectedDesignType.set(type);
    this.fixAttempts = 0; // Reset fix attempts
    
    const state = this.getDesignState(type);
    const diagramStart = state.mermaidCode?.trim().split('\n')[0].substring(0, 50) || 'NONE';
    console.log(`  State status: ${state.status}`);
    console.log(`  Diagram starts: "${diagramStart}"`);
    console.log(`  Diagram length: ${state.mermaidCode?.length || 0}`);
    
    if (state.mermaidCode) {
      this.mermaidCode.set(state.mermaidCode);
      this.showPlaceholder.set(false);
      // Set flag to show the design instead of loading overlay (but keep generation running)
      console.log('[VIEW-DURING-GEN] Setting isViewingDuringGeneration to TRUE');
      this.isViewingDuringGeneration.set(true);
      // Skip auto-fix for completed diagrams
      setTimeout(() => this.renderDiagram(true), 50);
    } else {
      console.error(`%c[VIEW-DURING-GEN] No mermaid code for ${type}!`, 'color: red');
    }
  }
  
  // Go back to showing the generation progress (called when clicking on a generating design card)
  backToGenerationView() {
    this.isViewingDuringGeneration.set(false);
  }
  
  selectDesignType(type: DesignType) {
    console.log(`%c[SELECT] Selecting design type: ${type}`, 'color: #ff00ff; font-weight: bold');
    this.selectedDesignType.set(type);
    this.fixAttempts = 0; // Reset fix attempts when switching diagrams
    
    const state = this.getDesignState(type);
    console.log(`  State status: ${state.status}`);
    console.log(`  Has mermaidCode: ${!!state.mermaidCode}`);
    if (state.mermaidCode) {
      const diagramStart = state.mermaidCode.trim().split('\n')[0].substring(0, 40);
      console.log(`  Diagram starts with: "${diagramStart}"`);
      this.mermaidCode.set(state.mermaidCode);
      this.showPlaceholder.set(false);
      // Wait for DOM to update before rendering
      // Skip auto-fix for already generated diagrams - render as-is
      setTimeout(() => this.renderDiagram(true), 50);
    } else {
      // Show placeholder message - no diagram
      console.log('  No mermaidCode - showing placeholder');
      this.mermaidCode.set('');
      this.showPlaceholder.set(true);
    }
  }
  
  // Track fix attempts to prevent infinite loops
  private fixAttempts = 0;
  private readonly MAX_FIX_ATTEMPTS = 2;
  
  async renderDiagram(skipAutoFix = false) {
    console.log(`%c[RENDER] renderDiagram called, skipAutoFix: ${skipAutoFix}`, 'color: #66ccff; font-weight: bold');
    
    if (!this.mermaidContainer?.nativeElement) {
      console.log('[RENDER] No mermaidContainer - aborting');
      return;
    }
    
    const container = this.mermaidContainer.nativeElement;
    const code = this.mermaidCode();
    
    console.log(`[RENDER] Code length: ${code?.length || 0}, starts with: "${code?.substring(0, 40)}"`);
    
    // Reset fixing state when starting fresh render
    this.isFixingDiagram.set(false);
    
    // First, validate the diagram syntax
    const validationResult = await this.validateMermaidSyntax(code);
    console.log(`[RENDER] Validation result: valid=${validationResult.valid}, error=${validationResult.error?.substring(0, 50)}`);
    
    if (!validationResult.valid && !skipAutoFix && this.fixAttempts < this.MAX_FIX_ATTEMPTS) {
      console.log(`%c[RENDER] Invalid syntax, will attempt fix (attempt ${this.fixAttempts + 1}/${this.MAX_FIX_ATTEMPTS})`, 'color: orange');
      console.log('[RENDER] Validation error:', validationResult.error);
      
      this.fixAttempts++;
      this.isFixingDiagram.set(true);
      
      const fixMessage = this.fixAttempts > 1 
        ? 'Taking longer than expected...'
        : 'Optimizing diagram...';
      this.generationProgress.set(fixMessage);
      
      // Show fixing status in container
      container.innerHTML = `
        <div style="color: #60a5fa; padding: 20px; text-align: center;">
          <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 10px; animation: spin 2s linear infinite;">
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
          </svg>
          <style>@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }</style>
          <div>${fixMessage}</div>
          <div style="font-size: 12px; opacity: 0.7; margin-top: 5px;">Please wait while we optimize the diagram</div>
        </div>
      `;
      
      try {
        // Determine diagram type from code
        const diagramType = this.detectDiagramType(code);
        
        const fixResponse = await this.apiService.fixDiagram(
          code,
          diagramType,
          validationResult.error || 'Unknown syntax error'
        ).toPromise();
        
        if (fixResponse && fixResponse.was_fixed) {
          console.log('[DEBUG] Diagram fixed successfully');
          this.mermaidCode.set(fixResponse.fixed_diagram);
          
          // Update the design state with fixed code
          const currentType = this.selectedDesignType();
          const currentState = this.getDesignState(currentType);
          if (currentState.status === 'completed') {
            this.updateDesignState(currentType, {
              ...currentState,
              mermaidCode: fixResponse.fixed_diagram
            });
          }
          
          // Try rendering again with fixed code
          await this.renderDiagram(false);
          this.generationProgress.set('Diagram syntax fixed!');
          setTimeout(() => this.generationProgress.set(''), 2000);
          return;
        }
      } catch (fixError) {
        console.error('[DEBUG] Failed to fix diagram:', fixError);
      }
    }
    
    // Reset fix attempts on successful render or after max attempts
    if (validationResult.valid) {
      this.fixAttempts = 0;
      this.isFixingDiagram.set(false);
    }
    
    try {
      const id = 'mermaid-diagram-' + Date.now();
      
      // Clear previous content
      container.innerHTML = '';
      
      // Render new diagram
      const { svg } = await mermaid.render(id, code);
      container.innerHTML = svg;
      
      // Update line and char count
      const lines = code.split('\n').length;
      const chars = code.length;
      this.diagramLineCount.set(lines);
      this.diagramCharCount.set(chars);
      
      this.mermaidInitialized = true;
      this.fixAttempts = 0; // Reset on success
      this.isFixingDiagram.set(false);
      console.log(`%c[RENDER] Successfully rendered diagram`, 'color: #00ff00; font-weight: bold');
    } catch (error: any) {
      console.error('[RENDER] Mermaid render error:', error.message?.substring(0, 100));
      
      // If skipAutoFix is true, don't try to fix - just show the error
      if (skipAutoFix) {
        console.log('[RENDER] skipAutoFix=true, showing error without fix attempt');
        this.isFixingDiagram.set(false);
        container.innerHTML = `<div style="color: #94a3b8; padding: 20px; text-align: center;">
          <p>Diagram has syntax issues but rendering skipped auto-fix.</p>
          <p style="font-size: 12px; opacity: 0.7;">Edit the code or click Regenerate.</p>
        </div>`;
        return;
      }
      
      // If we haven't tried fixing yet and this is a real error, try to fix
      if (this.fixAttempts < this.MAX_FIX_ATTEMPTS) {
        this.fixAttempts++;
        this.isFixingDiagram.set(true);
        console.log(`[RENDER] Render failed, attempting AI fix (attempt ${this.fixAttempts}/${this.MAX_FIX_ATTEMPTS})...`);
        
        const fixMessage = this.fixAttempts > 1 
          ? 'Taking longer than expected...'
          : 'Optimizing diagram...';
        
        try {
          const diagramType = this.detectDiagramType(code);
          const errorMessage = error.message || error.toString();
          
          container.innerHTML = `
            <div style="color: #60a5fa; padding: 20px; text-align: center;">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#60a5fa" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 10px; animation: spin 2s linear infinite;">
                <circle cx="12" cy="12" r="3"></circle>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
              </svg>
              <style>@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }</style>
              <div>${fixMessage}</div>
              <div style="font-size: 12px; opacity: 0.7; margin-top: 5px;">Please wait while we optimize the diagram</div>
            </div>
          `;
          
          const fixResponse = await this.apiService.fixDiagram(
            code,
            diagramType,
            errorMessage
          ).toPromise();
          
          if (fixResponse && fixResponse.was_fixed) {
            console.log('[DEBUG] Diagram fixed after render error');
            this.mermaidCode.set(fixResponse.fixed_diagram);
            
            // Update design state
            const currentType = this.selectedDesignType();
            const currentState = this.getDesignState(currentType);
            if (currentState.status === 'completed') {
              this.updateDesignState(currentType, {
                ...currentState,
                mermaidCode: fixResponse.fixed_diagram
              });
            }
            
            // Try rendering the fixed diagram
            await this.renderDiagram(true); // Skip auto-fix to prevent loops
            return;
          }
        } catch (fixError) {
          console.error('[DEBUG] Failed to fix diagram after render error:', fixError);
        }
      }
      
      // Clean up error message for display
      let cleanError = error.message || 'Unknown error';
      // Extract just the first line or key part of the error
      if (cleanError.includes('Parse error')) {
        cleanError = 'Invalid diagram syntax detected';
      } else if (cleanError.includes('Expecting')) {
        cleanError = 'Diagram has syntax errors';
      } else if (cleanError.length > 100) {
        cleanError = cleanError.substring(0, 100) + '...';
      }
      
      // Show error in container if fix failed
      container.innerHTML = `
        <div style="padding: 40px; text-align: center;">
          <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 16px;">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
            <line x1="12" y1="9" x2="12" y2="13"></line>
            <line x1="12" y1="17" x2="12.01" y2="17"></line>
          </svg>
          <div style="color: #f87171; font-size: 1.125rem; font-weight: 600; margin-bottom: 8px;">Diagram rendering error</div>
          <div style="color: #94a3b8; font-size: 0.875rem; max-width: 400px; margin: 0 auto 20px; word-break: break-word; line-height: 1.5;">
            ${cleanError}
          </div>
          <button onclick="window.dispatchEvent(new CustomEvent('retry-diagram-fix'))" 
                  style="padding: 10px 24px; background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 0.9375rem; font-weight: 500; transition: all 0.2s; box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);"
                  onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(59, 130, 246, 0.4)';"
                  onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(59, 130, 246, 0.3)';">
            Try Fix Again
          </button>
        </div>
      `;
    }
  }
  
  /**
   * Validate Mermaid syntax before rendering
   */
  private async validateMermaidSyntax(code: string): Promise<{ valid: boolean; error?: string }> {
    try {
      // Use mermaid's parse function to validate without rendering
      await mermaid.parse(code);
      return { valid: true };
    } catch (error: any) {
      return { 
        valid: false, 
        error: error.message || error.toString() 
      };
    }
  }
  
  /**
   * Detect the type of Mermaid diagram from code
   */
  private detectDiagramType(code: string): string {
    const trimmed = code.trim().toLowerCase();
    
    if (trimmed.startsWith('erdiagram')) return 'erDiagram';
    if (trimmed.startsWith('classdiagram')) return 'classDiagram';
    if (trimmed.startsWith('sequencediagram')) return 'sequenceDiagram';
    if (trimmed.startsWith('statediagram')) return 'stateDiagram';
    if (trimmed.startsWith('flowchart')) return 'flowchart';
    if (trimmed.startsWith('graph')) return 'flowchart';
    if (trimmed.startsWith('pie')) return 'pie';
    if (trimmed.startsWith('gantt')) return 'gantt';
    
    // Check after %%{init} block
    const lines = code.split('\n');
    for (const line of lines) {
      const trimmedLine = line.trim().toLowerCase();
      if (trimmedLine.startsWith('erdiagram')) return 'erDiagram';
      if (trimmedLine.startsWith('classdiagram')) return 'classDiagram';
      if (trimmedLine.startsWith('sequencediagram')) return 'sequenceDiagram';
      if (trimmedLine.startsWith('statediagram')) return 'stateDiagram';
      if (trimmedLine.startsWith('flowchart')) return 'flowchart';
      if (trimmedLine.startsWith('graph')) return 'flowchart';
    }
    
    return 'unknown';
  }
  
  onMermaidCodeChange() {
    this.renderDiagram();
  }
  
  toggleTheme() {
    this.isDarkTheme.set(!this.isDarkTheme());
    
    const darkThemeVars = {
      primaryColor: '#3b82f6',
      primaryTextColor: '#ffffff',
      primaryBorderColor: '#60a5fa',
      secondaryColor: '#1e3a5f',
      secondaryTextColor: '#e2e8f0',
      secondaryBorderColor: '#475569',
      tertiaryColor: '#0f172a',
      background: '#0f172a',
      mainBkg: '#1e293b',
      secondBkg: '#334155',
      lineColor: '#60a5fa',
      textColor: '#e2e8f0',
      nodeTextColor: '#ffffff',
      noteBkgColor: '#1e3a5f',
      noteTextColor: '#e2e8f0',
      noteBorderColor: '#3b82f6'
    };
    
    const lightThemeVars = {
      primaryColor: '#3b82f6',
      primaryTextColor: '#1e293b',
      primaryBorderColor: '#3b82f6',
      secondaryColor: '#e2e8f0',
      secondaryTextColor: '#1e293b',
      background: '#ffffff',
      mainBkg: '#f8fafc',
      secondBkg: '#e2e8f0',
      lineColor: '#3b82f6',
      textColor: '#1e293b',
      nodeTextColor: '#1e293b'
    };
    
    mermaid.initialize({
      startOnLoad: false,
      theme: this.isDarkTheme() ? 'dark' : 'default',
      securityLevel: 'loose',
      suppressErrorRendering: true,
      themeVariables: this.isDarkTheme() ? darkThemeVars : lightThemeVars
    });
    this.renderDiagram();
    
    // Update fullscreen diagram if in fullscreen mode
    if (this.isFullscreen()) {
      this.updateFullscreenDiagram();
    }
  }
  
  async toggleFullscreen() {
    if (!this.isFullscreen()) {
      // Entering fullscreen - reset zoom/pan and render
      this.resetZoom();
      this.isFullscreen.set(true);
      document.body.style.overflow = 'hidden';
      // Wait for DOM to update, then render directly to container
      setTimeout(() => this.renderFullscreenDiagram(), 100);
    } else {
      // Exiting fullscreen
      this.isFullscreen.set(false);
      document.body.style.overflow = '';
    }
  }
  
  private async renderFullscreenDiagram() {
    const code = this.mermaidCode();
    if (!code || !this.fullscreenMermaidContainer?.nativeElement) return;
    
    const container = this.fullscreenMermaidContainer.nativeElement;
    
    try {
      const id = 'fullscreen-mermaid-' + Date.now();
      container.innerHTML = '';
      const { svg } = await mermaid.render(id, code);
      container.innerHTML = svg;
    } catch (error) {
      console.error('[DEBUG] Fullscreen render error:', error);
      // Fallback: copy from existing container
      if (this.mermaidContainer?.nativeElement) {
        container.innerHTML = this.mermaidContainer.nativeElement.innerHTML;
      }
    }
  }
  
  private updateFullscreenDiagram() {
    this.renderFullscreenDiagram();
  }
  
  // Zoom and Pan controls
  onFullscreenWheel(event: WheelEvent) {
    event.preventDefault();
    const delta = event.deltaY > 0 ? -0.1 : 0.1;
    const newZoom = Math.max(0.1, this.zoomLevel() + delta);
    this.zoomLevel.set(newZoom);
  }
  
  onFullscreenMouseDown(event: MouseEvent) {
    this.isPanning.set(true);
    this.panStartX = event.clientX;
    this.panStartY = event.clientY;
    this.lastPanX = this.panX();
    this.lastPanY = this.panY();
  }
  
  onFullscreenMouseMove(event: MouseEvent) {
    if (!this.isPanning()) return;
    
    const deltaX = (event.clientX - this.panStartX) / this.zoomLevel();
    const deltaY = (event.clientY - this.panStartY) / this.zoomLevel();
    
    this.panX.set(this.lastPanX + deltaX);
    this.panY.set(this.lastPanY + deltaY);
  }
  
  onFullscreenMouseUp() {
    this.isPanning.set(false);
  }
  
  resetZoom() {
    this.zoomLevel.set(7);
    this.panX.set(0);
    this.panY.set(0);
  }
  
  onDiagramTypeChange(event: Event) {
    const target = event.target as HTMLSelectElement;
    this.selectDesignType(target.value as DesignType);
  }
  
  onDesignTypeSelectChange(value: DesignType) {
    this.selectDesignType(value);
  }
  
  regenerateDiagram() {
    const currentType = this.selectedDesignType();
    if (!this.isDesignLocked(currentType)) {
      this.generateDesign(currentType);
    }
  }
  
  importMermaid() {
    // Could open a file picker or modal for importing
    console.log('Import Mermaid clicked');
  }
  
  copyMermaid() {
    navigator.clipboard.writeText(this.mermaidCode()).then(() => {
      console.log('Mermaid code copied to clipboard');
    });
  }
  
  toggleChat() {
    this.isChatOpen.set(!this.isChatOpen());
  }
  
  // Get status icon for design type
  getStatusIcon(type: DesignType): string {
    const state = this.getDesignState(type);
    switch (state.status) {
      case 'locked': return 'lock';
      case 'available': return 'play_circle';
      case 'generating': return 'sync';
      case 'completed': return 'check_circle';
      case 'error': return 'error';
      default: return 'help';
    }
  }
  
  getStatusColor(type: DesignType): string {
    const state = this.getDesignState(type);
    switch (state.status) {
      case 'locked': return '#666';
      case 'available': return '#4ecdc4';
      case 'generating': return '#ffd93d';
      case 'completed': return '#6bcb77';
      case 'error': return '#ff6b6b';
      default: return '#888';
    }
  }
  
  // Computed values
  get featureCount(): number {
    return this.project?.features?.length || 0;
  }
  
  get storyCount(): number {
    return this.project?.stories?.length || 0;
  }
  
  get approvedStories(): Story[] {
    return this.project?.stories?.filter(s => s.approved) || [];
  }
  
  get completedDesignsCount(): number {
    let count = 0;
    this.designStates().forEach(state => {
      if (state.status === 'completed') count++;
    });
    return count;
  }
  
  get epicsList(): string[] {
    const epics = [];
    if (this.project?.epicIdeas) {
      epics.push(...this.project.epicIdeas.filter(e => e.trim()));
    }
    // Also add template features as epics if no manual epics
    if (epics.length === 0 && this.project) {
      // Use security, compliance, mobile-first as fallback
      epics.push('security', 'compliance', 'mobile-first experience');
    }
    return epics;
  }
  
  get risksList(): string[] {
    if (this.project?.riskHighlights?.length > 0) {
      return this.project.riskHighlights.filter(r => r.trim());
    }
    if (this.project?.generatedRisks) {
      return ['Pending AI insights based on your selected prompts.'];
    }
    return ['Pending AI insights based on your selected prompts.'];
  }
  
  // Parse markdown text to HTML
  get formattedSummary(): string {
    let text = this.project?.executiveSummary || this.project?.promptSummary || 'Deliver a secure, personalised banking experience with account management, payments, and analytics.';
    
    // Convert markdown to HTML
    // Headers: ## -> <strong>
    text = text.replace(/##\s*([^\n#]+)/g, '<strong>$1</strong><br>');
    text = text.replace(/#\s*([^\n#]+)/g, '<strong class="heading">$1</strong><br>');
    
    // Bold: **text** -> <strong>
    text = text.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Line breaks for readability
    text = text.replace(/\n/g, '<br>');
    
    // Numbered items: 1. 2. etc
    text = text.replace(/(\d+)\.\s+/g, '<br><span class="list-number">$1.</span> ');
    
    // Dash items: - item
    text = text.replace(/-\s+([^\n<]+)/g, '<br>• $1');
    
    return text;
  }

  // ============================================================================
  // WIREFRAME GENERATION METHODS
  // ============================================================================
  
  async generateWireframes() {
    console.log('[WIREFRAME] generateWireframes() called');
    console.log('[WIREFRAME] isGeneratingWireframes:', this.isGeneratingWireframes());
    console.log('[WIREFRAME] devMode:', this.devModeService.isDevMode());
    
    if (this.isGeneratingWireframes()) {
      console.log('[WIREFRAME] Already generating, skipping...');
      return;
    }
    
    this.isGeneratingWireframes.set(true);
    this.wireframeProgress.set('Initializing wireframe generation...');
    console.log('[WIREFRAME] Set isGeneratingWireframes to true');
    
    // Reset wireframe viewer progress
    if (this.wireframeViewer) {
      this.wireframeViewer.resetProgress();
    }
    
    try {
      // Check if dev mode is enabled - when ON, make real API calls for testing
      if (!this.devModeService.isDevMode()) {
        console.log('[PROD MODE] Using mock wireframe data');
        const mockData = MOCK_WIREFRAME_DATA as WireframeData;
        
        // Simulate realistic loading steps with live page updates
        this.wireframeProgress.set('Analyzing project structure...');
        await new Promise(resolve => setTimeout(resolve, 800));
        
        // Simulate generating each page with live updates
        for (let i = 0; i < mockData.pages.length; i++) {
          const page = mockData.pages[i];
          
          // Show current page being generated
          if (this.wireframeViewer) {
            const completed = mockData.pages.slice(0, i).map(p => p.name);
            this.wireframeViewer.updatePageProgress(completed, page.name);
          }
          
          this.wireframeProgress.set(`Generating ${page.name}...`);
          await new Promise(resolve => setTimeout(resolve, 1200));
          
          // Mark as completed
          if (this.wireframeViewer) {
            const completed = mockData.pages.slice(0, i + 1).map(p => p.name);
            this.wireframeViewer.updatePageProgress(completed, '');
          }
        }
        
        this.wireframeProgress.set('Finalizing designs...');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        this.wireframeData.set(mockData);
        this.wireframeProgress.set('Wireframes generated successfully!');
        
        // Update wireframe design state to completed
        this.updateDesignState('wireframe', {
          type: 'wireframe',
          status: 'completed',
          mermaidCode: 'WIREFRAME_HTML_PAGES',
          summary: `Generated ${mockData.pages.length} wireframe pages`,
          timestamp: new Date().toLocaleString()
        });
        
      } else {
        // Dev mode is ON - make real API call with retry logic
        console.log('[DEV MODE] Making real API call...');
        
        const summaries = this.designSummaries();
        
        const request = {
          project_summary: this.project?.promptSummary || '',
          features_summary: this.project?.features?.map(f => f.title).join(', ') || '',
          hld_summary: summaries.get('hld') || '',
          api_summary: summaries.get('api') || '',
          // Page count settings
          page_mode: this.wireframePageMode(),
          page_count: this.wireframePageMode() === 'manual' ? this.wireframePageCount() : undefined
        };
        
        console.log('[WIREFRAME] Current wireframePageMode:', this.wireframePageMode());
        console.log('[WIREFRAME] Current wireframePageCount:', this.wireframePageCount());
        console.log('[WIREFRAME] API Request:', request);
        
        // Start progress animation while API call is in progress
        const expectedPages = this.wireframePageMode() === 'manual' ? this.wireframePageCount() : 5;
        const progressPhases = [
          'Analyzing project requirements...',
          'Planning wireframe structure...',
          'Designing page layouts...',
          'Creating responsive components...',
          'Generating HTML/CSS code...',
          'Finalizing wireframes...'
        ];
        let phaseIndex = 0;
        
        // Update progress every 2 seconds
        const progressInterval = setInterval(() => {
          if (phaseIndex < progressPhases.length) {
            this.wireframeProgress.set(progressPhases[phaseIndex]);
            phaseIndex++;
          }
        }, 2000);
        
        // Retry logic with exponential backoff
        const maxRetries = 3;
        let lastError: any = null;
        
        for (let attempt = 1; attempt <= maxRetries; attempt++) {
          try {
            this.wireframeProgress.set(progressPhases[0]);
            
            const response = await this.apiService.generateWireframePages(request).toPromise();
            
            clearInterval(progressInterval);
            console.log('[WIREFRAME] API Response:', response);
            
            if (response && response.pages) {
              // Show live progress as we reveal each page
              this.wireframeProgress.set('Rendering wireframes...');
              
              for (let i = 0; i < response.pages.length; i++) {
                const page = response.pages[i];
                const completed = response.pages.slice(0, i).map(p => p.name);
                
                // Show current page being rendered
                if (this.wireframeViewer) {
                  this.wireframeViewer.updatePageProgress(completed, page.name);
                }
                this.wireframeProgress.set(`Rendering ${page.name}...`);
                await new Promise(resolve => setTimeout(resolve, 300));
                
                // Mark as completed
                if (this.wireframeViewer) {
                  const completedNow = response.pages.slice(0, i + 1).map(p => p.name);
                  this.wireframeViewer.updatePageProgress(completedNow, '');
                }
              }
              
              this.wireframeData.set({
                pages: response.pages,
                shared_components: response.shared_components,
                plan: response.plan,
                metadata: response.metadata
              });
              
              // Update wireframe design state
              this.updateDesignState('wireframe', {
                type: 'wireframe',
                status: 'completed',
                mermaidCode: 'WIREFRAME_HTML_PAGES',
                summary: `Generated ${response.pages.length} wireframe pages`,
                timestamp: new Date().toLocaleString()
              });
              
              this.wireframeProgress.set(`Generated ${response.pages.length} wireframe pages!`);
              return; // Success - exit the retry loop
            }
          } catch (retryError: any) {
            clearInterval(progressInterval);
            lastError = retryError;
            console.warn(`[WIREFRAME] Attempt ${attempt} failed:`, retryError);
            
            if (attempt < maxRetries) {
              // Exponential backoff: 1s, 2s, 4s
              const delay = Math.pow(2, attempt - 1) * 1000;
              this.wireframeProgress.set('Retrying, please wait...');
              await new Promise(resolve => setTimeout(resolve, delay));
            }
          }
        }
        
        // All retries failed
        throw lastError || new Error('Failed after all retry attempts');
      }
      
    } catch (error) {
      console.error('[ERROR] Wireframe generation failed:', error);
      this.wireframeProgress.set('Wireframe generation failed. Please try again.');
      
      this.updateDesignState('wireframe', {
        type: 'wireframe',
        status: 'error',
        error: String(error),
        timestamp: new Date().toLocaleString()
      });
      
    } finally {
      this.isGeneratingWireframes.set(false);
      
      // Reset progress in wireframe viewer
      if (this.wireframeViewer) {
        this.wireframeViewer.resetProgress();
      }
      
      // Clear progress after delay
      setTimeout(() => {
        this.wireframeProgress.set('');
      }, 3000);
    }
  }
  
  async regenerateWireframePage(page: WireframePage) {
    if (this.isGeneratingWireframes()) {
      return;
    }
    
    this.isGeneratingWireframes.set(true);
    this.wireframeProgress.set(`Regenerating ${page.name}...`);
    
    try {
      const currentData = this.wireframeData();
      
      const request = {
        page_id: page.id,
        page_name: page.name,
        page_type: page.type,
        project_context: this.project?.promptSummary || '',
        shared_components: currentData?.shared_components
      };
      
      const response = await this.apiService.regenerateWireframePage(request).toPromise();
      
      if (response && currentData) {
        // Update the page in the wireframe data
        const updatedPages = currentData.pages.map(p => 
          p.id === page.id ? response.page : p
        );
        
        this.wireframeData.set({
          ...currentData,
          pages: updatedPages
        });
        
        this.wireframeProgress.set(`${page.name} regenerated successfully!`);
      }
      
    } catch (error) {
      console.error('[ERROR] Page regeneration failed:', error);
      this.wireframeProgress.set(`Failed to regenerate ${page.name}`);
      
    } finally {
      this.isGeneratingWireframes.set(false);
      
      setTimeout(() => {
        this.wireframeProgress.set('');
      }, 3000);
    }
  }
}