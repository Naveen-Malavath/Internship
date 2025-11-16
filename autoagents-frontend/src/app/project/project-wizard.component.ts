import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';

import {
  AgentFeatureDetail,
  AgentStorySpec,
  FeatureFormSubmission,
  ProjectTemplate,
  ProjectWorkflowPreset,
  ProjectWizardAISummary,
  ProjectWizardDetails,
  ProjectWizardSubmissionPayload,
} from '../types';
import {
  PROJECT_AI_SUGGESTIONS,
  PROJECT_TEMPLATES,
  PROJECT_TEAM_SIZES,
  PROJECT_TIMEZONES,
  PROJECT_WORKFLOWS,
  generateProjectKey,
} from './project-wizard.data';
import { FeatureFormComponent } from '../features/feature-form.component';

type WizardStory = {
  id: string;
  spec: AgentStorySpec;
  approved: boolean;
};

type WizardFeature = {
  id: string;
  detail: AgentFeatureDetail;
  approved: boolean;
  source: 'recommended' | 'manual';
  stories: WizardStory[];
};

@Component({
  selector: 'project-wizard',
  standalone: true,
  imports: [CommonModule, FormsModule, FeatureFormComponent],
  templateUrl: './project-wizard.component.html',
  styleUrl: './project-wizard.component.scss',
})
export class ProjectWizardComponent {
  @Input() open = false;
  @Input() templates: ProjectTemplate[] = PROJECT_TEMPLATES;
  @Input() workflows: ProjectWorkflowPreset[] = PROJECT_WORKFLOWS;
  @Input() timezones: string[] = PROJECT_TIMEZONES;
  @Input() teamSizes: number[] = PROJECT_TEAM_SIZES;
  @Input() saving = false;
  @Input() aiSummaryLoading = false;
  @Input() featureRecommendationsLoading = false;
  @Input() storyRecommendationsLoading = false;
  @Input() set aiSummaryDraft(value: ProjectWizardAISummary | null) {
    if (!value) {
      return;
    }
    this.aiSummary = {
      executiveSummary: value.executiveSummary,
      epicIdeas: [...value.epicIdeas],
      riskNotes: [...value.riskNotes],
      customPrompt: value.customPrompt ?? this.aiSummary.customPrompt ?? '',
    };
  }
  @Input() set featureRecommendations(value: AgentFeatureDetail[] | null) {
    if (!value?.length) {
      return;
    }
    this.applyFeatureRecommendations(value);
  }
  @Input() set storyRecommendations(value: AgentStorySpec[] | null) {
    if (!value) {
      return;
    }
    this.applyStoryRecommendations(value);
  }

  @Output() cancel = new EventEmitter<void>();
  @Output() complete = new EventEmitter<ProjectWizardSubmissionPayload>();
  @Output() requestAISummary = new EventEmitter<ProjectWizardDetails>();
  @Output() requestFeatureRecommendations = new EventEmitter<{
    details: ProjectWizardDetails;
    aiSummary: ProjectWizardAISummary;
  }>();
  @Output() requestStoryRecommendations = new EventEmitter<{
    details: ProjectWizardDetails;
    aiSummary: ProjectWizardAISummary;
    features: AgentFeatureDetail[];
  }>();
  @Output() editStory = new EventEmitter<{
    featureIndex: number;
    storyIndex: number;
    story: AgentStorySpec;
    featureDetail: AgentFeatureDetail;
  }>();
  @Output() dismissStory = new EventEmitter<{ featureIndex: number; storyIndex: number }>();

  protected readonly steps = ['Template', 'Project Details', 'AI Assist', 'Features', 'Stories', 'Review'];
  protected stepIndex = 0;

  protected selectedTemplateId: string | null = null;
  protected selectedWorkflowId: string | null = null;

  protected details: ProjectWizardDetails = {
    name: '',
    key: '',
    description: '',
    industry: 'General',
    methodology: 'scrum',
    timezone: 'UTC',
    startDate: null,
    targetLaunch: null,
    teamSize: null,
  };

  protected aiSummary: ProjectWizardAISummary = {
    executiveSummary: '',
    epicIdeas: [],
    riskNotes: [],
    customPrompt: '',
  };

  protected readonly aiPrompts = PROJECT_AI_SUGGESTIONS;
  protected projectFiles: File[] = [];
  protected wizardFeatures: WizardFeature[] = [];
  protected isFeatureFormOpen = false;
  protected featureEditingIndex: number | null = null;
  protected featurePreset: AgentFeatureDetail | null = null;
  protected featureFormSaving = false;

  private hasRequestedFeatureRecommendations = false;
  private hasRequestedStoryRecommendations = false;

  protected get selectedTemplate(): ProjectTemplate | undefined {
    return this.templates.find((template) => template.id === this.selectedTemplateId);
  }

  protected get selectedWorkflow(): ProjectWorkflowPreset | undefined {
    const workflowId = this.selectedWorkflowId ?? this.selectedTemplate?.defaultWorkflow;
    return this.workflows.find((workflow) => workflow.id === workflowId);
  }

  protected onSelectTemplate(template: ProjectTemplate): void {
    this.selectedTemplateId = template.id;
    this.selectedWorkflowId = template.defaultWorkflow;
    this.details = {
      ...this.details,
      industry: template.industry,
      methodology: template.methodology,
      description: template.summary,
      name: this.details.name || template.name,
      key: this.details.key || generateProjectKey(template.name),
    };
    this.seedAISummary(template);
    this.stepIndex = Math.max(this.stepIndex, 1);
  }

  protected onSelectWorkflow(workflow: ProjectWorkflowPreset): void {
    this.selectedWorkflowId = workflow.id;
  }

  protected onNameBlur(): void {
    if (!this.details.key.trim() && this.details.name.trim()) {
      this.details.key = generateProjectKey(this.details.name);
    }
  }

  protected onAddEpicIdea(): void {
    this.aiSummary.epicIdeas = [...this.aiSummary.epicIdeas, ''];
  }

  protected onRemoveEpicIdea(index: number): void {
    this.aiSummary.epicIdeas = this.aiSummary.epicIdeas.filter((_, idx) => idx !== index);
  }

  protected onEpicIdeaChange(index: number, value: string): void {
    this.aiSummary.epicIdeas = this.aiSummary.epicIdeas.map((idea, idx) =>
      idx === index ? value : idea,
    );
  }

  protected onAddRiskNote(): void {
    this.aiSummary.riskNotes = [...this.aiSummary.riskNotes, ''];
  }

  protected onRemoveRiskNote(index: number): void {
    this.aiSummary.riskNotes = this.aiSummary.riskNotes.filter((_, idx) => idx !== index);
  }

  protected onRiskNoteChange(index: number, value: string): void {
    this.aiSummary.riskNotes = this.aiSummary.riskNotes.map((note, idx) =>
      idx === index ? value : note,
    );
  }

  protected onProjectFilesSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (!input.files?.length) {
      return;
    }
    const files = Array.from(input.files);
    this.projectFiles = [...this.projectFiles, ...files];
    input.value = '';
  }

  protected removeProjectFile(index: number): void {
    this.projectFiles = this.projectFiles.filter((_, idx) => idx !== index);
  }

  protected onAddFeature(): void {
    this.featureEditingIndex = null;
    this.featurePreset = null;
    this.isFeatureFormOpen = true;
    this.featureFormSaving = false;
  }

  protected onEditFeature(index: number): void {
    const existing = this.wizardFeatures[index];
    if (!existing) {
      return;
    }
    this.featureEditingIndex = index;
    this.featurePreset = existing.detail;
    this.isFeatureFormOpen = true;
  }

  protected onRemoveFeature(index: number): void {
    this.wizardFeatures = this.wizardFeatures.filter((_, idx) => idx !== index);
    this.invalidateStoryRecommendations(true);
  }

  protected onToggleFeatureApproval(index: number, approved: boolean): void {
    const feature = this.wizardFeatures[index];
    if (!feature) {
      return;
    }
    this.wizardFeatures[index] = { ...feature, approved, stories: approved ? feature.stories : [] };
    this.invalidateStoryRecommendations(false);
  }

  protected onFeatureFormCancel(): void {
    this.isFeatureFormOpen = false;
    this.featureEditingIndex = null;
    this.featurePreset = null;
    this.featureFormSaving = false;
  }

  protected onFeatureFormSubmit(submission: FeatureFormSubmission): void {
    if (this.featureFormSaving) {
      return;
    }
    this.featureFormSaving = true;
    const baseId =
      this.featureEditingIndex !== null
        ? this.wizardFeatures[this.featureEditingIndex].id
        : this.createFeatureId(submission.detail.summary);

    const entry: WizardFeature = {
      id: baseId,
      detail: submission.detail,
      approved: true,
      source: this.featureEditingIndex !== null ? this.wizardFeatures[this.featureEditingIndex].source : 'manual',
      stories: this.featureEditingIndex !== null ? [...this.wizardFeatures[this.featureEditingIndex].stories] : [],
    };

    if (this.featureEditingIndex !== null) {
      this.wizardFeatures[this.featureEditingIndex] = entry;
    } else {
      this.wizardFeatures = this.sortWizardFeatures([...this.wizardFeatures, entry]);
    }

    if (submission.files.length) {
      this.projectFiles = [...this.projectFiles, ...submission.files];
    }

    this.invalidateStoryRecommendations(true);
    this.isFeatureFormOpen = false;
    this.featureEditingIndex = null;
    this.featurePreset = null;
    this.featureFormSaving = false;
  }

  protected onRequestAISummary(): void {
    if (this.aiSummaryLoading) {
      return;
    }
    this.requestAISummary.emit(this.details);
  }

  protected onRefreshFeatureRecommendations(): void {
    this.hasRequestedFeatureRecommendations = false;
    this.invalidateStoryRecommendations(true);
    this.maybeRequestFeatureRecommendations();
  }

  protected onRefreshStoryRecommendations(): void {
    this.hasRequestedStoryRecommendations = false;
    this.invalidateStoryRecommendations(true);
    this.maybeRequestStoryRecommendations();
  }

  protected approveAllFeatures(): void {
    this.wizardFeatures = this.wizardFeatures.map((feature) => ({
      ...feature,
      approved: true,
    }));
    this.invalidateStoryRecommendations(false);
  }

  protected approveAllFeaturesAndStories(): void {
    this.wizardFeatures = this.wizardFeatures.map((feature) => ({
      ...feature,
      approved: true,
      stories: feature.stories.map((story) => ({ ...story, approved: true })),
    }));
  }

  protected onToggleStoryApproval(featureIndex: number, storyIndex: number): void {
    const feature = this.wizardFeatures[featureIndex];
    if (!feature) {
      return;
    }
    const nextStories = feature.stories.map((story, idx) =>
      idx === storyIndex ? { ...story, approved: !story.approved } : story,
    );
    this.wizardFeatures[featureIndex] = { ...feature, stories: nextStories };
  }

  protected onEditStory(featureIndex: number, storyIndex: number): void {
    const feature = this.wizardFeatures[featureIndex];
    if (!feature) {
      return;
    }
    const story = feature.stories[storyIndex];
    if (!story) {
      return;
    }
    this.editStory.emit({
      featureIndex,
      storyIndex,
      story: story.spec,
      featureDetail: feature.detail,
    });
  }

  protected onDismissStory(featureIndex: number, storyIndex: number): void {
    this.wizardFeatures = this.wizardFeatures.map((feature, idx) => {
      if (idx !== featureIndex) {
        return feature;
      }
      return {
        ...feature,
        stories: feature.stories.filter((_, sIdx) => sIdx !== storyIndex),
      };
    });
    this.dismissStory.emit({ featureIndex, storyIndex });
  }

  protected onNext(): void {
    if (!this.canProceed()) {
      return;
    }
    const nextIndex = Math.min(this.stepIndex + 1, this.steps.length - 1);
    this.stepIndex = nextIndex;
    this.onEnterStep(nextIndex);
  }

  protected onPrevious(): void {
    this.stepIndex = Math.max(this.stepIndex - 1, 0);
  }

  protected onSubmit(): void {
    if (!this.canSubmit()) {
      return;
    }

    const approvedFeatures = this.wizardFeatures.filter((feature) => feature.approved);
    const approvedStories = approvedFeatures.flatMap((feature) =>
      feature.stories.filter((story) => story.approved).map((story) => story.spec),
    );

    this.complete.emit({
      submission: {
        templateId: this.selectedTemplateId,
        workflowId: this.selectedWorkflow?.id ?? this.workflows[0]?.id ?? 'scrum-flow',
        details: this.details,
        aiSummary: this.aiSummary,
        features: approvedFeatures.map((feature) => feature.detail),
        stories: approvedStories,
        createdAt: new Date().toISOString(),
      },
      files: this.projectFiles,
    });
  }

  protected onCancel(): void {
    this.cancel.emit();
    this.resetWizard();
  }

  protected canProceed(): boolean {
    switch (this.stepIndex) {
      case 0:
        return Boolean(this.selectedTemplateId);
      case 1:
        return (
          this.details.name.trim().length >= 3 &&
          this.details.key.trim().length >= 2 &&
          this.details.description.trim().length >= 10
        );
      case 2:
        return this.aiSummary.executiveSummary.trim().length >= 20;
      case 3: {
        const approvedFeatures = this.getApprovedFeatures();
        return approvedFeatures.length > 0;
      }
      case 4: {
        const approvedStories = this.getApprovedStories();
        return approvedStories.length > 0;
      }
      default:
        return true;
    }
  }

  protected canSubmit(): boolean {
    if (this.stepIndex !== this.steps.length - 1) {
      return false;
    }
    const approvedFeatures = this.getApprovedFeatures();
    const approvedStories = this.getApprovedStories();
    return approvedFeatures.length > 0 && approvedStories.length > 0;
  }

  protected resetWizard(): void {
    this.stepIndex = 0;
    this.selectedTemplateId = null;
    this.selectedWorkflowId = null;
    this.details = {
      name: '',
      key: '',
      description: '',
      industry: 'General',
      methodology: 'scrum',
      timezone: 'UTC',
      startDate: null,
      targetLaunch: null,
      teamSize: null,
    };
    this.aiSummary = {
      executiveSummary: '',
      epicIdeas: [],
      riskNotes: [],
      customPrompt: '',
    };
    this.projectFiles = [];
    this.wizardFeatures = [];
    this.isFeatureFormOpen = false;
    this.featureEditingIndex = null;
    this.featurePreset = null;
    this.hasRequestedFeatureRecommendations = false;
    this.hasRequestedStoryRecommendations = false;
  }

  private onEnterStep(index: number): void {
    this.scrollWizardToTop();
    if (index === 2 && !this.aiSummary.executiveSummary.trim().length) {
      this.seedAISummary(this.selectedTemplate);
    }
    if (index === 3) {
      this.maybeRequestFeatureRecommendations();
    }
    if (index === 4) {
      this.maybeRequestStoryRecommendations();
    }
  }

  private scrollWizardToTop(): void {
    setTimeout(() => {
      const body = document.querySelector('.wizard-body');
      if (body instanceof HTMLElement) {
        body.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }, 0);
  }

  private maybeRequestFeatureRecommendations(): void {
    if (this.hasRequestedFeatureRecommendations || this.featureRecommendationsLoading) {
      return;
    }
    this.hasRequestedFeatureRecommendations = true;
    this.requestFeatureRecommendations.emit({
      details: this.details,
      aiSummary: this.aiSummary,
    });
  }

  private maybeRequestStoryRecommendations(): void {
    if (this.hasRequestedStoryRecommendations || this.storyRecommendationsLoading) {
      return;
    }
    const approvedFeatures = this.wizardFeatures.filter((feature) => feature.approved);
    if (!approvedFeatures.length) {
      return;
    }
    this.hasRequestedStoryRecommendations = true;
    this.requestStoryRecommendations.emit({
      details: this.details,
      aiSummary: this.aiSummary,
      features: approvedFeatures.map((feature) => feature.detail),
    });
  }

  private applyFeatureRecommendations(recommendations: AgentFeatureDetail[]): void {
    let changed = false;
    const nextFeatures = [...this.wizardFeatures];

    recommendations.forEach((detail) => {
      const key = this.featureKey(detail);
      const existingIndex = nextFeatures.findIndex((feature) => this.featureKey(feature.detail) === key);

      if (existingIndex >= 0) {
        const existing = nextFeatures[existingIndex];
        if (existing.source === 'manual') {
          return;
        }
        nextFeatures[existingIndex] = {
          ...existing,
          detail,
          source: 'recommended',
        };
      } else {
        nextFeatures.push({
          id: this.createFeatureId(detail.summary),
          detail,
          approved: false,
          source: 'recommended',
          stories: [],
        });
      }
      changed = true;
    });

    if (changed) {
      this.wizardFeatures = this.sortWizardFeatures(nextFeatures);
      this.invalidateStoryRecommendations(true);
    }
  }

  private applyStoryRecommendations(recommendations: AgentStorySpec[]): void {
    if (!recommendations.length) {
      return;
    }

    const grouped = new Map<string, WizardStory[]>();

    recommendations.forEach((spec, index) => {
      const featureKey = spec.featureTitle.trim().toLowerCase();
      const list = grouped.get(featureKey) ?? [];
      const entry: WizardStory = {
        id: this.createStoryId(featureKey, spec, list.length || index),
        spec,
        approved: false,
      };
      grouped.set(featureKey, [...list, entry]);
    });

    this.wizardFeatures = this.wizardFeatures.map((feature) => {
      if (!feature.approved) {
        return { ...feature, stories: [] };
      }
      const key = feature.detail.summary.trim().toLowerCase();
      const stories = grouped.get(key) ?? [];
      return {
        ...feature,
        stories,
      };
    });
  }

  public updateStory(featureIndex: number, storyIndex: number, story: AgentStorySpec): void {
    this.wizardFeatures = this.wizardFeatures.map((feature, idx) => {
      if (idx !== featureIndex) {
        return feature;
      }
      const stories = feature.stories.map((entry, sIdx) =>
        sIdx === storyIndex ? { ...entry, spec: story } : entry,
      );
      return { ...feature, stories };
    });
  }

  private sortWizardFeatures(features: WizardFeature[]): WizardFeature[] {
    return [...features].sort((a, b) => {
      if (a.source !== b.source) {
        return a.source === 'recommended' ? -1 : 1;
      }
      return a.detail.summary.localeCompare(b.detail.summary);
    });
  }

  private invalidateStoryRecommendations(clear: boolean): void {
    if (clear) {
      this.wizardFeatures = this.wizardFeatures.map((feature) => ({
        ...feature,
        stories: [],
      }));
    }
    this.hasRequestedStoryRecommendations = false;
  }

  private getApprovedFeatures(): WizardFeature[] {
    return this.wizardFeatures.filter((feature) => feature.approved);
  }

  private getApprovedStories(): WizardStory[] {
    return this.getApprovedFeatures().flatMap((feature) =>
      feature.stories.filter((story) => story.approved),
    );
  }

  private seedAISummary(template?: ProjectTemplate): void {
    if (!template) {
      this.aiSummary = {
        executiveSummary: '',
        epicIdeas: [],
        riskNotes: [],
        customPrompt: '',
      };
      return;
    }

    this.aiSummary = {
      executiveSummary: template.summary,
      epicIdeas: template.focusAreas.map((focus, index) => `Epic ${index + 1}: ${focus}`),
      riskNotes: ['Pending AI insights based on your selected prompts.'],
      customPrompt: '',
    };
  }

  private createFeatureId(summary: string): string {
    const slug = summary.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-');
    return `${slug || 'feature'}-${Math.random().toString(36).slice(2, 6)}`;
  }

  private createStoryId(featureKey: string, story: AgentStorySpec, index: number): string {
    const slug = story.userStory.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 24);
    return `${featureKey}-${slug || index}`;
  }

  private featureKey(detail: AgentFeatureDetail): string {
    const base = detail.key?.trim().toLowerCase() || detail.summary.trim().toLowerCase();
    return base.replace(/[^a-z0-9]+/g, '-');
  }

}

