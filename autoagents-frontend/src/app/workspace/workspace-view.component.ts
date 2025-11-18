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
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import mermaid from 'mermaid';

import { AgentFeatureSpec, AgentStorySpec, AgentVisualizationResponse, ProjectWizardSubmission } from '../types';

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
  @Output() exit = new EventEmitter<void>();
  @Output() featureEdit = new EventEmitter<AgentFeatureSpec>();
  @Output() featureDismiss = new EventEmitter<AgentFeatureSpec>();
  @Output() storyEdit = new EventEmitter<{ feature: AgentFeatureSpec; story: AgentStorySpec }>();
  @Output() storyDismiss = new EventEmitter<{ feature: AgentFeatureSpec; story: AgentStorySpec }>();
  @Output() createProject = new EventEmitter<void>();
  @ViewChild('mermaidContainer') private mermaidContainer?: ElementRef<HTMLDivElement>;
  @ViewChild('mermaidFileInput') private mermaidFileInput?: ElementRef<HTMLInputElement>;

  protected mermaidInput = '';
  protected mermaidError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isDotCopied = false;
  protected isMermaidCopied = false;
  protected previewTheme: 'dark' | 'light' = 'dark';
  protected mermaidLineNumbers: number[] = [1];
  protected lineNumberOffset = 0;

  private mermaidInitialised = false;
  private mermaidRenderIndex = 0;
  private copyNotificationTimer: ReturnType<typeof setTimeout> | null = null;

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

    if (changes['stories'] && !this.mermaidEditorContent && !this.mermaidSource) {
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
    } else {
      this.renderMermaid();
    }
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

  protected onFeatureEdit(feature: AgentFeatureSpec): void {
    this.featureEdit.emit(feature);
  }

  protected onFeatureDismiss(feature: AgentFeatureSpec): void {
    this.featureDismiss.emit(feature);
  }

  protected onCreateProject(): void {
    this.createProject.emit();
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
    if (this.prompt) {
      lines.push(`${promptNode}["${this.escapeHtml(this.prompt)}"]`);
    } else {
      lines.push(`${promptNode}["Customer Request"]`);
    }

    this.features.forEach((feature, index) => {
      const featureId = this.escapeMermaidId(`feature_${index}`);
      lines.push(`${promptNode} --> ${featureId}["${this.escapeHtml(feature.title)}"]`);
      this.stories
        .filter((story) => story.featureTitle === feature.title)
        .forEach((story, storyIndex) => {
          const storyId = this.escapeMermaidId(`story_${index}_${storyIndex}`);
          lines.push(`${featureId} --> ${storyId}["${this.escapeHtml(story.userStory)}"]`);
        });
    });

    if (lines.length === 1) {
      lines.push('A[No data]');
    }

    this.setMermaidInput(lines.join('\n'), true);
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

    mermaid.initialize({ startOnLoad: false, theme: this.previewTheme });
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
      this.mermaidContainer.nativeElement.innerHTML = svg;
      this.mermaidError = null;
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Mermaid syntax error. Please review the diagram definition.';
      this.mermaidError = message;
      this.mermaidContainer.nativeElement.innerHTML = '';
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

}

