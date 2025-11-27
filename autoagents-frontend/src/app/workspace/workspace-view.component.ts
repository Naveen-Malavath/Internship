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
import { FeedbackChatbotComponent } from '../feedback/feedback-chatbot.component';
import { normalizeMermaid, stripBomAndZwsp, validateWithMermaid } from '../shared/mermaid/mermaid-lint';
import { initializeMermaidOnce } from '../shared/mermaid/mermaid-init.guard';

@Component({
  selector: 'workspace-view',
  standalone: true,
  imports: [CommonModule, FormsModule, FeedbackChatbotComponent],
  templateUrl: './workspace-view.component.html',
  styleUrl: './workspace-view.component.scss',
})
export class WorkspaceViewComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input() prompt = '';
  @Input() features: AgentFeatureSpec[] = [];
  @Input() stories: AgentStorySpec[] = [];
  @Input() visualization: AgentVisualizationResponse | null = null;
  @Input() project: ProjectWizardSubmission | null = null;
  @Input() projectId: string | null = null;
  @Input() mermaidEditorContent = '';
  @Input() mermaidSource: string | null = null;
  @Input() mermaidSaving = false;
  @Input() mermaidUpdatedAt: string | null = null;
  @Input() mermaidSaveMessage: string | null = null;
  @Input() mermaidStyleConfig: any = null;
  @Input() designGenerationKey: number | null = null;
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
  @Output() contentRegenerated = new EventEmitter<{ type: string; itemId: string; content: any }>();
  @ViewChild('mermaidContainer') private mermaidContainer?: ElementRef<HTMLDivElement>;
  @ViewChild('mermaidFileInput') private mermaidFileInput?: ElementRef<HTMLInputElement>;

  protected mermaidInput = '';
  protected uiError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isMermaidCopied = false;
  protected previewTheme: 'dark' | 'light' = 'dark';
  protected currentDiagramType: 'hld' | 'lld' | 'database' = 'hld';
  protected isDiagramDropdownOpen = false;
  private userSelectedDiagramType = false;
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
  protected showZoomControls = false;
  private mermaidRenderIndex = 0;
  private copyNotificationTimer: ReturnType<typeof setTimeout> | null = null;
  private renderDebounceTimer: ReturnType<typeof setTimeout> | null = null;
  private readonly RENDER_DEBOUNCE_MS = 1500;
  private previewAutoScale = 1;
  private readonly previewScaleMin = 0.75;
  private readonly previewScaleMax = 3;
  private readonly previewScaleStep = 0.25;
  private readonly previewReadableScaleFloor = 0.65;
  private currentMermaid = '';

  constructor() {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['mermaidSource']) {
      const newSource = changes['mermaidSource'].currentValue;
      if (newSource !== null && typeof newSource === 'string' && newSource.trim()) {
        if (!this.isNoData(newSource)) {
          this.setMermaidInput(newSource);
        } else {
          // Empty/invalid source - wait for API-generated diagram
          console.debug('[workspace] Empty mermaidSource - waiting for API diagram');
        }
      }
    }

    if (changes['visualization']) {
      this.visualizationData = this.visualization;
      if (this.visualizationData?.diagrams?.mermaid) {
        if (!this.isNoData(this.visualizationData.diagrams.mermaid)) {
          this.setMermaidInput(this.visualizationData.diagrams.mermaid);
          this.userSelectedDiagramType = false;
        } else {
          console.debug('[workspace] Empty visualization data - waiting for API diagram');
        }
      }
    }

    if (changes['mermaidEditorContent'] && typeof changes['mermaidEditorContent'].currentValue === 'string' && !this.mermaidSource) {
      const content = changes['mermaidEditorContent'].currentValue;
      if (content.trim() && !this.isNoData(content)) {
        this.setMermaidInput(content);
      } else {
        console.debug('[workspace] Empty mermaidEditorContent - waiting for API diagram');
      }
    }
  }

  ngAfterViewInit(): void {
    if (this.mermaidSource !== null && typeof this.mermaidSource === 'string' && this.mermaidSource.trim() && !this.isNoData(this.mermaidSource)) {
      this.setMermaidInput(this.mermaidSource);
    } else if (this.mermaidInput && !this.isNoData(this.mermaidInput)) {
      this.renderMermaid(this.mermaidInput);
    } else {
      // Show placeholder - diagram will be generated via API
      if (this.mermaidContainer) {
        this.mermaidContainer.nativeElement.innerHTML = `
          <div style="text-align: center; padding: 3rem; color: #60a5fa;">
            <p style="font-size: 1.2rem; margin-bottom: 1rem;">📊 Ready to generate diagrams</p>
            <p style="color: #94a3b8; font-size: 0.95rem;">Select a diagram type above to generate with AI</p>
          </div>
        `;
      }
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
    if (this.renderDebounceTimer) {
      clearTimeout(this.renderDebounceTimer);
      this.renderDebounceTimer = null;
    }
  }

  protected onExit(): void {
    this.exit.emit();
  }

  protected onMermaidInput(value: string): void {
    this.mermaidInput = value;
    this.updateLineNumbers();
    this.mermaidChange.emit(this.mermaidInput);
    this.debouncedSetMermaidInput(value);
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
        this.uiError = 'Diagram invalid — uploaded file is empty';
      } else {
        this.setMermaidInput(result);
        this.uiError = null;
      }
      if (this.mermaidFileInput?.nativeElement) {
        this.mermaidFileInput.nativeElement.value = '';
      }
    };

    reader.onerror = () => {
      this.uiError = 'Diagram invalid — unable to read file';
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
    this.renderMermaid(this.currentMermaid);
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
      console.debug(`[workspace] VALIDATION diagram type changed to ${type}`);
      this.currentDiagramType = type;
      this.isDiagramDropdownOpen = false;
      this.userSelectedDiagramType = true;
      
      this.uiError = null;
      
      if (this.mermaidContainer) {
        this.mermaidContainer.nativeElement.innerHTML = 
          `<p style="text-align: center; padding: 2rem; color: #3b82f6;">Generating ${this.getDiagramTypeLabel(type)}...</p>`;
      }
      
      this.diagramTypeChange.emit(type);
    }
  }

  protected onRegenerateDiagram(): void {
    this.uiError = null;
    
    if (this.mermaidContainer) {
      this.mermaidContainer.nativeElement.innerHTML = 
        `<p style="text-align: center; padding: 2rem; color: #3b82f6;">Regenerating ${this.getCurrentDiagramTypeLabel()}...</p>`;
    }
    
    console.debug(`[workspace] VALIDATION regenerating ${this.currentDiagramType}`);
    
    this.regenerateDiagram.emit(this.currentDiagramType);
  }

  protected loadPredefinedDiagram(type: 'hld' | 'lld' | 'database'): void {
    // This function is now deprecated - all diagrams should be generated via API
    // Trigger API-based diagram regeneration instead
    console.debug(`[workspace] loadPredefinedDiagram called for ${type} - triggering API generation instead`);
    this.onRegenerateDiagram();
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

  protected savePreviewDiagram(): void {
    const diagramTypeLabel = this.getCurrentDiagramTypeLabel().replace(/\s+/g, '_');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const filename = `${diagramTypeLabel}_${timestamp}.mermaid`;
    
    const blob = new Blob([this.mermaidInput], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.style.display = 'none';
    document.body.appendChild(anchor);
    anchor.click();
    
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
  }

  private debouncedSetMermaidInput(value: string): void {
    if (this.renderDebounceTimer) {
      clearTimeout(this.renderDebounceTimer);
    }
    
    this.uiError = null;
    
    this.renderDebounceTimer = setTimeout(() => {
      this.setMermaidInput(value);
      this.renderDebounceTimer = null;
    }, this.RENDER_DEBOUNCE_MS);
  }

  private setMermaidInput(input: string): void {
    const clean = normalizeMermaid(stripBomAndZwsp(input));
    const validation = validateWithMermaid(clean);
    
    if (!validation.ok) {
      const line = validation.line ? ` near line ${validation.line}` : '';
      this.uiError = `Diagram invalid — ${validation.message}${line}`;
      console.debug(`[workspace] VALIDATION ${validation.message}`);
      return;
    }
    
    this.currentMermaid = clean;
    this.mermaidInput = input;
    this.updateLineNumbers();
    this.uiError = null;
    this.renderMermaid(clean);
  }

  private renderMermaid(text: string): void {
    if (!this.mermaidContainer) {
      console.debug('[workspace] VALIDATION container not available');
      return;
    }

    if (!text || !text.trim()) {
      this.mermaidContainer.nativeElement.innerHTML = '<p style="text-align: center; color: #94a3b8;">Enter Mermaid code to render diagram.</p>';
      this.uiError = null;
      return;
    }

    initializeMermaidOnce();

    const renderId = `diagram-${this.mermaidRenderIndex++}`;

    mermaid.render(renderId, text)
      .then(({ svg }) => {
        if (!this.mermaidContainer) return;
        
      const wrapper = document.createElement('div');
      wrapper.className = 'mermaid-svg-wrapper';
      wrapper.innerHTML = svg;
      this.mermaidContainer.nativeElement.innerHTML = '';
      this.mermaidContainer.nativeElement.appendChild(wrapper);
      
        this.uiError = null;
        
      this.previewFitToContainer = true;
      const timeout = this.currentDiagramType === 'lld' ? 300 : 100;
      setTimeout(() => {
        this.applyPreviewScale();
      }, timeout);
      
        console.debug('[workspace] VALIDATION render success');
      })
      .catch((error: any) => {
        console.error('[workspace] VALIDATION render failed:', error?.message);
        this.uiError = `Diagram invalid — ${error?.message || 'render error'}. Please regenerate.`;
        
        // Show helpful message to user
        if (this.mermaidContainer) {
          this.mermaidContainer.nativeElement.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #f87171;">
              <p style="font-size: 1.1rem; margin-bottom: 1rem;">⚠️ Diagram rendering failed</p>
              <p style="color: #94a3b8; margin-bottom: 1.5rem;">${error?.message || 'Unknown error'}</p>
              <p style="color: #60a5fa; font-size: 0.9rem;">Click "Regenerate Diagram" to try again with AI</p>
            </div>
          `;
        }
      });
  }

  private isNoData(content: string): boolean {
    if (!content) return false;
    const normalized = content.replace(/\s/g, '').toLowerCase();
    return normalized.includes('graphtd') && normalized.includes('a[nodata]');
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
      const scaleWidth = availableWidth / naturalWidth;
      const scaleHeight = availableHeight / naturalHeight;
      
      // Compute base fit scale
      const maxScaleForLLD = this.currentDiagramType === 'lld' ? 2.0 : 1.5;
      const baseFitScale = Math.min(scaleWidth, scaleHeight, maxScaleForLLD);
      
      // Apply boost factor for LLD to make class cards readable (~150% zoom effect)
      const boostFactor = this.currentDiagramType === 'lld' ? 1.4 : 1.0;
      const boostedScale = baseFitScale * boostFactor;
      
      // Clamp the final scale between 0.8 and 2.0
      const finalScale = Math.max(0.8, Math.min(2.0, boostedScale));
      
      const displayWidth = naturalWidth * finalScale;
      const displayHeight = naturalHeight * finalScale;
      
      // For LLD, allow overflow so user can scroll/pan; for others, constrain to container
      const allowOverflow = this.currentDiagramType === 'lld';
      
      svgWrapper.style.width = `${displayWidth}px`;
      svgWrapper.style.maxWidth = allowOverflow ? 'none' : '100%';
      svgWrapper.style.height = `${displayHeight}px`;
      svgWrapper.style.maxHeight = allowOverflow ? 'none' : '100%';
      
      svg.style.width = `${displayWidth}px`;
      svg.style.height = `${displayHeight}px`;
      svg.style.maxWidth = allowOverflow ? 'none' : '100%';
      svg.style.maxHeight = allowOverflow ? 'none' : '100%';
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

    const baseScale = this.previewFitToContainer ? 1 : 1;
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

  protected shouldShowNoDiagramMessage(): boolean {
    if (this.mermaidSaving) {
      return false;
    }
    
    if (!this.mermaidInput || !this.mermaidInput.trim()) {
      return true;
    }
    
    return this.isNoData(this.mermaidInput);
  }

  onStoryRegenerated(regeneratedContent: any, storyIndex: number): void {
    console.debug('[workspace] VALIDATION story regenerated', { storyIndex });
    if (this.stories[storyIndex]) {
      this.stories[storyIndex] = {
        ...this.stories[storyIndex],
        ...regeneratedContent,
      };
      this.contentRegenerated.emit({
        type: 'story',
        itemId: `story-${storyIndex}`,
        content: regeneratedContent,
      });
    }
  }

  onVisualizationRegenerated(regeneratedContent: any): void {
    console.debug('[workspace] VALIDATION visualization regenerated');
    
    if (regeneratedContent?.mermaid || regeneratedContent?.diagrams?.mermaid) {
      const newMermaid = regeneratedContent.mermaid || regeneratedContent.diagrams?.mermaid || '';
      
      this.setMermaidInput(newMermaid);
      this.contentRegenerated.emit({
        type: 'visualization',
        itemId: `visualization-${this.currentDiagramType}`,
        content: regeneratedContent,
      });
    }
  }

  onFeedbackError(error: string): void {
    console.debug('[workspace] VALIDATION feedback error', { error });
    this.uiError = error;
  }
}
