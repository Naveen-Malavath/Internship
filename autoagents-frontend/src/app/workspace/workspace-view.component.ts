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
  protected mermaidError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isDotCopied = false;
  protected isMermaidCopied = false;
  protected previewTheme: 'dark' | 'light' = 'dark';
  protected currentDiagramType: 'hld' | 'lld' | 'database' = 'hld';
  protected isDiagramDropdownOpen = false;
  private userSelectedDiagramType = false; // Flag to prevent overwriting when user explicitly selects type
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
      if (newSource !== null && typeof newSource === 'string' && newSource.trim()) {
        if (!this.isNoData(newSource)) {
          this.setMermaidInput(newSource, false);
        } else {
          // If it's "No data", load default HLD
          this.currentDiagramType = 'hld';
          this.loadPredefinedDiagram('hld');
        }
      } else if ((newSource === null || newSource === '') && this.mermaidInput) {
        // Clear editor if source becomes null or empty, then load default
        this.currentDiagramType = 'hld';
        this.loadPredefinedDiagram('hld');
      }
    }

    if ((changes['stories'] || changes['features']) && this.currentDiagramType === 'lld') {
      this.loadPredefinedDiagram('lld');
    }

    if (changes['stories'] && !this.mermaidEditorContent && !this.mermaidSource && !this.mermaidInput) {
      this.loadPredefinedDiagram('hld');
    }

    if (changes['visualization']) {
      this.visualizationData = this.visualization;
      // Only update if user hasn't explicitly selected a diagram type
      if (this.visualizationData?.diagrams?.mermaid && !this.mermaidSource && !this.userSelectedDiagramType) {
        if (!this.isNoData(this.visualizationData.diagrams.mermaid)) {
          this.setMermaidInput(this.visualizationData.diagrams.mermaid, false);
          this.userSelectedDiagramType = false; // Reset flag after accepting Agent3 response
        } else {
          // If it's "No data", load default HLD
          this.currentDiagramType = 'hld';
          this.loadPredefinedDiagram('hld');
        }
      } else if (this.userSelectedDiagramType && this.visualizationData?.diagrams?.mermaid) {
        // User selected a type, so accept the Agent3 response for that type
        if (!this.isNoData(this.visualizationData.diagrams.mermaid)) {
          this.setMermaidInput(this.visualizationData.diagrams.mermaid, false);
          this.userSelectedDiagramType = false; // Reset flag after accepting Agent3 response
        }
      }
    }

    if (changes['mermaidEditorContent'] && typeof changes['mermaidEditorContent'].currentValue === 'string' && !this.mermaidSource) {
      const content = changes['mermaidEditorContent'].currentValue;
      if (content.trim() && !this.isNoData(content)) {
        this.setMermaidInput(content, false);
      } else if (!content.trim() || this.isNoData(content)) {
        // If empty or "No data", load default HLD
        this.currentDiagramType = 'hld';
        this.loadPredefinedDiagram('hld');
      }
    }
  }

  ngAfterViewInit(): void {
    // If mermaidSource is provided initially, use it
    if (this.mermaidSource !== null && typeof this.mermaidSource === 'string' && this.mermaidSource.trim() && !this.isNoData(this.mermaidSource)) {
      this.setMermaidInput(this.mermaidSource, false);
    } else if (this.mermaidInput && !this.isNoData(this.mermaidInput)) {
      // We have valid content in mermaidInput, render it
      this.renderMermaid();
    } else {
      // No valid content, load default HLD diagram
      this.currentDiagramType = 'hld';
      this.loadPredefinedDiagram('hld');
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
      this.userSelectedDiagramType = true; // Mark that user explicitly selected this type
      
      // Don't load static template - let Agent3 generate dynamically
      // Emit event to parent to trigger Agent3 diagram generation
      this.diagramTypeChange.emit(type);
      
      // Show loading state while waiting for Agent3
      this.mermaidError = null;
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
        // Pass features, stories, and prompt for dynamic HLD generation
        diagramContent = DiagramDataService.getHLDDiagram(this.features, this.stories, this.prompt);
        break;
      case 'lld':
        // Pass actual features and stories for dynamic LLD generation
        diagramContent = DiagramDataService.getLLDDiagram(this.features, this.stories, this.prompt);
        break;
      case 'database':
        // Pass features and stories for dynamic DBD generation
        diagramContent = DiagramDataService.getDBDDiagram(this.features, this.stories);
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

  protected savePreviewDiagram(): void {
    // Get the current diagram type label for filename
    const diagramTypeLabel = this.getCurrentDiagramTypeLabel().replace(/\s+/g, '_');
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').split('T')[0];
    const filename = `${diagramTypeLabel}_${timestamp}.mermaid`;
    
    // Create a blob with the mermaid content
    const blob = new Blob([this.mermaidInput], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    // Create a temporary anchor element and trigger download
    const anchor = document.createElement('a');
    anchor.href = url;
    anchor.download = filename;
    anchor.style.display = 'none';
    document.body.appendChild(anchor);
    anchor.click();
    
    // Cleanup
    document.body.removeChild(anchor);
    URL.revokeObjectURL(url);
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

  private sanitizeMermaidDefinition(value: string): string {
    if (!value) {
      return '';
    }

    let normalised = value.replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
    
    // Fix common truncated CSS properties before other processing
    normalised = normalised
      .replace(/stroke-widt(?!h)/gi, 'stroke-width')
      .replace(/stroke-wid(?!th)/gi, 'stroke-width')
      .replace(/stroke-w(?!idth)/gi, 'stroke-width')
      .replace(/font-weigh(?!t)/gi, 'font-weight')
      .replace(/font-siz(?!e)/gi, 'font-size')
      .replace(/font-famil(?!y)/gi, 'font-family')
      .replace(/border-radi(?!us)/gi, 'border-radius')
      .replace(/stroke-das(?!harray)/gi, 'stroke-dasharray');

    // Fix erDiagram formatting issues
    // 1. Ensure newline between closing } and next entity
    normalised = normalised.replace(/}\s+([A-Z_][A-Z_0-9]*)\s*\{/g, '}\n\n    $1 {\n');
    
    // 2. Fix entity attributes with quotes and emojis - remove descriptions in quotes
    // This handles patterns like: varchar status "✅ Status"
    normalised = normalised.replace(/(\w+\s+\w+\s+[A-Z]{2,})\s+"[^"]*"/g, '$1');
    
    // 3. Fix relationship labels with quotes - replace with underscores
    normalised = normalised.replace(/:\s+"([^"]+)"/g, (match, label) => {
      return ': ' + label.replace(/[^a-zA-Z0-9_]/g, '_');
    });
    
    // Fix node labels: ensure proper spacing after "]" before next node
    normalised = normalised.replace(/"\]\s+([A-Z_a-z0-9]+)\[/g, '"]\n    $1[');
    
    // Remove lines that are just node IDs followed by opening bracket without proper syntax
    // Pattern: SomeID[ without closing or content on same line after a closing quote
    normalised = normalised.replace(/"\]\s*\n\s*([A-Z_a-z0-9]+)\[\s*$/gm, '"]');

    // Enhanced node label quoting with better escape handling
    const withQuotedNodes = normalised.replace(/\[(?!["!])([^\]\n]+?)\]/g, (match, label: string) => {
      // Skip if already quoted
      if (label.startsWith('"') && label.endsWith('"')) {
        return match;
      }
      // Properly escape quotes and special characters, remove <br/> tags
      const escapedLabel = label
        .replace(/<br\s*\/?>/gi, ' ') // Remove <br/> tags, replace with space
        .replace(/\\/g, '\\\\')
        .replace(/"/g, '\\"')
        .replace(/\n/g, ' ')
        .replace(/\s+/g, ' ') // Normalize multiple spaces
        .trim();
      return `["${escapedLabel}"]`;
    });

    const withQuotedParticipants = withQuotedNodes.replace(
      /(participant\s+[^\s]+\s+as\s+)([^"\n][^\n]*)/g,
      (match, prefix: string, label: string) => {
        const trimmedLabel = label.trim();
        // Skip if already quoted
        if (trimmedLabel.startsWith('"') && trimmedLabel.endsWith('"')) {
          return match;
        }
        const escaped = trimmedLabel
          .replace(/<br\s*\/?>/gi, ' ')
          .replace(/\\/g, '\\\\')
          .replace(/"/g, '\\"');
        return `${prefix}"${escaped}"`;
      },
    );

    // Remove incomplete or malformed classDef and style statements
    const lines = withQuotedParticipants.split('\n');
    
    // Detect diagram type from first line OR from current diagram type setting
    const firstLine = lines[0]?.trim().toLowerCase() || '';
    const isErDiagram = firstLine.includes('erdiagram') || firstLine.includes('entityrelationshipdiagram') || this.currentDiagramType === 'database';
    const isClassDiagram = firstLine.includes('classdiagram');
    const isFlowchart = firstLine.includes('graph') || firstLine.includes('flowchart');
    
    const cleanedLines = lines.filter((line, index) => {
      let trimmed = line.trim();
      
      // Skip empty lines and comments
      if (!trimmed || trimmed.startsWith('%%')) {
        return true;
      }
      
      // Fix malformed node labels with escaped quotes and extra characters
      // Pattern: Node[("Label\")"]        Text - escaped quotes followed by closing brackets
      // Pattern: Node[("Database PostgreSQL\")"]        Knowledg - text after closing bracket
      // Pattern: Node[("Label\")]"]        Text - double bracket with escaped quote
      if (trimmed.includes('\\")"]') || (trimmed.includes('\\")') && trimmed.includes('"]'))) {
        // Fix escaped quotes - handle double bracket pattern first: \")]\" -> ")]
        let fixedLine = trimmed.replace(/\\"\)"\]\\"/g, '")]')
                                  .replace(/\\"\)"\]/g, '")]')  // Fix single pattern
                                  .replace(/\\"/g, '"');  // Fix remaining escaped quotes
        
        // Remove text after closing bracket that's not a connection
        // Pattern: ...")]        Text (with spaces after closing bracket)
        // Match: closing bracket ] followed by whitespace and text (not a connection arrow)
        const trailingTextMatch = fixedLine.match(/"\]\s{2,}([A-Za-z][^\s]*)/);
        if (trailingTextMatch) {
          // Check if it's not a connection arrow
          const afterMatch = fixedLine.substring(trailingTextMatch.index! + trailingTextMatch[0].length);
          if (!afterMatch.match(/^\s*(--?>|==?>|--|-\.->)/)) {
            // Remove text after closing bracket - it's malformed
            fixedLine = fixedLine.substring(0, trailingTextMatch.index! + 2); // Keep the '"]'
            console.warn(`[workspace-view] Fixed escaped quotes and removed trailing text at line ${index + 1}: ${trailingTextMatch[1]}`);
          }
        }
        
        // Update the line in the array and continue with fixed version
        lines[index] = fixedLine;
        trimmed = fixedLine.trim();
      }
      
      // For erDiagram: check for malformed entity definitions (but don't remove valid syntax!)
      if (isErDiagram && index > 0) {
        // Check for entity attributes with quoted descriptions containing emojis or special chars
        // These should be simple: datatype field_name [PK|FK|UK]
        if (/^\s*\w+\s+\w+\s+[A-Z]{2,}\s+"/.test(trimmed)) {
          console.warn(`Mermaid sanitization: Removing erDiagram attribute with quoted description at ${index + 1}:`, trimmed.substring(0, 80));
          return false;
        }
      }
      
      // For classDiagram: check for malformed member definitions
      // Fix invalid class syntax in flowcharts (classDiagram syntax shouldn't appear in flowcharts)
      // Pattern: "class X {        +method" - this is invalid in flowcharts and causes DIAMOND_START parse error
      const classWithMethodMatch = trimmed.match(/^\s*class\s+(\w+)\s*\{\s+([+\-#~].*)/);
      if (classWithMethodMatch) {
        if (isFlowchart) {
          // In flowcharts, class syntax with methods is invalid - remove it
          console.warn(`[workspace-view] Removing invalid class syntax from flowchart at line ${index + 1}:`, trimmed.substring(0, 80));
          return false;
        }
        // In classDiagram, backend will handle splitting it properly
      }
      
      if (isClassDiagram && index > 0) {
        // Check for class members appearing right after diagram declaration (without class definition)
        const prevLine = index > 0 ? lines[index - 1].trim() : '';
        if (prevLine.toLowerCase().includes('classdiagram') && /^\s*[+\-#~]/.test(trimmed)) {
          console.warn(`Mermaid sanitization: Removing class member without class context at ${index + 1}:`, trimmed.substring(0, 80));
          return false;
        }
      }
      
      // Check for style definitions (classDef or style commands)
      if (trimmed.toLowerCase().includes('classdef') || trimmed.toLowerCase().startsWith('style ')) {
        // Valid endings for complete style definitions
        const validEndings = ['px', 'bold', 'italic', 'normal', 'lighter', 'bolder', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
        
        // Check for complete hex colors at the end (3 or 6 hex digits)
        const hexColorEnding = /[#][0-9a-fA-F]{3}$|[#][0-9a-fA-F]{6}$/;
        
        // Check if line ends properly
        const endsWithValid = validEndings.some(ending => trimmed.endsWith(ending)) || 
                             hexColorEnding.test(trimmed);
        
        // Check for incomplete hex colors (# followed by 1-2 or 4-5 characters, or invalid chars)
        const hasIncompleteHexColor = (
          /#[0-9a-fA-F]{1,2}(?:[,\s]|$)/i.test(trimmed) && !/#[0-9a-fA-F]{3}(?:[,\s:]|$)|#[0-9a-fA-F]{6}(?:[,\s:]|$)/i.test(trimmed)
        ) || /#[0-9a-fA-F]{4,5}(?:[,\s]|$)/i.test(trimmed);
        
        // Check for any remaining truncated properties (should be rare after our fix above)
        const hasTruncatedProps = /stroke-widt(?!h)|font-weigh(?!t)|font-siz(?!e)|font-famil(?!y)|border-radi(?!us)/i.test(trimmed);
        
        // Check for incomplete property values (property: with nothing or only # after it)
        const hasIncompleteValue = /:\s*$|:\s*#\s*$/.test(trimmed);
        
        // Check for trailing comma or colon (incomplete)
        const hasTrailingComma = trimmed.endsWith(',');
        const hasTrailingColon = trimmed.endsWith(':');
        
        // Check for properties with suspiciously short or invalid values
        let hasInvalidPropertyValue = false;
        if (trimmed.includes(':')) {
          const properties = trimmed.split(',').map(p => p.trim());
          for (const prop of properties) {
            if (prop.includes(':')) {
              const parts = prop.split(':', 2);
              if (parts.length === 2) {
                const propValue = parts[1].trim();
                // Value is too short, ends with dash, or is empty
                if (!propValue || propValue.length < 2 || propValue.endsWith('-')) {
                  hasInvalidPropertyValue = true;
                  break;
                }
              }
            }
          }
        }
        
        // Check for style lines that have properties but don't end correctly
        const hasProperties = /fill:|stroke:|color:|font-weight:|stroke-width:/i.test(trimmed);
        
        if (hasTruncatedProps || hasTrailingComma || hasTrailingColon || hasIncompleteValue || hasIncompleteHexColor || hasInvalidPropertyValue) {
          console.warn(`Mermaid sanitization: Removing incomplete style definition at line ${index + 1}:`, trimmed.substring(0, 80));
          return false; // Filter out this line
        }
        
        // If it has style properties but doesn't end with a valid value, remove it
        if (hasProperties && !endsWithValid) {
          console.warn(`Mermaid sanitization: Removing malformed style definition at line ${index + 1}:`, trimmed.substring(0, 80));
          return false;
        }
      }
      
      // Check for malformed node definitions with unclosed quotes or brackets
      // IMPORTANT: Skip brace checking for erDiagram syntax which uses { in relationships and entity definitions
      if (trimmed.includes('[') || trimmed.includes('(') || trimmed.includes('{')) {
        const openBrackets = (trimmed.match(/\[/g) || []).length;
        const closeBrackets = (trimmed.match(/\]/g) || []).length;
        const openParens = (trimmed.match(/\(/g) || []).length;
        const closeParens = (trimmed.match(/\)/g) || []).length;
        const openBraces = (trimmed.match(/\{/g) || []).length;
        const closeBraces = (trimmed.match(/\}/g) || []).length;
        
        // For erDiagram, { and } are part of the syntax (relationships and entity definitions)
        // Skip brace checking for erDiagram lines
        const isErDiagramRelationship = /\|\|--|\}o--|\}o\.\.|o\{--/.test(trimmed); // ERD relationship syntax
        const isErDiagramEntityDef = isErDiagram && /^[A-Z_][A-Z_0-9]*\s*\{\s*$/.test(trimmed); // Entity definition
        
        // Check for mismatched brackets/parens/braces, but skip brace check for erDiagram
        const bracketsMismatch = openBrackets !== closeBrackets;
        const parensMismatch = openParens !== closeParens;
        const bracesMismatch = !isErDiagram && (openBraces !== closeBraces); // Only check braces for non-erDiagram
        
        if (bracketsMismatch || parensMismatch || bracesMismatch) {
          // Don't count subgraph lines or erDiagram syntax as errors
          if (!trimmed.toLowerCase().startsWith('subgraph') && !isErDiagramRelationship && !isErDiagramEntityDef) {
            console.warn(`Mermaid sanitization: Removing line with mismatched brackets at line ${index + 1}:`, trimmed.substring(0, 80));
            return false;
          }
        }
        
        // Check for lines with node labels followed immediately by another node (no arrow)
        // Pattern: ..."]  NodeName[ should be invalid (but not for erDiagram)
        if (!isErDiagram && /"\]\s+[A-Z_a-z0-9]+\s*\[/.test(trimmed) && !/(-->|---|-\.|==>|===)/.test(trimmed)) {
          console.warn(`Mermaid sanitization: Removing line with adjacent nodes without arrow at line ${index + 1}:`, trimmed.substring(0, 80));
          return false;
        }
      }
      
      // Additional check: Lines that are just fragments or incomplete
      // Example: lines ending with just "]  SomeText" without proper node definition
      if (/"\]\s+[A-Z_a-z]+\s*$/.test(trimmed) && !trimmed.includes('-->') && !trimmed.includes('---')) {
        console.warn(`Mermaid sanitization: Removing incomplete node definition at line ${index + 1}:`, trimmed.substring(0, 80));
        return false;
      }
      
      return true; // Keep this line
    });

    return cleanedLines.join('\n');
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

  protected shouldShowNoDiagramMessage(): boolean {
    // Show "No diagram" message when:
    // 1. There's no mermaid input content, or it's a "no data" placeholder
    // 2. We're not currently saving/loading a diagram
    if (this.mermaidSaving) {
      return false; // Don't show "no diagram" while loading
    }
    
    if (!this.mermaidInput || !this.mermaidInput.trim()) {
      return true;
    }
    
    return this.isNoData(this.mermaidInput);
  }

  onStoryRegenerated(regeneratedContent: any, storyIndex: number): void {
    console.debug('[WorkspaceView] Story regenerated', { storyIndex, regeneratedContent });
    if (this.stories[storyIndex]) {
      // Update the story with regenerated content
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
    console.debug('[WorkspaceView] Visualization regenerated', { regeneratedContent });
    if (regeneratedContent?.mermaid || regeneratedContent?.diagrams?.mermaid) {
      const newMermaid = regeneratedContent.mermaid || regeneratedContent.diagrams?.mermaid || '';
      this.setMermaidInput(newMermaid, true);
      this.contentRegenerated.emit({
        type: 'visualization',
        itemId: `visualization-${this.currentDiagramType}`,
        content: regeneratedContent,
      });
    }
  }

  onFeedbackError(error: string): void {
    console.error('[WorkspaceView] Feedback error', { error });
    this.mermaidError = error;
    // Error will be displayed by the FeedbackChatbot component
  }
}

