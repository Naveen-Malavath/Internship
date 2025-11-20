import { CommonModule } from '@angular/common';
import {
  Component,
  EventEmitter,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  ViewChild,
  ElementRef,
  AfterViewInit,
  OnDestroy,
  HostListener,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import mermaid from 'mermaid';

import { AgentFeatureSpec, AgentStorySpec, AgentVisualizationResponse, ProjectWizardSubmission } from '../types';
import { DiagramDataService } from '../diagram-data.service';
import { MermaidStyleService, MermaidStyleConfig } from '../services/mermaid-style.service';
import { DesignService, DesignResponse } from '../services/design.service';
import { inject } from '@angular/core';

@Component({
  selector: 'workspace-view',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './workspace-view.component.html',
  styleUrl: './workspace-view.component.scss',
})
export class WorkspaceViewComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() prompt = '';
  @Input() features: AgentFeatureSpec[] = [];
  @Input() stories: AgentStorySpec[] = [];
  @Input() visualization: AgentVisualizationResponse | null = null;
  @Input() project: ProjectWizardSubmission | null = null;
  @Input() projectId: string | null = null; // Project ID for fetching designs from backend
  @Input() mermaidEditorContent = '';
  @Input() mermaidSource: string | null = null;
  @Input() mermaidStyleConfig: MermaidStyleConfig | null = null;
  @Input() designGenerationKey: number | null = null; // Key to track design regenerations and clear cache
  @Input() mermaidSaving = false;
  @Input() mermaidUpdatedAt: string | null = null;
  @Input() mermaidSaveMessage: string | null = null;
  @Output() mermaidChange = new EventEmitter<string>();
  @Output() mermaidSave = new EventEmitter<string>();
  @Output() diagramTypeChange = new EventEmitter<string>();
  @Output() exit = new EventEmitter<void>();
  @Output() featureEdit = new EventEmitter<AgentFeatureSpec>();
  @Output() featureDismiss = new EventEmitter<AgentFeatureSpec>();
  @Output() storyEdit = new EventEmitter<{ feature: AgentFeatureSpec; story: AgentStorySpec }>();
  @Output() storyDismiss = new EventEmitter<{ feature: AgentFeatureSpec; story: AgentStorySpec }>();
  @Output() createProject = new EventEmitter<void>();
  @Output() regenerateDiagram = new EventEmitter<string>();
  @ViewChild('mermaidContainer') private mermaidContainer?: ElementRef<HTMLDivElement>;
  @ViewChild('mermaidFileInput') private mermaidFileInput?: ElementRef<HTMLInputElement>;

  private readonly designService = inject(DesignService);
  private cachedDesigns: DesignResponse | null = null;
  private isLoadingDesigns = false;

  protected mermaidInput = '';
  protected mermaidError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isDotCopied = false;
  protected isMermaidCopied = false;
  private lastValidMermaidSource: string | null = null;
  protected previewTheme: 'dark' | 'light' = 'dark';
  protected currentDiagramType: 'hld' | 'lld' | 'database' = 'hld';
  protected isDiagramDropdownOpen = false;
  protected diagramTypes = [
    { value: 'hld', label: 'HLD', fullLabel: 'High Level Design', description: 'System architecture & business flow' },
    { value: 'lld', label: 'LLD', fullLabel: 'Low Level Design', description: 'Component interactions & implementation' },
    { value: 'database', label: 'DBD', fullLabel: 'Database Design', description: 'ER diagrams & data models' },
  ] as const;
  protected mermaidLineNumbers: number[] = [1];
  protected lineNumberOffset = 0;
  protected previewScale = 1;
  protected previewDisplayScale = 1;
  protected previewFitToContainer = true;
  protected previewOverflowing = false;
  protected showZoomControls = false; // Hide zoom controls by default
  private mermaidInitialised = false;
  private mermaidRenderIndex = 0;
  private copyNotificationTimer: ReturnType<typeof setTimeout> | null = null;
  private previewAutoScale = 1;
  private readonly previewScaleMin = 0.75;
  private readonly previewScaleMax = 3;
  private readonly previewScaleStep = 0.25;
  private readonly mermaidLabelMaxChars = 36;
  private readonly previewReadableScaleFloor = 0.65;

  ngOnChanges(changes: SimpleChanges): void {
    // Handle projectId changes - clear cache when project changes
    if (changes['projectId']) {
      const newProjectId = changes['projectId'].currentValue;
      const oldProjectId = changes['projectId'].previousValue;
      if (newProjectId !== oldProjectId) {
        console.log(`[workspace-view] Project ID changed from ${oldProjectId} to ${newProjectId}, clearing cache`);
        this.clearDesignCache();
        // If we have a projectId, try to load designs
        if (newProjectId && this.currentDiagramType) {
          this.loadDesignFromBackend(this.currentDiagramType);
        }
      }
    }

    // Handle designGenerationKey changes - clear cache when designs are regenerated
    if (changes['designGenerationKey']) {
      const newKey = changes['designGenerationKey'].currentValue;
      const oldKey = changes['designGenerationKey'].previousValue;
      if (newKey !== null && newKey !== oldKey) {
        console.log(`[workspace-view] Design generation key changed from ${oldKey} to ${newKey}, clearing cache for fresh data`);
        this.clearDesignCache();
        // If we have a projectId, reload current diagram type from backend
        if (this.projectId && this.currentDiagramType) {
          this.loadDesignFromBackend(this.currentDiagramType);
        }
      }
    }

    // If mermaidSource changes and we have a projectId, it might be from a design regeneration
    // Clear cache to force fresh fetch on next diagram type change
    if (changes['mermaidSource'] && this.projectId) {
      const newSource = changes['mermaidSource'].currentValue;
      if (newSource && newSource.trim()) {
        console.log(`[workspace-view] mermaidSource updated, clearing cache to ensure fresh data`);
        this.clearDesignCache();
      }
    }

    // Handle mermaidSource changes - highest priority as it's the primary way parent updates content
    if (changes['mermaidSource']) {
      const newSource = changes['mermaidSource'].currentValue;
      // Only update if we have a non-empty string
      if (newSource !== null && typeof newSource === 'string' && newSource.trim() !== '') {
        // Store as last valid source and update editor
        this.lastValidMermaidSource = newSource.trim();
        this.setMermaidInput(newSource, false);
      } else {
        // If newSource is null/empty/undefined, restore from lastValidMermaidSource if available
        // This prevents showing "No data" when we have a valid diagram stored
        if (this.lastValidMermaidSource && this.isDefaultNoDataDiagram(this.mermaidInput)) {
          this.setMermaidInput(this.lastValidMermaidSource, false);
        }
        // Otherwise, keep showing lastValidMermaidSource in renderMermaid()
      }
    }

    if (changes['stories'] && !this.mermaidEditorContent && !this.mermaidSource && !this.mermaidInput && !this.lastValidMermaidSource) {
      this.generateDefaultMermaid();
    }

    if (changes['visualization']) {
      this.visualizationData = this.visualization;
      if (this.visualizationData?.diagrams?.mermaid && !this.mermaidSource) {
        this.setMermaidInput(this.visualizationData.diagrams.mermaid, false);
      }
    }

    if (changes['mermaidEditorContent']) {
      const newContent = changes['mermaidEditorContent'].currentValue;
      // Always update if we have a new non-empty string, regardless of mermaidSource
      // This ensures live preview updates when diagram type changes
      if (typeof newContent === 'string' && newContent.trim() !== '') {
        // Only skip if mermaidSource is explicitly set (higher priority)
        // Otherwise update from mermaidEditorContent
        if (!this.mermaidSource) {
          this.setMermaidInput(newContent, false);
        } else if (this.mermaidSource === newContent.trim()) {
          // If mermaidSource matches, still update to ensure rendering
          this.setMermaidInput(newContent, false);
        }
      }
    }
  }

  ngAfterViewInit(): void {
    // If mermaidSource is provided initially, use it
    if (this.mermaidSource !== null && typeof this.mermaidSource === 'string' && this.mermaidSource.trim() !== '' && !this.mermaidInput) {
      this.lastValidMermaidSource = this.mermaidSource.trim();
      this.setMermaidInput(this.mermaidSource, false);
    } else if (this.projectId && !this.mermaidInput && !this.mermaidEditorContent && !this.visualizationData?.diagrams?.mermaid && !this.mermaidSource) {
      // If we have a projectId, try to load designs from backend first
      console.log(`[workspace-view] Initial load with projectId, fetching designs from backend`);
      this.currentDiagramType = 'hld';
      this.loadDesignFromBackend('hld');
    } else if (!this.mermaidInput && !this.mermaidEditorContent && !this.visualizationData?.diagrams?.mermaid && !this.mermaidSource) {
      // Load HLD diagram by default if no mermaid content exists (fallback for non-project contexts)
      this.currentDiagramType = 'hld';
      this.loadPredefinedDiagram('hld');
    } else {
      this.renderMermaid();
    }
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    this.applyPreviewScale();
  }

  ngOnDestroy(): void {
    if (this.copyNotificationTimer) {
      clearTimeout(this.copyNotificationTimer);
      this.copyNotificationTimer = null;
    }
  }

  protected onExit(): void {
    this.exit.emit();
  }

  protected onMermaidInput(value: string): void {
    this.setMermaidInput(value, true);
    this.isMermaidCopied = false;
  }

  protected onMermaidScroll(event: Event): void {
    const target = event.target as HTMLTextAreaElement | null;
    this.lineNumberOffset = target?.scrollTop ?? 0;
  }

  protected onMermaidSave(): void {
    this.mermaidSave.emit(this.mermaidInput);
  }

  protected onMermaidUploadClick(): void {
    this.mermaidFileInput?.nativeElement?.click();
  }

  protected onMermaidFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement | null;
    const file = input?.files?.[0];

    if (!file) {
      return;
    }

    const reader = new FileReader();

    reader.onload = () => {
      const result = typeof reader.result === 'string' ? reader.result : '';
      if (!result.trim()) {
        this.mermaidError = 'Uploaded file is empty.';
      } else {
        this.setMermaidInput(result, true);
        this.mermaidError = null;
      }
      if (this.mermaidFileInput?.nativeElement) {
        this.mermaidFileInput.nativeElement.value = '';
      }
    };

    reader.onerror = () => {
      this.mermaidError = 'Unable to read the Mermaid file.';
      if (this.mermaidFileInput?.nativeElement) {
        this.mermaidFileInput.nativeElement.value = '';
      }
    };

    reader.readAsText(file);
  }

  protected onMermaidCopy(): void {
    if (!navigator?.clipboard) {
      return;
    }

    navigator.clipboard
      .writeText(this.mermaidInput)
      .then(() => {
        this.isMermaidCopied = true;
        if (this.copyNotificationTimer) {
          clearTimeout(this.copyNotificationTimer);
        }
        this.copyNotificationTimer = setTimeout(() => {
          this.isMermaidCopied = false;
        }, 2000);
      })
      .catch(() => {
        this.isMermaidCopied = false;
      });
  }

  protected togglePreviewTheme(): void {
    this.previewTheme = this.previewTheme === 'dark' ? 'light' : 'dark';
    this.mermaidInitialised = false;
    void this.renderMermaid();
  }

  protected zoomIn(): void {
    this.previewScale = this.clampScale(this.previewScale + this.previewScaleStep);
    this.applyPreviewScale();
  }

  protected zoomOut(): void {
    this.previewScale = this.clampScale(this.previewScale - this.previewScaleStep);
    this.applyPreviewScale();
  }

  protected resetZoom(): void {
    this.previewScale = 1;
    this.applyPreviewScale();
  }

  protected togglePreviewFit(): void {
    this.previewFitToContainer = !this.previewFitToContainer;
    this.applyPreviewScale();
  }

  protected canZoomIn(): boolean {
    return this.previewScale < this.previewScaleMax - 0.001;
  }

  protected canZoomOut(): boolean {
    return this.previewScale > this.previewScaleMin + 0.001;
  }

  protected onFeatureEdit(feature: AgentFeatureSpec): void {
    this.featureEdit.emit(feature);
  }

  protected onFeatureDismiss(feature: AgentFeatureSpec): void {
    this.featureDismiss.emit(feature);
  }

  protected onCreateProject(): void {
    this.createProject.emit();
  }

  protected onDiagramTypeChange(type: 'hld' | 'lld' | 'database'): void {
    if (this.currentDiagramType !== type) {
      this.currentDiagramType = type;
      this.isDiagramDropdownOpen = false;
      
      // If we have a projectId, fetch designs from backend instead of using static templates
      if (this.projectId) {
        console.log(`[workspace-view] Diagram type changed to ${type}, fetching from backend for project ${this.projectId}`);
        this.loadDesignFromBackend(type);
      } else {
        console.log(`[workspace-view] No projectId available, using static template for ${type}`);
        // Load predefined diagram based on type (fallback for non-project contexts)
        this.loadPredefinedDiagram(type);
      }
      
      // Emit event to parent to trigger diagram regeneration
      this.diagramTypeChange.emit(type);
    }
  }

  protected onRegenerateDiagram(): void {
    // Emit event to regenerate diagram with current type
    this.regenerateDiagram.emit(this.currentDiagramType);
  }

  /**
   * Load design from backend for the given diagram type.
   * Uses cached designs if available, otherwise fetches from API.
   */
  private loadDesignFromBackend(type: 'hld' | 'lld' | 'database'): void {
    if (!this.projectId || this.isLoadingDesigns) {
      console.warn(`[workspace-view] Cannot load design: projectId=${this.projectId}, isLoading=${this.isLoadingDesigns}`);
      return;
    }

    // If we have cached designs, use them immediately
    if (this.cachedDesigns) {
      console.log(`[workspace-view] Using cached designs for type ${type}`);
      this.applyDesignFromCache(type);
      return;
    }

    // Otherwise, fetch from backend
    console.log(`[workspace-view] Fetching designs from backend for project ${this.projectId}`);
    this.isLoadingDesigns = true;
    
    this.designService.getLatestDesigns(this.projectId).subscribe({
      next: (designs) => {
        console.log(`[workspace-view] Successfully fetched designs:`, {
          hasHLD: !!designs.hld_mermaid,
          hasLLD: !!designs.lld_mermaid,
          hasDBD: !!designs.dbd_mermaid,
          hldLength: designs.hld_mermaid?.length || 0,
          lldLength: designs.lld_mermaid?.length || 0,
          dbdLength: designs.dbd_mermaid?.length || 0,
        });
        
        // Cache the designs
        this.cachedDesigns = designs;
        
        // Apply the design for the requested type
        this.applyDesignFromCache(type);
        
        // Update style config if available
        if (designs.style_config) {
          // Note: style_config is passed via @Input, so parent should handle this
          console.log(`[workspace-view] Style config available:`, designs.style_config);
        }
        
        this.isLoadingDesigns = false;
      },
      error: (err) => {
        console.error(`[workspace-view] Failed to fetch designs:`, err);
        this.isLoadingDesigns = false;
        
        // Fallback to static template on error
        console.log(`[workspace-view] Falling back to static template for ${type}`);
        this.loadPredefinedDiagram(type);
      },
    });
  }

  /**
   * Apply design from cache for the given diagram type.
   */
  private applyDesignFromCache(type: 'hld' | 'lld' | 'database'): void {
    if (!this.cachedDesigns) {
      console.warn(`[workspace-view] No cached designs available`);
      return;
    }

    let diagramContent = '';
    const typeUpper = type.toUpperCase() as 'HLD' | 'LLD' | 'DBD';
    
    switch (typeUpper) {
      case 'HLD':
        diagramContent = this.cachedDesigns.hld_mermaid || '';
        break;
      case 'LLD':
        diagramContent = this.cachedDesigns.lld_mermaid || '';
        break;
      case 'DBD':
        diagramContent = this.cachedDesigns.dbd_mermaid || '';
        break;
    }

    if (diagramContent && diagramContent.trim()) {
      console.log(`[workspace-view] Applying ${type} design (${diagramContent.length} chars)`);
      // Validate that the diagram contains actual content, not just whitespace
      const trimmed = diagramContent.trim();
      if (trimmed.length < 10) {
        console.warn(`[workspace-view] ${type} design seems too short (${trimmed.length} chars), may be invalid`);
      }
      this.setMermaidInput(diagramContent, true);
      this.previewFitToContainer = true;
      this.previewScale = 1;
      this.mermaidError = null;
      
      const timeout = type === 'lld' ? 350 : 200;
      setTimeout(() => {
        this.applyPreviewScale();
      }, timeout);
    } else {
      console.warn(`[workspace-view] No ${type} design available in cache, using static template`);
      this.loadPredefinedDiagram(type);
    }
  }

  /**
   * Clear the cached designs (useful when designs are regenerated).
   */
  private clearDesignCache(): void {
    console.log(`[workspace-view] Clearing design cache`);
    this.cachedDesigns = null;
  }

  /**
   * Load predefined static diagram (fallback when no backend designs available).
   */
  protected loadPredefinedDiagram(type: 'hld' | 'lld' | 'database'): void {
    let diagramContent = '';
    
    switch (type) {
      case 'hld':
        diagramContent = DiagramDataService.getHLDDiagram();
        break;
      case 'lld':
        // Pass actual features and stories for dynamic LLD generation
        diagramContent = DiagramDataService.getLLDDiagram(this.features, this.stories, this.prompt);
        break;
      case 'database':
        diagramContent = DiagramDataService.getDBDDiagram();
        break;
    }
    
    if (diagramContent) {
      console.log(`[workspace-view] Using static template for ${type}`);
      this.setMermaidInput(diagramContent, true);
      // Reset zoom to show full diagram
      this.previewFitToContainer = true;
      this.previewScale = 1;
      this.mermaidError = null; // Clear any previous errors
      
      // Render will be triggered by setMermaidInput, then apply scale after render
      // Longer timeout for LLD to ensure proper sizing
      const timeout = type === 'lld' ? 350 : 200;
      setTimeout(() => {
        this.applyPreviewScale();
      }, timeout);
    }
  }

  protected getDiagramTypeLabel(type: string): string {
    const found = this.diagramTypes.find((dt) => dt.value === type);
    return found ? found.fullLabel : 'High Level Design';
  }

  protected getCurrentDiagramTypeLabel(): string {
    return this.getDiagramTypeLabel(this.currentDiagramType);
  }

  protected toggleDiagramDropdown(): void {
    this.isDiagramDropdownOpen = !this.isDiagramDropdownOpen;
  }

  protected closeDiagramDropdown(): void {
    this.isDiagramDropdownOpen = false;
  }

  protected isDiagramTypeActive(type: string): boolean {
    return this.currentDiagramType === type;
  }

  protected shouldShowNoDiagramMessage(): boolean {
    // Only show "No diagram available" if:
    // 1. lastValidMermaidSource is null (never had a valid diagram)
    // 2. mermaidInput is empty or is the default "No data" diagram
    // 3. Not currently loading (mermaidSaving is false)
    const isEmptyOrDefault = !this.mermaidInput.trim() || this.isDefaultNoDataDiagram(this.mermaidInput);
    return this.lastValidMermaidSource === null && isEmptyOrDefault && !this.mermaidSaving;
  }

  /**
   * Check if the given mermaid string is the default "No data" diagram.
   */
  private isDefaultNoDataDiagram(mermaid: string): boolean {
    if (!mermaid) return false;
    const trimmed = mermaid.trim().toLowerCase();
    // Check for common "No data" patterns
    return trimmed.includes('no data') || 
           (trimmed.includes('graph') && trimmed.includes('a["no data"]')) ||
           trimmed === 'graph td\na["no data"]';
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (!target.closest('.diagram-type-dropdown')) {
      this.isDiagramDropdownOpen = false;
    }
  }

  protected onStoryEdit(feature: AgentFeatureSpec, story: AgentStorySpec): void {
    this.storyEdit.emit({ feature, story });
  }

  protected onStoryDismiss(feature: AgentFeatureSpec, story: AgentStorySpec): void {
    this.storyDismiss.emit({ feature, story });
  }

  protected copyVisualizationDot(code: string): void {
    if (!navigator?.clipboard) {
      this.isDotCopied = false;
      return;
    }

    navigator.clipboard
      .writeText(code)
      .then(() => {
        this.isDotCopied = true;
        setTimeout(() => {
          this.isDotCopied = false;
        }, 2000);
      })
      .catch(() => {
        this.isDotCopied = false;
      });
  }

  private generateDefaultMermaid(): void {
    const lines: string[] = ['graph TD'];
    const promptNode = this.escapeMermaidId('prompt');
    const promptLabel = this.formatMermaidLabel(this.prompt || 'Customer Request');
    lines.push(`${promptNode}["${promptLabel}"]`);

    this.features.forEach((feature, index) => {
      const featureId = this.escapeMermaidId(`feature_${index}`);
      const featureLabel = this.formatMermaidLabel(feature.title || `Feature ${index + 1}`);
      lines.push(`${promptNode} --> ${featureId}["${featureLabel}"]`);
      this.stories
        .filter((story) => story.featureTitle === feature.title)
        .forEach((story, storyIndex) => {
          const storyId = this.escapeMermaidId(`story_${index}_${storyIndex}`);
          const storyLabel = this.formatMermaidLabel(story.userStory || `Story ${storyIndex + 1}`);
          lines.push(`${featureId} --> ${storyId}["${storyLabel}"]`);
        });
    });

    if (lines.length === 1) {
      lines.push('A[No data]');
    }

    this.setMermaidInput(lines.join('\n'), true);
  }

  private formatMermaidLabel(value: string): string {
    const trimmed = (value || '').trim();
    if (!trimmed) {
      return this.escapeHtml('Untitled');
    }

    const words = trimmed.split(/\s+/);
    const lines: string[] = [];
    let current = '';

    words.forEach((word) => {
      const candidate = current ? `${current} ${word}` : word;
      if (candidate.length > this.mermaidLabelMaxChars && current) {
        lines.push(current);
        current = word;
      } else {
        current = candidate;
      }
    });

    if (current) {
      lines.push(current);
    }

    const escapedLines = lines.map((line) => this.escapeHtml(line));
    return escapedLines.join('<br/>');
  }

  private setMermaidInput(value: string, emitEvent: boolean): void {
    let sanitized = this.sanitizeMermaidDefinition(value);
    
    // Fix common Mermaid syntax issues before rendering
    sanitized = this.fixMermaidSyntax(sanitized);
    
    this.mermaidInput = sanitized;
    
    // Update lastValidMermaidSource if we have a non-empty value
    if (sanitized.trim() !== '') {
      this.lastValidMermaidSource = sanitized.trim();
    }
    
    this.updateLineNumbers();
    this.lineNumberOffset = 0;
    if (emitEvent) {
      this.mermaidChange.emit(this.mermaidInput);
    }
    this.mermaidError = null;
    void this.renderMermaid();
  }

  /**
   * Fix common Mermaid syntax issues in generated diagrams.
   * Handles malformed node shapes, missing brackets, and subgraph formatting.
   */
  private fixMermaidSyntax(mermaid: string): string {
    if (!mermaid || !mermaid.trim()) {
      return mermaid;
    }

    const lines = mermaid.split('\n');
    const fixedLines: string[] = [];
    let inSubgraph = false;

    for (let i = 0; i < lines.length; i++) {
      let line = lines[i];
      const stripped = line.trim();

      // Skip empty lines and comments
      if (!stripped || stripped.startsWith('%%')) {
        fixedLines.push(line);
        continue;
      }

      // Track subgraph state
      if (stripped.startsWith('subgraph')) {
        inSubgraph = true;
        fixedLines.push(line);
        continue;
      } else if (stripped === 'end') {
        inSubgraph = false;
        fixedLines.push(line);
        continue;
      }

      // Fix malformed node shapes - must be complete
      // Fix incomplete stadium: (["text -> (["text"])
      if (stripped.includes('(["') && !stripped.match(/\(\["[^"]*"\]\)/)) {
        const match = stripped.match(/\(\["([^"]*?)(?:"|$)/);
        if (match) {
          const text = match[1] || 'text';
          // Replace the incomplete pattern with complete one
          line = line.replace(/\(\["[^"]*?(?:"\]\)|$)/, `(["${text}"])`);
        }
      }

      // Fix incomplete circle: ((text -> ((text))
      // Must match complete pattern: ((text))
      if (stripped.includes('((') && !stripped.match(/\(\([^)]+\)\)/)) {
        const match = stripped.match(/\(\(([^)]*?)(?:\)|$)/);
        if (match) {
          const text = match[1] || 'text';
          // Replace incomplete pattern
          line = line.replace(/\(\([^)]*?(?:\)\)|$)/, `((${text}))`);
        }
      }

      // Fix nodes inside subgraphs - ensure proper formatting
      if (inSubgraph && stripped) {
        const isDirection = stripped.startsWith('direction');
        
        // Check if this is a standalone node definition (not a connection)
        // Pattern: nodeId((text)) or nodeId(["text"]) or nodeId["text"] or nodeId{text}
        // Also handle cases where there might be extra spaces or formatting issues
        const standaloneNodePattern = /^\s*(\w+)\s*(\(\([^)]+\)\)|\(\["[^"]+"\]\)|\[[^\]]+\]|\{[^}]+\})\s*$/;
        const isStandaloneNode = standaloneNodePattern.test(stripped);
        
        // Also check for nodes that might be on the same line as subgraph label
        // Pattern: "subgraph label"] nodeId((text)) - this is invalid
        const nodeAfterSubgraphLabel = /\]\s+(\w+)\s*(\(\(|\(\[|\[|\{)/.test(line);
        
        // Check if this is a connection line
        const isConnection = stripped.includes('-->') || stripped.includes('->') || stripped.includes('==>') || stripped.includes('-.->');
        
        // If node appears after subgraph label on same line, split it
        if (nodeAfterSubgraphLabel) {
          const parts = line.split(/\]\s+/);
          if (parts.length > 1) {
            fixedLines.push(parts[0] + ']');
            line = '    ' + parts[1].trim();
          }
        }
        
        // If it's a standalone node in a subgraph, ensure proper formatting
        if (isStandaloneNode) {
          const match = stripped.match(standaloneNodePattern);
          if (match) {
            const nodeId = match[1];
            const nodeShape = match[2];
            // Ensure proper indentation and formatting - must be on its own line
            line = `    ${nodeId}${nodeShape}`;
          }
        } else if (isConnection && !line.startsWith('    ') && !isDirection) {
          // Connections in subgraphs also need indentation
          line = '    ' + line.trimStart();
        } else if (!isConnection && !isStandaloneNode && !isDirection && !line.startsWith('    ')) {
          // Other content in subgraphs (like node definitions) need indentation
          // Match patterns like: nodeId((text)) or nodeId["text"] at start of line
          if (stripped.match(/^\w+\s*[\[\(]/)) {
            line = '    ' + line.trimStart();
          }
        }
      }

      // Ensure proper spacing around arrows (but preserve existing spacing)
      line = line.replace(/(\w+)(->|-->|==>|-.->)(\w+)/g, '$1 $2 $3');

      fixedLines.push(line);
    }

    let fixedMermaid = fixedLines.join('\n');
    
    // Final pass: Fix any remaining issues with nodes in subgraphs
    // Ensure nodes are on separate lines and properly indented
    const finalLines = fixedMermaid.split('\n');
    const finalFixed: string[] = [];
    let inSubgraphFinal = false;
    
    for (let i = 0; i < finalLines.length; i++) {
      let line = finalLines[i];
      const stripped = line.trim();
      
      if (stripped.startsWith('subgraph')) {
        inSubgraphFinal = true;
        finalFixed.push(line);
        continue;
      } else if (stripped === 'end') {
        inSubgraphFinal = false;
        finalFixed.push(line);
        continue;
      }
      
      if (inSubgraphFinal && stripped) {
        // If line contains a node definition but also other content, try to split it
        // Pattern: "text"] nodeId((text)) - split at the ]
        if (stripped.includes(']') && /\]\s+\w+\s*[\[\(]/.test(stripped)) {
          const splitIndex = stripped.indexOf(']') + 1;
          const before = stripped.substring(0, splitIndex);
          const after = stripped.substring(splitIndex).trim();
          finalFixed.push(before);
          if (after) {
            finalFixed.push('    ' + after);
          }
          continue;
        }
        
        // Ensure standalone nodes in subgraphs are properly indented
        if (stripped.match(/^\w+\s*(\(\(|\(\[|\[|\{)/) && !line.startsWith('    ')) {
          line = '    ' + stripped;
        }
      }
      
      finalFixed.push(line);
    }
    
    return finalFixed.join('\n');
  }

  async renderMermaid(): Promise<void> {
    if (!this.mermaidContainer) {
      return;
    }

    // Use lastValidMermaidSource if mermaidInput is empty or is the default "No data" diagram
    let sourceToRender = this.mermaidInput.trim();
    
    // If mermaidInput is empty or is the "No data" diagram, use lastValidMermaidSource instead
    if (!sourceToRender || this.isDefaultNoDataDiagram(sourceToRender)) {
      sourceToRender = this.lastValidMermaidSource || '';
    }
    
    // Only show "No diagram available" if:
    // 1. lastValidMermaidSource is null (never had a valid diagram)
    // 2. Not currently loading (mermaidSaving is false)
    if (!sourceToRender) {
      if (this.lastValidMermaidSource === null && !this.mermaidSaving) {
        this.mermaidContainer.nativeElement.innerHTML = '<p class="mermaid-placeholder">No diagram available.</p>';
      }
      // If we're loading or have a lastValidMermaidSource, don't show placeholder
      // (will keep showing the last rendered diagram)
      this.mermaidError = null;
      return;
    }

    // Configure Mermaid with better defaults for larger diagrams
    // Enhanced sizing for LLD diagrams
    const isLLD = this.currentDiagramType === 'lld' || 
                  sourceToRender.includes('Feature Components') || 
                  sourceToRender.includes('Story Components');
    const padding = isLLD ? 30 : 20;
    const nodeSpacing = isLLD ? 60 : 50;
    const rankSpacing = isLLD ? 80 : 60;
    
    // Generate Mermaid config from style configuration (if available)
    // Use dynamic styles from backend, or fallback to default
    const mermaidConfig = MermaidStyleService.generateMermaidConfig(
      this.mermaidStyleConfig,
      {
        isLLD,
        padding,
        nodeSpacing,
        rankSpacing,
      }
    );
    
    // Override theme with previewTheme if user has manually selected it
    // But prefer style config theme if available
    if (this.mermaidStyleConfig) {
      mermaidConfig.theme = this.mermaidStyleConfig.theme || this.previewTheme;
    } else {
      mermaidConfig.theme = this.previewTheme;
    }
    
    mermaid.initialize(mermaidConfig as any);
    this.mermaidInitialised = true;

    const definition = sourceToRender.replace(/^\uFEFF/, '').trim();
    if (!definition) {
      // This shouldn't happen due to check above, but handle it gracefully
      if (this.lastValidMermaidSource === null && !this.mermaidSaving) {
        this.mermaidContainer.nativeElement.innerHTML = '<p class="mermaid-placeholder">No diagram available.</p>';
      }
      this.mermaidError = null;
      return;
    }

    const renderId = `mermaid-diagram-${this.mermaidRenderIndex++}`;

    try {
      await mermaid.parse(definition);
      const { svg } = await mermaid.render(renderId, definition);
      const wrapper = document.createElement('div');
      wrapper.className = 'mermaid-svg-wrapper';
      wrapper.innerHTML = svg;
      this.mermaidContainer.nativeElement.innerHTML = '';
      this.mermaidContainer.nativeElement.appendChild(wrapper);
      
      // Store as last valid source after successful render
      this.lastValidMermaidSource = definition;
      
      // Add data attribute for LLD diagrams to help with styling
      if (this.currentDiagramType === 'lld') {
        const svgElement = wrapper.querySelector('svg');
        if (svgElement) {
          svgElement.setAttribute('data-diagram-type', 'lld');
        }
        this.mermaidContainer.nativeElement.setAttribute('lld-diagram', 'true');
      }
      
      this.mermaidError = null;
      
      // Ensure fit to container is enabled for proper display
      this.previewFitToContainer = true;
      
      // Use longer timeout for LLD diagrams to ensure proper rendering and sizing
      const timeout = this.currentDiagramType === 'lld' ? 300 : 100;
      setTimeout(() => {
        this.applyPreviewScale();
      }, timeout);
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Mermaid syntax error. Please review the diagram definition.';
      this.mermaidError = message;
      this.mermaidContainer.nativeElement.innerHTML = '';
      console.error('Mermaid render error:', error);
    }
  }

  private escapeHtml(value: string): string {
    return value
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/`/g, '&#96;');
  }

  private escapeMermaidId(value: string): string {
    return value.replace(/[^a-zA-Z0-9_]/g, '_');
  }

  private sanitizeMermaidDefinition(value: string): string {
    if (!value) {
      return '';
    }

    const normalised = value.replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
    const withQuotedNodes = normalised.replace(/\[(?!["!])([^\]\n]+?)\]/g, (_, label: string) => {
      const escapedLabel = label.replace(/"/g, '\\"');
      return `["${escapedLabel}"]`;
    });

    const withQuotedParticipants = withQuotedNodes.replace(
      /(participant\s+[^\s]+\s+as\s+)([^"\n][^\n]*)/g,
      (_, prefix: string, label: string) => {
        const trimmedLabel = label.trim();
        const escaped = trimmedLabel.replace(/"/g, '\\"');
        return `${prefix}"${escaped}"`;
      },
    );

    return withQuotedParticipants;
  }

  private updateLineNumbers(): void {
    const lines = this.mermaidInput.split('\n').length || 1;
    this.mermaidLineNumbers = Array.from({ length: lines }, (_, index) => index + 1);
  }

  private clampScale(value: number): number {
    const fixed = Number(value.toFixed(2));
    return Math.min(this.previewScaleMax, Math.max(this.previewScaleMin, fixed));
  }

  private applyPreviewScale(): void {
    if (!this.mermaidContainer) {
      return;
    }

    const svgWrapper = this.mermaidContainer.nativeElement.querySelector('.mermaid-svg-wrapper') as HTMLElement | null;
    const svg = svgWrapper?.querySelector('svg');
    if (!svgWrapper || !svg) {
      return;
    }

    svg.removeAttribute('width');
    svg.removeAttribute('height');

    const viewBox = svg.viewBox?.baseVal;
    const bbox = svg.getBBox();
    const fallbackBox = svg.getBoundingClientRect();

    const naturalWidth = Math.max(1, viewBox?.width || bbox.width || fallbackBox.width || 600);
    const naturalHeight = Math.max(1, viewBox?.height || bbox.height || fallbackBox.height || 400);

    const previewHost = this.mermaidContainer.nativeElement.closest('.preview-scroll') as HTMLElement | null;
    const availableWidth = previewHost?.clientWidth || this.mermaidContainer.nativeElement.clientWidth || naturalWidth;
    const availableHeight = previewHost?.clientHeight || this.mermaidContainer.nativeElement.clientHeight || naturalHeight;

    const { scale: autoScale, overflowing } = this.calculateAutoScale(naturalWidth, naturalHeight, availableWidth, availableHeight);
    this.previewAutoScale = autoScale;
    this.previewOverflowing = overflowing && this.previewFitToContainer;

    svg.style.transformOrigin = 'center center';
    svg.style.display = 'block';
    svgWrapper.style.transformOrigin = 'center center';
    svgWrapper.style.display = 'flex';
    svgWrapper.style.justifyContent = 'center';
    svgWrapper.style.alignItems = 'center';
    svgWrapper.style.gap = '0';

    if (this.previewFitToContainer) {
      // Calculate scale to fit diagram in container while maintaining aspect ratio
      // Allow scaling up to 200% for better visibility, especially for LLD diagrams
      const scaleWidth = availableWidth / naturalWidth;
      const scaleHeight = availableHeight / naturalHeight;
      
      // For LLD diagrams (which can be complex), allow larger scale up to 200%
      // For other diagrams, use up to 150%
      const maxScaleForLLD = this.currentDiagramType === 'lld' ? 2.0 : 1.5;
      const fitScale = Math.min(scaleWidth, scaleHeight, maxScaleForLLD);
      
      // Ensure minimum size for readability - use at least 80% of container width/height for better visibility
      // Or ensure minimum width of 800px for LLD diagrams
      const minWidthForLLD = this.currentDiagramType === 'lld' ? 900 : 700;
      const minScaleWidth = minWidthForLLD / naturalWidth;
      const minScaleHeight = (availableHeight * 0.8) / naturalHeight;
      const minScale = Math.max(0.8, Math.min(minScaleWidth, minScaleHeight, 1.0));
      
      const finalScale = Math.max(fitScale, minScale);
      
      const displayWidth = naturalWidth * finalScale;
      const displayHeight = naturalHeight * finalScale;
      
      svgWrapper.style.width = `${displayWidth}px`;
      svgWrapper.style.maxWidth = '100%';
      svgWrapper.style.height = `${displayHeight}px`;
      svgWrapper.style.maxHeight = '100%';
      
      svg.style.width = `${displayWidth}px`;
      svg.style.height = `${displayHeight}px`;
      svg.style.maxWidth = '100%';
      svg.style.maxHeight = '100%';
    } else {
      svgWrapper.style.width = `${naturalWidth}px`;
      svgWrapper.style.height = `${naturalHeight}px`;
      svgWrapper.style.maxWidth = 'none';
      svgWrapper.style.maxHeight = 'none';
      svg.style.width = `${naturalWidth}px`;
      svg.style.height = `${naturalHeight}px`;
      svg.style.maxWidth = 'none';
      svg.style.maxHeight = 'none';
    }

    const baseScale = this.previewFitToContainer ? 1 : 1; // Always use 1 for fit to container
    const effectiveScale = baseScale * this.previewScale;
    this.previewDisplayScale = Number(effectiveScale.toFixed(3));

    if (Math.abs(effectiveScale - 1) < 0.001) {
      svgWrapper.style.removeProperty('transform');
    } else {
      svgWrapper.style.transform = `scale(${effectiveScale})`;
    }
  }

  private calculateAutoScale(
    naturalWidth: number,
    naturalHeight: number,
    availableWidth: number,
    availableHeight: number,
  ): { scale: number; overflowing: boolean } {
    if (!naturalWidth || !naturalHeight) {
      return { scale: 1, overflowing: false };
    }

    const needsWidthFit = naturalWidth > availableWidth;
    const needsHeightFit = naturalHeight > availableHeight;

    if (!needsWidthFit && !needsHeightFit) {
      return { scale: 1, overflowing: false };
    }

    const ratios: number[] = [];
    if (needsWidthFit && Number.isFinite(availableWidth / naturalWidth)) {
      ratios.push(availableWidth / naturalWidth);
    }
    if (needsHeightFit && Number.isFinite(availableHeight / naturalHeight)) {
      ratios.push(availableHeight / naturalHeight);
    }

    if (!ratios.length) {
      return { scale: 1, overflowing: needsWidthFit || needsHeightFit };
    }

    const targetScale = Math.min(1, ...ratios);
    if (!Number.isFinite(targetScale) || targetScale <= 0) {
      return { scale: 1, overflowing: false };
    }

    if (targetScale < this.previewReadableScaleFloor) {
      return { scale: this.previewReadableScaleFloor, overflowing: true };
    }

    return { scale: Number(targetScale.toFixed(3)), overflowing: false };
  }
}

