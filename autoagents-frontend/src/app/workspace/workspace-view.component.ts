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
  @Input() mermaidSaving = false;
  @Input() mermaidUpdatedAt: string | null = null;
  @Input() mermaidSaveMessage: string | null = null;
  @Output() mermaidChange = new EventEmitter<string>();
  @Output() mermaidSave = new EventEmitter<string>();
  @Output() exit = new EventEmitter<void>();
  @ViewChild('mermaidContainer') private mermaidContainer?: ElementRef<HTMLDivElement>;

  protected mermaidInput = '';
  protected mermaidError: string | null = null;
  protected visualizationData: AgentVisualizationResponse | null = null;
  protected isDotCopied = false;
  protected isMermaidCopied = false;
  protected previewTheme: 'dark' | 'light' = 'dark';

  private mermaidInitialised = false;
  private mermaidRenderIndex = 0;
  private copyNotificationTimer: ReturnType<typeof setTimeout> | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['stories'] && !this.mermaidEditorContent) {
      this.generateDefaultMermaid();
    }

    if (changes['visualization']) {
      this.visualizationData = this.visualization;
      if (this.visualizationData?.diagrams?.mermaid) {
        this.setMermaidInput(this.visualizationData.diagrams.mermaid, false);
      }
    }

    if (changes['mermaidEditorContent'] && typeof changes['mermaidEditorContent'].currentValue === 'string') {
      this.setMermaidInput(changes['mermaidEditorContent'].currentValue, false);
    }
  }

  ngAfterViewInit(): void {
    this.renderMermaid();
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

  protected onMermaidSave(): void {
    this.mermaidSave.emit(this.mermaidInput);
  }

  protected onMermaidReset(): void {
    const fallback = this.mermaidEditorContent?.trim().length ? this.mermaidEditorContent : this.mermaidInput;
    this.setMermaidInput(fallback, true);
    this.mermaidError = null;
    this.isMermaidCopied = false;
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

  protected storiesForFeature(featureTitle: string): AgentStorySpec[] {
    return this.stories.filter((story) => story.featureTitle === featureTitle);
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
    this.mermaidInput = value;
    if (emitEvent) {
      this.mermaidChange.emit(this.mermaidInput);
    }
    this.mermaidError = null;
    void this.renderMermaid();
  }

  private async renderMermaid(): Promise<void> {
    if (!this.mermaidContainer) {
      return;
    }

    mermaid.initialize({ startOnLoad: false, theme: this.previewTheme });
    this.mermaidInitialised = true;

    const definition = this.mermaidInput.trim();
    if (!definition) {
      this.mermaidContainer.nativeElement.innerHTML = '<p class="mermaid-placeholder">Enter Mermaid code to render a diagram.</p>';
      this.mermaidError = null;
      return;
    }

    const renderId = `mermaid-diagram-${this.mermaidRenderIndex++}`;

    try {
      const { svg } = await mermaid.render(renderId, definition);
      this.mermaidContainer.nativeElement.innerHTML = svg;
      this.mermaidError = null;
    } catch (error) {
      this.mermaidError = 'Mermaid syntax error. Please review the diagram definition.';
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
}

