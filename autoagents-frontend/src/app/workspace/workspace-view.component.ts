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
  @Input() mermaidEditorContent = '';
  @Input() mermaidSource: string | null = null;
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

  protected mermaidInput = '';
  protected mermaidError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isDotCopied = false;
  protected isMermaidCopied = false;
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
    // Handle mermaidSource changes - highest priority as it's the primary way parent updates content
    if (changes['mermaidSource']) {
      const newSource = changes['mermaidSource'].currentValue;
      if (newSource !== null && typeof newSource === 'string') {
        this.setMermaidInput(newSource, false);
      } else if (newSource === null && this.mermaidInput) {
        // Clear editor if source becomes null
        this.setMermaidInput('', false);
      }
    }

    if (changes['stories'] && !this.mermaidEditorContent && !this.mermaidSource && !this.mermaidInput) {
      this.generateDefaultMermaid();
    }

    if (changes['visualization']) {
      this.visualizationData = this.visualization;
      if (this.visualizationData?.diagrams?.mermaid && !this.mermaidSource) {
        this.setMermaidInput(this.visualizationData.diagrams.mermaid, false);
      }
    }

    if (changes['mermaidEditorContent'] && typeof changes['mermaidEditorContent'].currentValue === 'string' && !this.mermaidSource) {
      this.setMermaidInput(changes['mermaidEditorContent'].currentValue, false);
    }
  }

  ngAfterViewInit(): void {
    // If mermaidSource is provided initially, use it
    if (this.mermaidSource !== null && typeof this.mermaidSource === 'string' && !this.mermaidInput) {
      this.setMermaidInput(this.mermaidSource, false);
    } else if (!this.mermaidInput && !this.mermaidEditorContent && !this.visualizationData?.diagrams?.mermaid && !this.mermaidSource) {
      // Load HLD diagram by default if no mermaid content exists
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
      
      // Load predefined diagram based on type
      this.loadPredefinedDiagram(type);
      
      // Emit event to parent to trigger diagram regeneration
      this.diagramTypeChange.emit(type);
    }
  }

  protected onRegenerateDiagram(): void {
    // Emit event to regenerate diagram with current type
    this.regenerateDiagram.emit(this.currentDiagramType);
  }

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
    this.mermaidInput = this.sanitizeMermaidDefinition(value);
    this.updateLineNumbers();
    this.lineNumberOffset = 0;
    if (emitEvent) {
      this.mermaidChange.emit(this.mermaidInput);
    }
    this.mermaidError = null;
    void this.renderMermaid();
  }

  async renderMermaid(): Promise<void> {
    if (!this.mermaidContainer) {
      return;
    }

    // Configure Mermaid with better defaults for larger diagrams
    // Enhanced sizing for LLD diagrams
    const isLLD = this.currentDiagramType === 'lld' || 
                  this.mermaidInput.includes('Feature Components') || 
                  this.mermaidInput.includes('Story Components');
    const baseFontSize = isLLD ? '18px' : '16px';
    const padding = isLLD ? 30 : 20;
    const nodeSpacing = isLLD ? 60 : 50;
    const rankSpacing = isLLD ? 80 : 60;
    
    mermaid.initialize({ 
      startOnLoad: false, 
      theme: this.previewTheme,
      themeVariables: {
        fontSize: baseFontSize,
        fontFamily: 'Arial, sans-serif',
        primaryColor: '#3b82f6',
        primaryTextColor: '#fff',
        primaryBorderColor: '#1e40af',
        lineColor: '#64748b',
        secondaryColor: '#10b981',
        tertiaryColor: '#f59e0b',
      },
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis',
        padding: padding,
        nodeSpacing: nodeSpacing,
        rankSpacing: rankSpacing,
      }
    } as any);
    this.mermaidInitialised = true;

    const definition = this.mermaidInput.replace(/^\uFEFF/, '').trim();
    if (!definition) {
      this.mermaidContainer.nativeElement.innerHTML = '<p class="mermaid-placeholder">Enter Mermaid code to render a diagram.</p>';
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

