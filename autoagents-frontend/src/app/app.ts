import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit, inject, signal, AfterViewInit, ViewChild, ElementRef } from '@angular/core';
import mermaid from 'mermaid';

import { FeatureFormComponent } from './features/feature-form.component';
import { ProjectWizardComponent } from './project/project-wizard.component';
import {
  PROJECT_TEMPLATES,
  PROJECT_TIMEZONES,
  PROJECT_TEAM_SIZES,
  PROJECT_WORKFLOWS,
} from './project/project-wizard.data';
import { WorkspaceViewComponent } from './workspace/workspace-view.component';
import {
  Agent1Decision,
  Agent2Decision,
  AgentFeatureRequestPayload,
  AgentFeatureResponse,
  AgentFeatureSpec,
  AgentStoryRequestPayload,
  AgentStoryResponse,
  AgentStorySpec,
  AgentVisualizationRequestPayload,
  AgentVisualizationResponse,
  AISuggestionRequest,
  AISuggestionResponse,
  ChatMessage,
  HistoryEntry,
  MermaidAssetResponse,
  MermaidAssetUpdatePayload,
  AgentFeatureDetail,
  AgentFeatureRisk,
  FeatureFormSubmission,
  ProjectWizardAISummary,
  ProjectWizardDetails,
  ProjectWizardSubmission,
  ProjectWizardSubmissionPayload,
} from './types';
import { StoryFormComponent } from './stories/story-form.component';
import { FeedbackChatbotComponent } from './feedback/feedback-chatbot.component';

type StoryFormContext =
  | { scope: 'wizard'; featureIndex: number; storyIndex: number; originalStory: AgentStorySpec }
  | { scope: 'workspace'; featureTitle: string; originalStory: AgentStorySpec };

type StoryFormContextInput =
  | { scope: 'wizard'; featureIndex: number; storyIndex: number }
  | { scope: 'workspace'; featureTitle: string };

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, WorkspaceViewComponent, ProjectWizardComponent, FeatureFormComponent, StoryFormComponent, FeedbackChatbotComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit, OnDestroy, AfterViewInit {
  protected readonly appTitle = 'Autoagents';
  protected readonly backendHost = 'http://localhost';
  protected readonly backendPort = 8000;
  protected readonly backendUrl = `${this.backendHost}:${this.backendPort}`;
  protected readonly rightNowStatus = signal('Loading status…');
  protected readonly isChatting = signal(false);
  protected readonly isSending = signal(false);
  protected readonly chatInput = signal('');
  protected readonly chatMessages = signal<ChatMessage[]>(this.createInitialMessages());
  protected readonly agentStage = signal<'agent1' | 'agent2'>('agent1');
  protected readonly agent1RunId = signal<string | null>(null);
  protected readonly agent2RunId = signal<string | null>(null);
  protected readonly agent1AwaitingDecision = signal(false);
  protected readonly agent2AwaitingDecision = signal(false);
  protected readonly lastPrompt = signal('');
  protected readonly latestFeatures = signal<AgentFeatureSpec[]>([]);
  protected readonly latestStories = signal<AgentStorySpec[]>([]);
  protected readonly agent1SelectedFeatures = signal<Set<string>>(new Set());
  protected readonly agent2SelectedStories = signal<Set<string>>(new Set());
  protected readonly conversationHistory = signal<HistoryEntry[]>([]);
  protected readonly activeConversationId = signal<string>(this.createConversationId());
  protected readonly isFullScreen = signal(false);
  protected readonly isWorkspaceMode = signal(false);
  protected readonly isChatDrawerOpen = signal(false);
  protected readonly workspacePrompt = signal('');
  protected readonly workspaceFeatures = signal<AgentFeatureSpec[]>([]);
  protected readonly workspaceStories = signal<AgentStorySpec[]>([]);
  protected readonly workspaceVisualization = signal<AgentVisualizationResponse | null>(null);
  protected readonly workspaceMermaid = signal('');
  protected readonly workspaceMermaidSaving = signal(false);
  protected readonly workspaceMermaidSaveMessage = signal<string | null>(null);
  protected readonly workspaceMermaidUpdatedAt = signal<string | null>(null);
  protected readonly isStoryFormOpen = signal(false);
  protected readonly storyFormSaving = signal(false);
  protected readonly storyFormDraft = signal<AgentStorySpec | null>(null);
  protected readonly storyFormFeatureReadonly = signal(false);
  protected readonly storyFormAiLoading = signal(false);
  protected readonly mermaidChatInput = signal('');
  protected readonly mermaidChatError = signal<string | null>(null);
  protected readonly workspaceProject = signal<ProjectWizardSubmission | null>(null);
  protected readonly workspaceProjectId = signal<string | null>(null); // MongoDB project ID if saved
  protected readonly isProjectWizardOpen = signal(false);
  protected readonly projectWizardSaving = signal(false);
  protected readonly projectWizardAiLoading = signal(false);
  protected readonly projectWizardSummaryDraft = signal<ProjectWizardAISummary | null>(null);
  protected readonly projectWizardLastSubmission = signal<ProjectWizardSubmission | null>(null);
  protected readonly projectWizardSuggestionResponse = signal<{ suggestionId: string; output: string } | null>(null);

  protected readonly projectWizardTemplates = PROJECT_TEMPLATES;
  protected readonly projectWizardWorkflows = PROJECT_WORKFLOWS;
  protected readonly projectWizardTimezones = PROJECT_TIMEZONES;
  protected readonly projectWizardTeamSizes = PROJECT_TEAM_SIZES;
  protected readonly isFeatureFormOpen = signal(false);
  protected readonly featureFormSaving = signal(false);
  protected readonly featureFormDraft = signal<AgentFeatureDetail | null>(null);
  protected readonly featureFormAiLoading = signal(false);
  protected readonly featureFormEditTarget = signal<string | null>(null);
  protected readonly projectWizardFeatureRecommendations = signal<AgentFeatureDetail[]>([]);
  protected readonly projectWizardStoryRecommendations = signal<AgentStorySpec[]>([]);
  protected readonly projectWizardFeaturesLoading = signal(false);
  protected readonly projectWizardStoriesLoading = signal(false);

  @ViewChild('chatMermaidContainer') private chatMermaidContainer?: ElementRef<HTMLDivElement>;
  @ViewChild(FeatureFormComponent) private featureFormRef?: FeatureFormComponent;
  @ViewChild(ProjectWizardComponent) private projectWizardRef?: ProjectWizardComponent;
  @ViewChild(StoryFormComponent) private storyFormRef?: StoryFormComponent;

  private readonly http = inject(HttpClient);
  private mermaidChatInitialised = false;
  private mermaidChatRenderIndex = 0;
  private projectWizardCompletionTimer: ReturnType<typeof setTimeout> | null = null;
  private projectWizardAiTimer: ReturnType<typeof setTimeout> | null = null;
  private featureFormTimer: ReturnType<typeof setTimeout> | null = null;
  private storyFormContext: StoryFormContext | null = null;

  ngOnInit(): void {
    this.fetchRightNowStatus();
    this.clearMermaidDiagram();
  }

  ngAfterViewInit(): void {
    this.renderChatMermaid();
  }

  ngOnDestroy(): void {
    this.setFullScreen(false);
    this.cancelProjectWizardTimers();
    this.cancelFeatureFormTimer();
  }

  protected continueToChat(): void {
    this.openChatDrawer();
    this.isChatting.set(true);
  }

  protected onChatInput(value: string): void {
    this.chatInput.set(value);
  }

  protected onChatSubmit(event: Event): void {
    event.preventDefault();
    this.sendChatMessage();
  }

  protected onNewChat(): void {
    if (this.isSending()) {
      return;
    }

    this.ensureChatOpen();
    this.archiveCurrentConversation();
    this.activeConversationId.set(this.createConversationId());
    this.resetConversationState();
    this.isChatting.set(true);
  }

  protected onHistorySelect(conversationId: string): void {
    if (this.isSending()) {
      return;
    }

    this.ensureChatOpen();

    this.archiveCurrentConversation();

    const sessions = this.conversationHistory();
    const match = sessions.find((session: HistoryEntry) => session.id === conversationId);
    if (!match) {
      return;
    }

    this.loadConversation(match);
    const remaining = sessions.filter((session: HistoryEntry) => session.id !== conversationId);
    this.conversationHistory.set([match, ...remaining]);
  }

  protected toggleFullScreen(): void {
    const next = !this.isFullScreen();
    this.setFullScreen(next);
  }

  protected toggleChatDrawer(): void {
    this.isChatDrawerOpen.update((open) => !open);
  }

  protected openChatDrawer(): void {
    this.isChatDrawerOpen.set(true);
  }

  protected closeChatDrawer(): void {
    this.isChatDrawerOpen.set(false);
  }

  protected onWorkspaceExit(): void {
    this.openChatDrawer();
  }

  protected formatTimestamp(epochMs: number): string {
    try {
      return new Date(epochMs).toLocaleString();
    } catch {
      return '';
    }
  }

  private setFullScreen(next: boolean): void {
    this.isFullScreen.set(next);
    document.body.classList.toggle('chat-fullscreen', next);
  }

  private ensureChatOpen(): void {
    if (!this.isChatDrawerOpen()) {
      this.isChatDrawerOpen.set(true);
    }
  }

  private openWorkspace(features: AgentFeatureSpec[], stories: AgentStorySpec[]): void {
    const featureClones = features.map((feature: AgentFeatureSpec) => this.cloneFeature(feature));
    const storyClones = stories.map((story: AgentStorySpec) => this.cloneStory(story));

    this.workspacePrompt.set(this.lastPrompt());
    this.workspaceFeatures.set(featureClones);
    this.workspaceStories.set(storyClones);
    this.workspaceVisualization.set(null);
    this.workspaceMermaid.set('');
    this.workspaceMermaidUpdatedAt.set(null);
    this.workspaceMermaidSaveMessage.set(null);
    this.workspaceMermaidSaving.set(false);
    this.workspaceProjectId.set(null); // Clear projectId when opening workspace from chat
    this.clearMermaidDiagram();
    this.isWorkspaceMode.set(true);
    this.isChatting.set(true);
    this.setFullScreen(true);
    this.fetchMermaidAsset();
  }

  private renderChatMermaid(): void {
    if (!this.chatMermaidContainer) {
      return;
    }

    if (!this.mermaidChatInitialised) {
      mermaid.initialize({ startOnLoad: false, theme: 'dark' });
      this.mermaidChatInitialised = true;
    }

    const definition = this.mermaidChatInput().trim();
    if (!definition) {
      this.chatMermaidContainer.nativeElement.innerHTML = '<p class="mermaid-placeholder">Agent 3 will generate a Mermaid diagram after user stories are approved.</p>';
      this.mermaidChatError.set(null);
      return;
    }

    const renderId = `chat-mermaid-${this.mermaidChatRenderIndex++}`;

    mermaid
      .render(renderId, definition)
      .then(({ svg }: { svg: string }) => {
        this.chatMermaidContainer!.nativeElement.innerHTML = svg;
        this.mermaidChatError.set(null);
      })
      .catch(() => {
        this.chatMermaidContainer!.nativeElement.innerHTML = '';
        this.mermaidChatError.set('Mermaid syntax error. Please review the diagram definition.');
      });
  }

  private clearMermaidDiagram(): void {
    this.mermaidChatInput.set('');
    this.mermaidChatError.set(null);
    this.mermaidChatRenderIndex = 0;
    this.renderChatMermaid();
  }

  private createInitialMessages(): ChatMessage[] {
    return [
      {
        sender: 'assistant',
        agent: 'agent1',
        text: 'Hello! I am the AutoAgents agent. Share your business idea and I will outline the feature roadmap.',
      },
    ];
  }

  private createConversationId(): string {
    return `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
  }

  private archiveCurrentConversation(): void {
    const messages = this.chatMessages();
    const userMessages = messages.filter((message: ChatMessage) => message.sender === 'user');
    if (userMessages.length === 0) {
      return;
    }

    const snapshot: HistoryEntry = {
      id: this.activeConversationId(),
      title: this.deriveConversationTitle(userMessages[0].text),
      createdAt: Date.now(),
      messages: this.cloneMessages(messages),
      agentStage: this.agentStage(),
      agent1RunId: this.agent1RunId(),
      agent2RunId: this.agent2RunId(),
      agent1AwaitingDecision: this.agent1AwaitingDecision(),
      agent2AwaitingDecision: this.agent2AwaitingDecision(),
      lastPrompt: this.lastPrompt(),
      latestFeatures: this.latestFeatures().map((feature: AgentFeatureSpec) => this.cloneFeature(feature)),
      latestStories: this.latestStories().map((story: AgentStorySpec) => this.cloneStory(story)),
      project: this.workspaceProject(),
    };

    this.conversationHistory.update((sessions: HistoryEntry[]) => {
      const existing = sessions.find((session: HistoryEntry) => session.id === snapshot.id);
      const snapshotWithTime: HistoryEntry = {
        ...snapshot,
        createdAt: existing?.createdAt ?? snapshot.createdAt,
      };

      return [
        snapshotWithTime,
        ...sessions.filter((session: HistoryEntry) => session.id !== snapshot.id),
      ];
    });
  }

  private startAgent2(features: AgentFeatureSpec[]): void {
    if (!features.length) {
      return;
    }

    this.latestFeatures.set(
      features.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)),
    );
    this.resetAgent1Selections(this.latestFeatures());
    this.latestStories.set([]);
    this.resetAgent2Selections([]);
    this.clearMermaidDiagram();
    this.agentStage.set('agent2');
    this.agent2AwaitingDecision.set(false);
    this.agent2RunId.set(null);

    this.appendMessage({
      sender: 'assistant',
      agent: 'agent2',
      text: 'Agent 2 is generating user stories based on the approved features...',
    });

    this.invokeAgent2(
      features.map((feature: AgentFeatureSpec) => ({
        ...feature,
        acceptanceCriteria: [...feature.acceptanceCriteria],
      })),
    );
  }

  private resetConversationState(): void {
    this.chatMessages.set(this.createInitialMessages());
    this.agentStage.set('agent1');
    this.agent1RunId.set(null);
    this.agent2RunId.set(null);
    this.agent1AwaitingDecision.set(false);
    this.agent2AwaitingDecision.set(false);
    this.lastPrompt.set('');
    this.latestFeatures.set([]);
    this.resetAgent1Selections([]);
    this.latestStories.set([]);
    this.resetAgent2Selections([]);
    this.chatInput.set('');
    this.workspaceVisualization.set(null);
    this.workspaceMermaid.set('');
    this.workspaceProject.set(null);
    this.workspaceProjectId.set(null); // Clear projectId when resetting conversation
    this.clearMermaidDiagram();
  }

  private loadConversation(session: HistoryEntry): void {
    this.chatMessages.set(this.cloneMessages(session.messages));
    this.agentStage.set(session.agentStage);
    this.agent1RunId.set(session.agent1RunId);
    this.agent2RunId.set(session.agent2RunId);
    this.agent1AwaitingDecision.set(session.agent1AwaitingDecision);
    this.agent2AwaitingDecision.set(session.agent2AwaitingDecision);
    this.lastPrompt.set(session.lastPrompt);
    this.latestFeatures.set(session.latestFeatures.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)));
    this.resetAgent1Selections(this.latestFeatures());
    this.latestStories.set(session.latestStories.map((story: AgentStorySpec) => this.cloneStory(story)));
    this.resetAgent2Selections(this.latestStories());
    this.workspaceMermaid.set('');
    this.workspaceProject.set(session.project ?? null);
    this.activeConversationId.set(session.id);
    this.isChatting.set(true);
    this.isSending.set(false);
    this.isWorkspaceMode.set(false);
    this.clearMermaidDiagram();
    if (this.latestFeatures().length && this.latestStories().length) {
      this.invokeAgent3(this.latestFeatures(), this.latestStories());
    }
  }

  private deriveConversationTitle(text: string): string {
    const trimmed = text.trim();
    if (!trimmed) {
      return 'Untitled conversation';
    }
    return trimmed.length > 40 ? `${trimmed.slice(0, 40)}…` : trimmed;
  }

  private cloneMessages(messages: ChatMessage[]): ChatMessage[] {
    return messages.map((message: ChatMessage) => ({
      ...message,
      features: message.features?.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)),
      stories: message.stories?.map((story: AgentStorySpec) => this.cloneStory(story)),
    }));
  }

  private cloneFeature(feature: AgentFeatureSpec): AgentFeatureSpec {
    return {
      title: feature.title,
      description: feature.description,
      acceptanceCriteria: [...feature.acceptanceCriteria],
      detail: feature.detail ? this.cloneFeatureDetail(feature.detail) : undefined,
    };
  }

  private cloneFeatureDetail(detail: AgentFeatureDetail): AgentFeatureDetail {
    return {
      summary: detail.summary,
      key: detail.key,
      problemStatement: detail.problemStatement,
      businessObjective: detail.businessObjective,
      userPersona: detail.userPersona,
      description: detail.description,
      acceptanceCriteria: [...detail.acceptanceCriteria],
      successMetrics: [...detail.successMetrics],
      stakeholders: [...detail.stakeholders],
      dependencies: [...detail.dependencies],
      constraints: [...detail.constraints],
      risks: detail.risks.map((risk: AgentFeatureRisk) => ({ ...risk })),
      targetRelease: detail.targetRelease,
      priority: detail.priority,
      nonFunctionalRequirements: [...detail.nonFunctionalRequirements],
      status: detail.status,
      team: detail.team,
    };
  }

  private featureTrackingKey(feature: AgentFeatureSpec): string {
    const detailKey = feature.detail?.key?.trim().toLowerCase();
    if (detailKey?.length) {
      return detailKey;
    }
    return feature.title?.trim().toLowerCase() ?? '';
  }

  private detailTrackingKey(detail: AgentFeatureDetail): string {
    const key = detail.key?.trim().toLowerCase();
    if (key?.length) {
      return key;
    }
    return detail.summary?.trim().toLowerCase() ?? '';
  }

  private storyTrackingKey(featureTitle: string, story: AgentStorySpec): string {
    const featureKey = featureTitle.trim().toLowerCase();
    const storyKey = story.userStory.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-');
    return `${featureKey}::${storyKey}`;
  }

  private extractFeatureKeys(features: AgentFeatureSpec[]): Set<string> {
    const keys = new Set<string>();
    for (const feature of features) {
      const key = this.featureTrackingKey(feature);
      if (key) {
        keys.add(key);
      }
    }
    return keys;
  }

  private resetAgent1Selections(features: AgentFeatureSpec[]): void {
    this.agent1SelectedFeatures.set(this.extractFeatureKeys(features));
  }

  private syncAgent1Selections(): void {
    const currentSelections = this.agent1SelectedFeatures();
    if (!currentSelections.size) {
      this.agent1SelectedFeatures.set(new Set());
      return;
    }

    const validKeys = this.extractFeatureKeys(this.latestFeatures());
    const nextSelections = new Set<string>();
    for (const key of validKeys) {
      if (currentSelections.has(key)) {
        nextSelections.add(key);
      }
    }

    this.agent1SelectedFeatures.set(nextSelections);
  }

  private setFeatureSelection(key: string, selected: boolean): void {
    if (!key) {
      return;
    }

    const currentSelections = this.agent1SelectedFeatures();
    const nextSelections = new Set<string>(currentSelections);
    if (selected) {
      nextSelections.add(key);
    } else {
      nextSelections.delete(key);
    }

    const validKeys = this.extractFeatureKeys(this.latestFeatures());
    const prunedSelections = new Set<string>();
    for (const validKey of validKeys) {
      if (nextSelections.has(validKey)) {
        prunedSelections.add(validKey);
      }
    }

    this.agent1SelectedFeatures.set(prunedSelections);
  }

  private getSelectedLatestFeatures(): AgentFeatureSpec[] {
    const selectedKeys = this.agent1SelectedFeatures();
    if (!selectedKeys.size) {
      return [];
    }

    return this.latestFeatures().filter((feature) => selectedKeys.has(this.featureTrackingKey(feature)));
  }

  protected canSelectFeatures(message: ChatMessage): boolean {
    if (
      this.agentStage() !== 'agent1' ||
      !this.agent1AwaitingDecision() ||
      message.agent !== 'agent1' ||
      !message.features?.length
    ) {
      return false;
    }

    const runId = this.agent1RunId();
    return Boolean(runId && message.runId === runId);
  }

  protected isFeatureSelected(feature: AgentFeatureSpec): boolean {
    const key = this.featureTrackingKey(feature);
    return Boolean(key && this.agent1SelectedFeatures().has(key));
  }

  protected onFeatureSelectionChange(feature: AgentFeatureSpec, selected: boolean): void {
    const key = this.featureTrackingKey(feature);
    this.setFeatureSelection(key, selected);
  }

  protected onFeatureSelectionInput(event: Event, feature: AgentFeatureSpec): void {
    event.stopPropagation();
    const target = event.target as HTMLInputElement | null;
    this.onFeatureSelectionChange(feature, !!target?.checked);
  }

  private extractStoryKeys(stories: AgentStorySpec[]): Set<string> {
    const keys = new Set<string>();
    for (const story of stories) {
      const featureTitle = story.featureTitle ?? '';
      const key = this.storyTrackingKey(featureTitle, story);
      if (key) {
        keys.add(key);
      }
    }
    return keys;
  }

  private resetAgent2Selections(stories: AgentStorySpec[]): void {
    this.agent2SelectedStories.set(this.extractStoryKeys(stories));
  }

  private syncAgent2Selections(): void {
    const currentSelections = this.agent2SelectedStories();
    if (!currentSelections.size) {
      this.agent2SelectedStories.set(new Set());
      return;
    }

    const validKeys = this.extractStoryKeys(this.latestStories());
    const nextSelections = new Set<string>();
    for (const key of validKeys) {
      if (currentSelections.has(key)) {
        nextSelections.add(key);
      }
    }

    this.agent2SelectedStories.set(nextSelections);
  }

  private setStorySelection(key: string, selected: boolean): void {
    if (!key) {
      return;
    }

    const currentSelections = this.agent2SelectedStories();
    const nextSelections = new Set<string>(currentSelections);
    if (selected) {
      nextSelections.add(key);
    } else {
      nextSelections.delete(key);
    }

    const validKeys = this.extractStoryKeys(this.latestStories());
    const prunedSelections = new Set<string>();
    for (const validKey of validKeys) {
      if (nextSelections.has(validKey)) {
        prunedSelections.add(validKey);
      }
    }

    this.agent2SelectedStories.set(prunedSelections);
  }

  private getSelectedLatestStories(): AgentStorySpec[] {
    const selectedKeys = this.agent2SelectedStories();
    if (!selectedKeys.size) {
      return [];
    }

    return this.latestStories().filter((story) =>
      selectedKeys.has(this.storyTrackingKey(story.featureTitle ?? '', story)),
    );
  }

  protected canSelectStories(message: ChatMessage): boolean {
    if (
      this.agentStage() !== 'agent2' ||
      !this.agent2AwaitingDecision() ||
      message.agent !== 'agent2' ||
      !message.stories?.length
    ) {
      return false;
    }

    const runId = this.agent2RunId();
    return Boolean(runId && message.runId === runId);
  }

  protected isStorySelected(story: AgentStorySpec): boolean {
    const key = this.storyTrackingKey(story.featureTitle ?? '', story);
    return Boolean(key && this.agent2SelectedStories().has(key));
  }

  protected onStorySelectionChange(story: AgentStorySpec, selected: boolean): void {
    const key = this.storyTrackingKey(story.featureTitle ?? '', story);
    this.setStorySelection(key, selected);
  }

  protected onStorySelectionInput(event: Event, story: AgentStorySpec): void {
    event.stopPropagation();
    const target = event.target as HTMLInputElement | null;
    this.onStorySelectionChange(story, !!target?.checked);
  }

  private applyWorkspaceStoryUpdate(
    featureTitle: string,
    existing: AgentStorySpec,
    updated: AgentStorySpec,
    notify = true,
  ): void {
    const featureTitleKey = featureTitle.trim().toLowerCase();
    const existingKey = this.storyTrackingKey(featureTitle, existing);
    const updatedStory = this.cloneStory({ ...updated, featureTitle });

    this.workspaceStories.update((stories) =>
      stories.map((story) => {
        const storyKey = this.storyTrackingKey(story.featureTitle, story);
        return storyKey === existingKey ? updatedStory : story;
      }),
    );

    this.latestStories.update((stories) =>
      stories.map((story) => {
        const storyKey = this.storyTrackingKey(story.featureTitle, story);
        return storyKey === existingKey ? updatedStory : story;
      }),
    );
    this.syncAgent2Selections();

    this.workspaceProject.update((project) => {
      if (!project) {
        return project;
      }
      const stories = project.stories.map((story) => {
        const storyKey = this.storyTrackingKey(story.featureTitle, story);
        return storyKey === existingKey ? updatedStory : story;
      });
      return {
        ...project,
        stories,
      };
    });

    // Update features detail acceptance criteria if necessary (no change here).
    if (notify) {
      this.appendMessage({
        sender: 'assistant',
        agent: 'agent2',
        text: `Story for "${featureTitle}" refined.`,
        stories: [updatedStory],
        runId: null,
      });
    }
  }

  private removeWorkspaceStory(featureTitle: string, story: AgentStorySpec): void {
    const storyKey = this.storyTrackingKey(featureTitle, story);

    this.workspaceStories.update((stories) =>
      stories.filter((entry) => this.storyTrackingKey(entry.featureTitle, entry) !== storyKey),
    );

    this.latestStories.update((stories) =>
      stories.filter((entry) => this.storyTrackingKey(entry.featureTitle, entry) !== storyKey),
    );
    this.syncAgent2Selections();

    this.workspaceProject.update((project) => {
      if (!project) {
        return project;
      }
      return {
        ...project,
        stories: project.stories.filter(
          (entry) => this.storyTrackingKey(entry.featureTitle, entry) !== storyKey,
        ),
      };
    });

    this.appendMessage({
      sender: 'assistant',
      agent: 'agent2',
      text: `Story "${story.userStory}" was dismissed from feature "${featureTitle}".`,
      runId: null,
    });
  }

  private cloneStory(story: AgentStorySpec): AgentStorySpec {
    return {
      featureTitle: story.featureTitle,
      userStory: story.userStory,
      acceptanceCriteria: [...story.acceptanceCriteria],
      implementationNotes: [...story.implementationNotes],
    };
  }

  private fetchRightNowStatus(): void {
    this.http
      .get<{ status: string }>(`${this.backendUrl}/status/right-now`)
      .subscribe({
        next: (response: { status: string }) => {
          console.debug('[status]', response);
          this.rightNowStatus.set(response.status);
        },
        error: (error: unknown) => {
          console.debug('[status:error]', error);
          this.rightNowStatus.set(
            'Unable to reach Autoagents backend. Start FastAPI to see live status.'
          );
        },
      });
  }

  private sendChatMessage(): void {
    const pendingMessage = this.chatInput().trim();
    if (!pendingMessage || this.isSending()) {
      return;
    }

    this.ensureChatOpen();
    this.appendMessage({ sender: 'user', text: pendingMessage });
    this.chatInput.set('');
    this.isSending.set(true);
    this.agentStage.set('agent1');
    this.agent1AwaitingDecision.set(false);
    this.agent2AwaitingDecision.set(false);
    this.agent1RunId.set(null);
    this.agent2RunId.set(null);
    this.latestFeatures.set([]);
    this.resetAgent1Selections([]);
    this.latestStories.set([]);
    this.resetAgent2Selections([]);
    this.lastPrompt.set(pendingMessage);
    this.clearMermaidDiagram();

    const payload: AgentFeatureRequestPayload = { prompt: pendingMessage };
    console.debug('[agent1:request]', payload);

    this.http
      .post<AgentFeatureResponse>(`${this.backendUrl}/agent/features`, payload)
      .subscribe({
        next: (response: AgentFeatureResponse) => {
          console.debug('[agent1:response]', response);
          const features = response.features ?? [];
          const assistantMessage: ChatMessage = {
            sender: 'assistant',
            agent: 'agent1',
            text: response.summary ?? response.message,
            features,
            runId: response.run_id,
          };
          this.appendMessage(assistantMessage);
          this.latestFeatures.set(
          features.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)),
          );
          this.resetAgent1Selections(this.latestFeatures());
          this.agent1RunId.set(response.run_id);
          this.agent1AwaitingDecision.set(true);
          this.clearMermaidDiagram();
        },
        error: (error: unknown) => {
          console.error('[agent1:error]', error);
          this.appendMessage({
            sender: 'assistant',
            agent: 'agent1',
            text: 'Sorry, I could not reach Agent_1. Please try again.',
          });
          this.isSending.set(false);
        },
        complete: () => this.isSending.set(false),
      });
  }

  private appendMessage(message: ChatMessage): void {
    this.chatMessages.update((messages: ChatMessage[]) => [...messages, message]);
  }

  protected onAgent1Decision(decision: Agent1Decision): void {
    const runId = this.agent1RunId();
    const prompt = this.lastPrompt().trim();
    if (!runId || !prompt || this.isSending()) {
      return;
    }

    const payload: AgentFeatureRequestPayload = {
      prompt,
      decision,
      run_id: runId,
    };

    let featuresSnapshot: AgentFeatureSpec[] | undefined;
    if (decision === 'keep' || decision === 'keep_all') {
      const sourceFeatures =
        decision === 'keep_all' ? this.latestFeatures() : this.getSelectedLatestFeatures();
      if (!sourceFeatures.length) {
        console.warn(
          decision === 'keep'
            ? '[agent1:keep] No features selected to store.'
            : '[agent1:keep_all] No features available to store.',
        );
        return;
      }
      featuresSnapshot = sourceFeatures.map((feature: AgentFeatureSpec) => this.cloneFeature(feature));
      payload.features = featuresSnapshot;
    }

    console.debug('[agent1:decision]', payload);

    this.isSending.set(true);

    this.http
      .post<AgentFeatureResponse>(`${this.backendUrl}/agent/features`, payload)
      .subscribe({
        next: (response: AgentFeatureResponse) => {
          console.debug('[agent1:decision:response]', response);
          const features = response.features ?? [];
          const assistantMessage: ChatMessage = {
            sender: 'assistant',
            agent: 'agent1',
            text: response.summary ?? response.message,
            features,
            runId: response.run_id,
          };
          this.appendMessage(assistantMessage);

          if (response.decision === 'generated') {
            this.latestFeatures.set(
              features.map((feature: AgentFeatureSpec) => ({
                ...feature,
                acceptanceCriteria: [...feature.acceptanceCriteria],
              })),
            );
            this.resetAgent1Selections(this.latestFeatures());
            this.agent1RunId.set(response.run_id);
            this.agent1AwaitingDecision.set(true);
            this.clearMermaidDiagram();
          } else {
            this.agent1RunId.set(null);
            this.agent1AwaitingDecision.set(false);
            this.latestFeatures.set(featuresSnapshot ?? []);
            this.resetAgent1Selections(this.latestFeatures());
            this.clearMermaidDiagram();
            if (featuresSnapshot?.length) {
              this.startAgent2(featuresSnapshot);
            }
          }

          this.isSending.set(false);
        },
        error: (error: unknown) => {
          console.error('[agent1:decision:error]', error);
          this.appendMessage({
            sender: 'assistant',
            agent: 'agent1',
            text: 'Agent_1 could not process that request. Please retry.',
          });
          this.isSending.set(false);
        },
      });
  }

  protected onAgent2Decision(decision: Agent2Decision): void {
    if (this.isSending()) {
      return;
    }

    const features = this.latestFeatures();
    if (!features.length) {
      console.warn('[agent2] No approved features available for story generation.');
      return;
    }

    if (decision === 'keep') {
      if (!this.agent2RunId()) {
        console.warn('[agent2:keep] Missing run id to approve.');
        return;
      }
      const stories = this.latestStories();
      if (!stories.length) {
        console.warn('[agent2:keep] No stories captured to approve.');
        return;
      }
      const selectedStories = this.getSelectedLatestStories();
      if (!selectedStories.length) {
        console.warn('[agent2:keep] No stories selected to approve.');
        return;
      }
      const approvedStories = selectedStories.map((story: AgentStorySpec) => this.cloneStory(story));
      this.latestStories.set(approvedStories);
      this.resetAgent2Selections(approvedStories);
      this.invokeAgent2(
        features.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)),
        decision,
        approvedStories,
      );
      return;
    }

    this.invokeAgent2(features.map((feature: AgentFeatureSpec) => this.cloneFeature(feature)), decision);
  }

  private invokeAgent2(
    features: AgentFeatureSpec[],
    decision?: Agent2Decision,
    stories?: AgentStorySpec[]
  ): void {
    if (!features.length) {
      console.warn('[agent2] Cannot invoke without features.');
      return;
    }

    const payload: AgentStoryRequestPayload = {
      prompt: this.lastPrompt(),
      features,
    };

    if (decision) {
      payload.decision = decision;
      const runId = this.agent2RunId();
      if (runId) {
        payload.run_id = runId;
      } else if (decision === 'keep') {
        console.warn('[agent2:keep] No run id available to approve.');
        return;
      }
    }

    if (decision === 'keep') {
      const storyPayload = stories ?? this.latestStories();
      if (!storyPayload.length) {
        console.warn('[agent2:keep] No stories provided to approve.');
        return;
      }
      payload.stories = storyPayload.map((story: AgentStorySpec) => ({
        featureTitle: story.featureTitle,
        userStory: story.userStory,
        acceptanceCriteria: [...story.acceptanceCriteria],
        implementationNotes: [...story.implementationNotes],
      }));
    }

    const requestPayload: AgentStoryRequestPayload = {
      ...payload,
      features: payload.features?.map((feature: AgentFeatureSpec) => ({
        title: feature.title,
        description: feature.description,
        acceptanceCriteria: [...feature.acceptanceCriteria],
      })),
      stories: payload.stories ? [...payload.stories] : undefined,
    };

    console.debug(`[agent2:${decision ?? 'request'}]`, requestPayload);

    this.isSending.set(true);

    this.http
      .post<AgentStoryResponse>(`${this.backendUrl}/agent/stories`, requestPayload)
      .subscribe({
        next: (response: AgentStoryResponse) => {
          console.debug('[agent2:response]', response);
          const storiesResponse = response.stories ?? [];
          if (storiesResponse.length) {
            const nextStories = storiesResponse.map((story: AgentStorySpec) => ({
              ...story,
              acceptanceCriteria: [...story.acceptanceCriteria],
              implementationNotes: [...story.implementationNotes],
            }));
            this.latestStories.set(nextStories);
            this.resetAgent2Selections(this.latestStories());
          } else if (decision !== 'keep') {
            this.latestStories.set([]);
            this.resetAgent2Selections([]);
          }

          const assistantMessage: ChatMessage = {
            sender: 'assistant',
            agent: 'agent2',
            text: response.summary ?? response.message,
            stories: response.stories,
            runId: response.run_id,
          };
          this.appendMessage(assistantMessage);

          if (response.decision === 'generated') {
            this.agent2RunId.set(response.run_id);
            this.agent2AwaitingDecision.set(true);
            this.clearMermaidDiagram();
          } else {
            this.agent2RunId.set(null);
            this.agent2AwaitingDecision.set(false);
            this.openWorkspace(this.latestFeatures(), this.latestStories());
            this.invokeAgent3(this.latestFeatures(), this.latestStories());
          }

          this.isSending.set(false);
        },
        error: (error: unknown) => {
          console.error('[agent2:error]', error);
          this.appendMessage({
            sender: 'assistant',
            agent: 'agent2',
            text: 'Agent 2 could not process that request. Please retry.',
          });
          this.isSending.set(false);
        },
      });
  }

  private invokeAgent3(features: AgentFeatureSpec[], stories: AgentStorySpec[], diagramType: string = 'hld'): void {
    // Enhanced validation - check for both empty arrays and valid data
    if (!features || !stories || features.length === 0 || stories.length === 0) {
      console.warn(`[app] Skipping Agent 3 call for ${diagramType.toUpperCase()} - insufficient data | features=${features?.length || 0} | stories=${stories?.length || 0}`);
      this.workspaceMermaidSaveMessage.set(`Cannot generate ${diagramType.toUpperCase()} diagram: Need both features and stories.`);
      return;
    }

    const payload: AgentVisualizationRequestPayload = {
      prompt: this.lastPrompt(),
      features: features.map((feature: AgentFeatureSpec) => ({
        ...feature,
        acceptanceCriteria: [...feature.acceptanceCriteria],
      })),
      stories: stories.map((story: AgentStorySpec) => ({
        ...story,
        acceptanceCriteria: [...story.acceptanceCriteria],
        implementationNotes: [...story.implementationNotes],
      })),
      diagramType, // Include diagram type in payload
    };

    // Always use legacy endpoint for now since we don't have MongoDB project IDs in workspace
    // The new endpoint requires a MongoDB ObjectId, but workspace projects only have keys
    const endpoint = `${this.backendUrl}/agent/visualizer`;
    const requestPayload = { ...payload, diagramType };

    // Set loading state
    this.workspaceMermaidSaving.set(true);
    this.workspaceMermaidSaveMessage.set(`Generating ${diagramType.toUpperCase()} diagram...`);
    
    console.debug(`[app] Calling Agent 3 API: ${endpoint} | diagramType=${diagramType}`);
    
    this.http
      .post<AgentVisualizationResponse>(
        endpoint,
        requestPayload
      )
      .subscribe({
        next: (response: AgentVisualizationResponse) => {
          console.debug(`[app] Agent 3 response received | hasMermaid=${!!response.diagrams?.mermaid} | mermaidLength=${response.diagrams?.mermaid?.length || 0}`);
          
          // Legacy endpoint always returns AgentVisualizationResponse format
          this.workspaceVisualization.set(response);
          
          const mermaidContent = response.diagrams?.mermaid ?? '';
          if (mermaidContent && mermaidContent.trim()) {
            this.workspaceMermaid.set(mermaidContent);
            this.workspaceMermaidUpdatedAt.set(response.diagrams?.mermaidUpdatedAt ?? null);
            this.workspaceMermaidSaveMessage.set(`Diagram generated by Agent 3 (${diagramType.toUpperCase()}).`);
            this.mermaidChatInput.set(mermaidContent);
            this.renderChatMermaid();
            console.debug(`[app] ${diagramType.toUpperCase()} diagram successfully set | length=${mermaidContent.length} chars`);
          } else {
            console.warn(`[app] Agent 3 returned empty mermaid diagram for ${diagramType.toUpperCase()}`);
            this.workspaceMermaidSaveMessage.set(`Warning: ${diagramType.toUpperCase()} diagram generation returned empty content. Please try again.`);
          }
          
          this.workspaceMermaidSaving.set(false);
        },
        error: (error: unknown) => {
          console.error(`[app] Agent 3 API error for ${diagramType.toUpperCase()}:`, error);
          
          // Extract error details from HttpErrorResponse
          let errorMessage = 'Unknown error';
          let statusCode = 0;
          
          if (error && typeof error === 'object' && 'error' in error) {
            const httpError = error as any;
            statusCode = httpError.status || 0;
            errorMessage = httpError.error?.detail || httpError.message || httpError.statusText || 'Unknown error';
          } else if (error instanceof Error) {
            errorMessage = error.message;
          }
          
          // More user-friendly error messages based on status code and message
          let userMessage = `Failed to generate ${diagramType.toUpperCase()} diagram. `;
          
          if (statusCode === 503 || errorMessage.includes('Service Unavailable')) {
            userMessage += 'Agent 3 is temporarily unavailable. The Claude API may be experiencing issues. Please try again in a moment.';
          } else if (statusCode === 400 || errorMessage.includes('requires approved features')) {
            userMessage += 'Invalid request. Please ensure you have approved features and stories.';
          } else if (errorMessage.includes('API key') || errorMessage.includes('authentication') || errorMessage.includes('Missing Claude')) {
            userMessage += 'Claude API key not configured. Please check your backend configuration.';
          } else if (errorMessage.includes('timeout') || errorMessage.includes('network')) {
            userMessage += 'Network error. Please check your connection and try again.';
          } else if (statusCode === 429 || errorMessage.includes('rate limit')) {
            userMessage += 'Rate limit exceeded. Please wait a moment and try again.';
          } else {
            userMessage += `Error: ${errorMessage}`;
          }
          
          this.workspaceMermaidSaveMessage.set(userMessage);
          this.workspaceMermaidSaving.set(false);
          
          // Only show error in chat for non-temporary issues
          if (statusCode !== 503) {
            this.appendMessage({
              sender: 'assistant',
              agent: 'agent2',
              text: `Agent 3 could not generate the ${diagramType.toUpperCase()} diagram. ${userMessage}`,
              runId: null,
            });
          }
        },
      });
  }

  protected openProjectWizard(): void {
    this.cancelProjectWizardTimers();
    this.projectWizardSummaryDraft.set(null);
    this.projectWizardAiLoading.set(false);
    this.projectWizardSaving.set(false);
    this.projectWizardFeatureRecommendations.set([]);
    this.projectWizardStoryRecommendations.set([]);
    this.projectWizardFeaturesLoading.set(false);
    this.projectWizardStoriesLoading.set(false);
    this.isProjectWizardOpen.set(true);
  }

  protected openFeatureForm(): void {
    this.cancelFeatureFormTimer();
    this.featureFormSaving.set(false);
    this.featureFormEditTarget.set(null);
    this.featureFormAiLoading.set(false);
    this.isFeatureFormOpen.set(true);
    this.featureFormDraft.set(null);
  }

  protected onFeatureFormCancel(): void {
    this.isFeatureFormOpen.set(false);
    this.cancelFeatureFormTimer();
    this.featureFormSaving.set(false);
    this.featureFormEditTarget.set(null);
    this.featureFormDraft.set(null);
    this.featureFormAiLoading.set(false);
  }

  protected onFeatureFormSubmit(submission: FeatureFormSubmission): void {
    if (this.featureFormSaving()) {
      return;
    }

    this.featureFormAiLoading.set(false);
    this.featureFormSaving.set(true);
    this.featureFormDraft.set(submission.detail);

    const editKey = this.featureFormEditTarget();
    const existingFeature =
      editKey !== null
        ? this.workspaceFeatures().find((feature: AgentFeatureSpec) => this.featureTrackingKey(feature) === editKey)
        : null;
    const previousFeature = existingFeature ? this.cloneFeature(existingFeature) : null;

    this.cancelFeatureFormTimer();
    this.featureFormTimer = setTimeout(() => {
      if (previousFeature) {
        this.applyWorkspaceFeatureUpdate(
          previousFeature,
          submission.detail,
          'manual',
          `Feature "${submission.detail.summary}" updated manually.`,
          null,
        );
        if (submission.files.length) {
          this.uploadFeatureFiles(submission.files, submission.detail);
        }
      } else {
        const feature = this.createFeatureFromDetail(submission.detail);
        this.latestFeatures.update((features: AgentFeatureSpec[]) => [...features, feature]);
        this.syncAgent1Selections();
        if (this.isWorkspaceMode()) {
          this.workspaceFeatures.update((features: AgentFeatureSpec[]) => [
            ...features,
            this.cloneFeature(feature),
          ]);
          this.workspaceProject.update((project) =>
            project
              ? {
                  ...project,
                  features: [...project.features, this.cloneFeatureDetail(submission.detail)],
                }
              : project,
          );
        }

        this.appendMessage({
          sender: 'assistant',
          agent: 'agent1',
          text: `Manual feature captured: ${submission.detail.summary}`,
          features: [feature],
          runId: null,
        });
        this.uploadFeatureFiles(submission.files, submission.detail);
      }

      this.featureFormSaving.set(false);
      this.isFeatureFormOpen.set(false);
      this.featureFormDraft.set(null);
      this.featureFormEditTarget.set(null);
      this.featureFormAiLoading.set(false);
    }, 650);
  }

  protected onFeatureFormAi(prompt: string): void {
    const trimmed = prompt.trim();
    if (!trimmed || this.featureFormAiLoading()) {
      return;
    }

    this.featureFormAiLoading.set(true);
    const existingDetail = this.featureFormDraft();
    const project = this.workspaceProject();
    const promptBody = existingDetail
      ? `${this.composeFeatureEnhancementPrompt(this.createFeatureFromDetail(existingDetail), project)}\n\nProduct owner request:\n${trimmed}`
      : trimmed;
    const payload: AgentFeatureRequestPayload = { prompt: promptBody };

    this.http.post<AgentFeatureResponse>(`${this.backendUrl}/agent/features`, payload).subscribe({
      next: (response: AgentFeatureResponse) => {
        const spec = response.features?.[0];
        if (!spec) {
          console.warn('[feature-form:ai] No features returned for prompt.');
          this.featureFormAiLoading.set(false);
          return;
        }

        const existing = this.featureFormDraft();
        const detail = existing
          ? this.mergeFeatureDetail(existing, spec)
          : this.createFeatureDetailFromSpec(spec, 0);

        this.featureFormDraft.set(detail);
        this.featureFormRef?.applyAiDetail(detail);
        this.featureFormAiLoading.set(false);
      },
      error: (error: unknown) => {
        console.error('[feature-form:ai:error]', error);
        this.featureFormAiLoading.set(false);
      },
    });
  }

  protected onWorkspaceFeatureEdit(feature: AgentFeatureSpec): void {
    const detail = feature.detail
      ? this.cloneFeatureDetail(feature.detail)
      : this.createFeatureDetailFromSpec(feature, 0);
    this.cancelFeatureFormTimer();
    this.featureFormSaving.set(false);
    this.featureFormDraft.set(detail);
    this.featureFormEditTarget.set(this.featureTrackingKey(feature));
    this.isFeatureFormOpen.set(true);
  }

  protected onWorkspaceFeatureDismiss(feature: AgentFeatureSpec): void {
    const key = this.featureTrackingKey(feature);
    if (!key) {
      return;
    }
    this.workspaceFeatures.update((features) =>
      features.filter((entry) => this.featureTrackingKey(entry) !== key),
    );
    this.latestFeatures.update((features) =>
      features.filter((entry) => this.featureTrackingKey(entry) !== key),
    );
    this.syncAgent1Selections();
    this.workspaceProject.update((project) => {
      if (!project) {
        return project;
      }
      return {
        ...project,
        features: project.features.filter(
          (detail) => this.detailTrackingKey(detail) !== key,
        ),
        stories: project.stories.filter(
          (story) => story.featureTitle.trim().toLowerCase() !== feature.title.trim().toLowerCase(),
        ),
      };
    });
    this.workspaceStories.update((stories) =>
      stories.filter(
        (entry) => entry.featureTitle.trim().toLowerCase() !== feature.title.trim().toLowerCase(),
      ),
    );
    this.latestStories.update((stories) =>
      stories.filter(
        (entry) => entry.featureTitle.trim().toLowerCase() !== feature.title.trim().toLowerCase(),
      ),
    );
    this.syncAgent2Selections();
    this.appendMessage({
      sender: 'assistant',
      agent: 'agent1',
      text: `Feature "${feature.title}" was dismissed from the workspace.`,
      runId: null,
    });
  }

  protected onWorkspaceStoryEdit(event: { feature: AgentFeatureSpec; story: AgentStorySpec }): void {
    const { feature, story } = event;
    this.openStoryForm({ scope: 'workspace', featureTitle: feature.title }, story, true);
  }

  protected onWorkspaceStoryDismiss(event: { feature: AgentFeatureSpec; story: AgentStorySpec }): void {
    const { feature, story } = event;
    this.removeWorkspaceStory(feature.title, story);
  }

  protected onStoryFormCancel(): void {
    this.storyFormSaving.set(false);
    this.storyFormAiLoading.set(false);
    this.closeStoryForm();
  }

  protected onStoryFormAi(prompt: string): void {
    const trimmed = prompt.trim();
    if (!trimmed || this.storyFormAiLoading()) {
      return;
    }

    if (!this.storyFormContext) {
      return;
    }

    this.storyFormAiLoading.set(true);
    const existingStory = this.storyFormDraft();
    if (!existingStory) {
      this.storyFormAiLoading.set(false);
      return;
    }

    // Find the feature for context
    let feature: AgentFeatureSpec | AgentFeatureDetail | null = null;
    if (this.storyFormContext.scope === 'workspace') {
      const featureTitle = this.storyFormContext.featureTitle;
      const workspaceFeature = this.workspaceFeatures().find(
        (f) => f.title?.trim().toLowerCase() === featureTitle.trim().toLowerCase(),
      );
      feature = workspaceFeature ?? null;
    } else {
      // For wizard context, we'd need to get feature from wizard
      // For now, try to find from workspace features
      const featureTitle = existingStory.featureTitle;
      const workspaceFeature = this.workspaceFeatures().find(
        (f) => f.title?.trim().toLowerCase() === featureTitle.trim().toLowerCase(),
      );
      feature = workspaceFeature ?? null;
    }

    const project = this.workspaceProject();
    const promptBody = this.composeStoryEnhancementPrompt(
      feature ?? { title: existingStory.featureTitle, description: '', acceptanceCriteria: [] },
      existingStory,
      project,
    ) + `\n\nProduct owner request:\n${trimmed}`;
    // Helper to extract feature data from either AgentFeatureSpec or AgentFeatureDetail
    const getFeatureData = (f: AgentFeatureSpec | AgentFeatureDetail): AgentFeatureSpec => {
      if ('summary' in f) {
        // It's AgentFeatureDetail
        const detail = f as AgentFeatureDetail;
        return {
          title: detail.summary,
          description: detail.description,
          acceptanceCriteria: detail.acceptanceCriteria,
        };
      } else {
        // It's AgentFeatureSpec
        return f as AgentFeatureSpec;
      }
    };

    const payload: AgentStoryRequestPayload = {
      prompt: promptBody,
      features: feature ? [getFeatureData(feature)] : [],
    };

    this.http.post<AgentStoryResponse>(`${this.backendUrl}/agent/stories`, payload).subscribe({
      next: (response: AgentStoryResponse) => {
        const spec = response.stories?.[0];
        if (!spec) {
          console.warn('[story-form:ai] No stories returned for prompt.');
          this.storyFormAiLoading.set(false);
          return;
        }

        const refinedStory: AgentStorySpec = {
          featureTitle: existingStory.featureTitle,
          userStory: spec.userStory,
          acceptanceCriteria: spec.acceptanceCriteria ?? [],
          implementationNotes: spec.implementationNotes ?? [],
        };

        this.storyFormDraft.set(refinedStory);
        this.storyFormRef?.applyAiStory(refinedStory);
        this.storyFormAiLoading.set(false);
      },
      error: (error: unknown) => {
        console.error('[story-form:ai:error]', error);
        this.storyFormAiLoading.set(false);
      },
    });
  }

  protected onStoryFormSubmit(story: AgentStorySpec): void {
    if (!this.storyFormContext) {
      this.closeStoryForm();
      return;
    }

    this.storyFormSaving.set(true);

    if (this.storyFormContext.scope === 'wizard') {
      const { featureIndex, storyIndex, originalStory } = this.storyFormContext;
      const patched = this.cloneStory({
        ...story,
        featureTitle: originalStory.featureTitle,
      });
      this.projectWizardRef?.updateStory(featureIndex, storyIndex, patched);
    } else {
      const { featureTitle, originalStory } = this.storyFormContext;
      const patched = this.cloneStory({
        ...story,
        featureTitle,
      });
      this.applyWorkspaceStoryUpdate(featureTitle, originalStory, patched, false);
      this.appendMessage({
        sender: 'assistant',
        agent: 'agent2',
        text: `Story "${patched.userStory}" updated manually for feature "${featureTitle}".`,
        stories: [patched],
        runId: null,
      });
    }

    this.storyFormSaving.set(false);
    this.closeStoryForm();
  }

  private openStoryForm(
    context: StoryFormContextInput,
    story: AgentStorySpec,
    featureReadonly: boolean,
  ): void {
    this.storyFormContext =
      context.scope === 'wizard'
        ? {
            scope: 'wizard',
            featureIndex: context.featureIndex,
            storyIndex: context.storyIndex,
            originalStory: this.cloneStory(story),
          }
        : {
            scope: 'workspace',
            featureTitle: context.featureTitle,
            originalStory: this.cloneStory(story),
          };
    this.storyFormDraft.set(this.cloneStory(story));
    this.storyFormFeatureReadonly.set(featureReadonly);
    this.isStoryFormOpen.set(true);
    this.storyFormSaving.set(false);
    this.storyFormAiLoading.set(false);
  }

  private closeStoryForm(): void {
    this.storyFormContext = null;
    this.isStoryFormOpen.set(false);
    this.storyFormDraft.set(null);
    this.storyFormFeatureReadonly.set(false);
    this.storyFormSaving.set(false);
    this.storyFormAiLoading.set(false);
  }

  private createFeatureFromDetail(detail: AgentFeatureDetail): AgentFeatureSpec {
    return {
      title: detail.summary,
      description: detail.description,
      acceptanceCriteria: [...detail.acceptanceCriteria],
      detail: this.cloneFeatureDetail(detail),
    };
  }

  private createFeatureDetailFromSpec(spec: AgentFeatureSpec, index: number): AgentFeatureDetail {
    if (spec.detail) {
      return this.cloneFeatureDetail(spec.detail);
    }

    const summary = spec.title?.trim().length ? spec.title.trim() : `Recommended Feature ${index + 1}`;
    const description = spec.description?.trim().length
      ? spec.description.trim()
      : `Define ${summary} to serve key customer needs.`;
    const acceptanceCriteria =
      spec.acceptanceCriteria?.length && spec.acceptanceCriteria.some((item) => item.trim().length)
        ? spec.acceptanceCriteria
        : [
            'Capture acceptance criteria for this recommendation.',
            'Ensure success measures reflect the business outcome.',
          ];

    return {
      summary,
      key: this.createDefaultKey(summary),
      problemStatement: description,
      businessObjective: `Deliver ${summary} to unlock measurable value.`,
      userPersona: 'Primary customer persona',
      description,
      acceptanceCriteria: [...acceptanceCriteria],
      successMetrics: ['Adoption rate', 'Customer satisfaction index'],
      stakeholders: ['Product Owner'],
      dependencies: [],
      constraints: [],
      risks: [],
      targetRelease: 'TBD',
      priority: 'medium',
      nonFunctionalRequirements: [],
      status: 'Draft',
      team: '',
    };
  }

  private findWorkspaceFeatureDetail(featureTitle: string): AgentFeatureDetail | null {
    const titleKey = featureTitle.trim().toLowerCase();
    const match = this.workspaceFeatures().find(
      (feature) => feature.title?.trim().toLowerCase() === titleKey,
    );
    if (!match) {
      return null;
    }
    return match.detail ? this.cloneFeatureDetail(match.detail) : this.createFeatureDetailFromSpec(match, 0);
  }

  private mergeFeatureDetail(original: AgentFeatureDetail, spec: AgentFeatureSpec): AgentFeatureDetail {
    const base = this.createFeatureDetailFromSpec(spec, 0);
    return {
      ...original,
      summary: base.summary,
      description: base.description,
      problemStatement: base.problemStatement,
      businessObjective: base.businessObjective,
      acceptanceCriteria: base.acceptanceCriteria,
    };
  }

  private applyWorkspaceFeatureUpdate(
    previousFeature: AgentFeatureSpec,
    newDetail: AgentFeatureDetail,
    origin: 'ai' | 'manual',
    summary: string | null,
    runId: string | null,
  ): void {
    const targetKey = this.featureTrackingKey(previousFeature);
    const previousTitle = previousFeature.title ?? '';
    const previousTitleKey = previousTitle.trim().toLowerCase();
    const previousDetailSummary = previousFeature.detail?.summary ?? '';
    const previousDetailSummaryKey = previousDetailSummary.trim().toLowerCase();
    const updatedSpec = this.createFeatureFromDetail(newDetail);
    const newTitle = updatedSpec.title ?? '';
    const newTitleKey = newTitle.trim().toLowerCase();

    const matchesFeature = (feature: AgentFeatureSpec): boolean => {
      const featureKey = this.featureTrackingKey(feature);
      if (targetKey && featureKey === targetKey) {
        return true;
      }
      const featureTitleKey = feature.title?.trim().toLowerCase() ?? '';
      return (!targetKey && featureTitleKey === previousTitleKey) || featureTitleKey === previousDetailSummaryKey;
    };

    this.workspaceFeatures.update((features) =>
      features.map((feature) => (matchesFeature(feature) ? this.cloneFeature(updatedSpec) : feature)),
    );

    this.latestFeatures.update((features) =>
      features.map((feature) => (matchesFeature(feature) ? this.cloneFeature(updatedSpec) : feature)),
    );
    this.syncAgent1Selections();

    this.workspaceProject.update((project) => {
      if (!project) {
        return project;
      }
      let matched = false;
      const updatedFeatures = project.features.map((detail) => {
        const detailKey = this.detailTrackingKey(detail);
        const detailSummaryKey = detail.summary?.trim().toLowerCase() ?? '';
        const isMatch =
          (targetKey && detailKey === targetKey) ||
          detailSummaryKey === previousDetailSummaryKey ||
          detailSummaryKey === previousTitleKey;
        if (isMatch) {
          matched = true;
          return this.cloneFeatureDetail(newDetail);
        }
        return detail;
      });
      return {
        ...project,
        features: matched ? updatedFeatures : [...updatedFeatures, this.cloneFeatureDetail(newDetail)],
      };
    });

    if (previousTitleKey && previousTitleKey !== newTitleKey) {
      this.workspaceStories.update((stories) =>
        stories.map((story) =>
          story.featureTitle?.trim().toLowerCase() === previousTitleKey
            ? {
                ...story,
                featureTitle: newTitle,
              }
            : story,
        ),
      );

      this.latestStories.update((stories) =>
        stories.map((story) =>
          story.featureTitle?.trim().toLowerCase() === previousTitleKey
            ? {
                ...story,
                featureTitle: newTitle,
              }
            : story,
        ),
      );
      this.syncAgent2Selections();
    }

    const messageText =
      summary && summary.trim().length
        ? summary
        : origin === 'ai'
          ? `Agent 1 refined feature "${updatedSpec.title}".`
          : `Feature "${updatedSpec.title}" updated.`;

    this.appendMessage({
      sender: 'assistant',
      agent: 'agent1',
      text: messageText,
      features: [this.cloneFeature(updatedSpec)],
      runId: runId ?? null,
    });
  }

  private activateProjectWorkspace(submission: ProjectWizardSubmission): void {
    this.workspaceProject.set(submission);
    
    // Optionally save project to MongoDB to get a projectId
    // This allows workspace-view to fetch saved designs from backend
    this.saveProjectToBackend(submission);
    
    const prompt = submission.details.description?.trim().length
      ? submission.details.description
      : submission.details.name;
    this.workspacePrompt.set(prompt);
    const featureSpecs = submission.features.map((detail) => this.createFeatureFromDetail(detail));
    const storySpecs = submission.stories.map((story) => this.cloneStory(story));
    this.latestFeatures.set(featureSpecs.map((feature) => this.cloneFeature(feature)));
    this.resetAgent1Selections(this.latestFeatures());
    this.latestStories.set(storySpecs.map((story) => this.cloneStory(story)));
    this.resetAgent2Selections(this.latestStories());
    this.workspaceFeatures.set(featureSpecs.map((feature) => this.cloneFeature(feature)));
    this.workspaceStories.set(storySpecs.map((story) => this.cloneStory(story)));
    this.workspaceVisualization.set(null);
    this.workspaceMermaid.set('');
    this.workspaceMermaidUpdatedAt.set(null);
    this.workspaceMermaidSaveMessage.set(null);
    this.workspaceMermaidSaving.set(false);
    this.lastPrompt.set(prompt);
    this.clearMermaidDiagram();
    this.isWorkspaceMode.set(true);
    this.isChatting.set(true);
    this.setFullScreen(false);
    this.fetchMermaidAsset();
    if (featureSpecs.length) {
      this.agent1AwaitingDecision.set(false);
      this.agent1RunId.set(null);
      this.appendMessage({
        sender: 'assistant',
        agent: 'agent1',
        text: `Project ${submission.details?.name || 'Untitled'} captured ${featureSpecs.length} feature(s) and ${storySpecs.length} story(s).`,
        features: featureSpecs,
        stories: storySpecs.length ? storySpecs : undefined,
        runId: null,
      });
    }
    if (storySpecs.length) {
      this.agentStage.set('agent2');
      this.agent2AwaitingDecision.set(false);
      this.agent2RunId.set(null);
    }
    if (featureSpecs.length && storySpecs.length) {
      this.invokeAgent3(
        featureSpecs.map((feature) => this.cloneFeature(feature)),
        storySpecs.map((story) => this.cloneStory(story)),
      );
    }
  }

  private saveProjectToBackend(submission: ProjectWizardSubmission): void {
    // Save project to MongoDB to get a projectId
    // This is optional - workspace can work without it, but having it enables backend design fetching
    const prompt = submission.details.description?.trim().length
      ? submission.details.description
      : submission.details.name;
    
    const payload = {
      user_id: 'workspace-user', // Default user ID for workspace projects
      title: submission.details.name,
      prompt: prompt,
    };
    
    console.debug(`[app] Saving project to backend to get projectId: ${submission.details.name}`);
    
    this.http
      .post<{ id: string; user_id: string; title: string; prompt: string; status: string; created_at: string }>(
        `${this.backendUrl}/projects`,
        payload
      )
      .subscribe({
        next: (response) => {
          console.debug(`[app] Project saved to backend | projectId=${response.id}`);
          this.workspaceProjectId.set(response.id);
        },
        error: (error) => {
          console.warn(`[app] Failed to save project to backend (workspace will work without projectId):`, error);
          // Not critical - workspace can work without projectId using dynamic generation
          this.workspaceProjectId.set(null);
        },
      });
  }

  protected onProjectWizardCancel(): void {
    this.closeProjectWizard();
  }

  protected onProjectWizardComplete(payload: ProjectWizardSubmissionPayload): void {
    this.projectWizardSaving.set(true);
    this.projectWizardLastSubmission.set(payload.submission);
    this.uploadProjectFiles(payload.files, payload.submission);

    if (this.projectWizardCompletionTimer) {
      clearTimeout(this.projectWizardCompletionTimer);
    }

    this.projectWizardCompletionTimer = setTimeout(() => {
      this.activateProjectWorkspace(payload.submission);
      this.projectWizardSaving.set(false);
      this.closeProjectWizard();
      console.debug('[project-wizard:complete]', payload.submission);
    }, 850);
  }

  protected onProjectWizardRequestAI(details: ProjectWizardDetails): void {
    if (this.projectWizardAiLoading()) {
      return;
    }

    this.projectWizardAiLoading.set(true);
    if (this.projectWizardAiTimer) {
      clearTimeout(this.projectWizardAiTimer);
    }

    this.projectWizardAiTimer = setTimeout(() => {
      this.projectWizardAiLoading.set(false);
      const summary = this.composeWizardSummary(details);
      this.projectWizardSummaryDraft.set(summary);
    }, 900);
  }

  protected onProjectWizardRequestAISuggestion(event: {
    suggestionId: string;
    suggestionType: 'summary' | 'epics' | 'acceptanceCriteria' | 'stories';
    prompt: string;
    projectContext: {
      industry: string;
      methodology: string;
      name: string;
      description: string;
      focusAreas?: string[];
    };
  }): void {
    const payload: AISuggestionRequest = {
      suggestion_type: event.suggestionType,
      prompt: event.prompt,
      project_context: {
        industry: event.projectContext.industry,
        methodology: event.projectContext.methodology,
        name: event.projectContext.name,
        description: event.projectContext.description,
        focusAreas: event.projectContext.focusAreas,
      },
    };

    this.http
      .post<AISuggestionResponse>(`${this.backendUrl}/agent/suggestions`, payload)
      .subscribe({
        next: (response: AISuggestionResponse) => {
          this.projectWizardSuggestionResponse.set({
            suggestionId: event.suggestionId,
            output: response.output,
          });
          // Clear the response after a short delay to allow the component to process it
          setTimeout(() => {
            this.projectWizardSuggestionResponse.set(null);
          }, 100);
        },
        error: (error: unknown) => {
          console.error('[wizard:suggestion:error]', error);
          this.projectWizardSuggestionResponse.set({
            suggestionId: event.suggestionId,
            output: 'Error generating suggestion. Please try again.',
          });
          setTimeout(() => {
            this.projectWizardSuggestionResponse.set(null);
          }, 100);
        },
      });
  }

  protected onProjectWizardRequestFeatures(event: { details: ProjectWizardDetails; aiSummary: ProjectWizardAISummary }): void {
    if (this.projectWizardFeaturesLoading()) {
      return;
    }

    this.projectWizardFeaturesLoading.set(true);
    this.projectWizardFeatureRecommendations.set([]);
    this.projectWizardStoryRecommendations.set([]);
    const prompt = this.composeFeaturePrompt(event.details, event.aiSummary);
    const payload: AgentFeatureRequestPayload = { prompt };

    this.http
      .post<AgentFeatureResponse>(`${this.backendUrl}/agent/features`, payload)
      .subscribe({
        next: (response: AgentFeatureResponse) => {
          const specs = response.features ?? [];
          const details = specs.map((spec: AgentFeatureSpec, index: number) => this.createFeatureDetailFromSpec(spec, index));
          this.projectWizardFeatureRecommendations.set(details);
        },
        error: (error: unknown) => {
          console.error('[wizard:features:error]', error);
          this.projectWizardFeatureRecommendations.set([]);
          this.projectWizardFeaturesLoading.set(false);
        },
        complete: () => {
          this.projectWizardFeaturesLoading.set(false);
        },
      });
  }

  protected onProjectWizardRequestStories(event: {
    details: ProjectWizardDetails;
    aiSummary: ProjectWizardAISummary;
    features: AgentFeatureDetail[];
  }): void {
    if (this.projectWizardStoriesLoading()) {
      return;
    }
    if (!event.features.length) {
      this.projectWizardStoryRecommendations.set([]);
      return;
    }

    this.projectWizardStoriesLoading.set(true);
    this.projectWizardStoryRecommendations.set([]);
    const prompt = this.composeStoryPrompt(event.details, event.aiSummary, event.features);
    const features = event.features.map((detail) => this.createFeatureFromDetail(detail));
    const payload: AgentStoryRequestPayload = { prompt, features };

    this.http
      .post<AgentStoryResponse>(`${this.backendUrl}/agent/stories`, payload)
      .subscribe({
        next: (response: AgentStoryResponse) => {
          this.projectWizardStoryRecommendations.set(response.stories ?? []);
        },
        error: (error: unknown) => {
          console.error('[wizard:stories:error]', error);
          this.projectWizardStoryRecommendations.set([]);
          this.projectWizardStoriesLoading.set(false);
          // Error is logged but UI will show empty recommendations
          // User can retry or proceed with manual story creation
        },
        complete: () => {
          this.projectWizardStoriesLoading.set(false);
        },
      });
  }

  private closeProjectWizard(): void {
    this.cancelProjectWizardTimers();
    this.isProjectWizardOpen.set(false);
    this.projectWizardSaving.set(false);
    this.projectWizardAiLoading.set(false);
  }

  protected onProjectWizardStoryEdit(event: {
    featureIndex: number;
    storyIndex: number;
    story: AgentStorySpec;
    featureDetail: AgentFeatureDetail;
  }): void {
    this.openStoryForm(
      { scope: 'wizard', featureIndex: event.featureIndex, storyIndex: event.storyIndex },
      event.story,
      true,
    );
  }

  protected onProjectWizardStoryDismiss(_: { featureIndex: number; storyIndex: number }): void {
    // Wizard manages its own state; nothing additional needed at the app level yet.
  }

  private composeWizardSummary(details: ProjectWizardDetails): ProjectWizardAISummary {
    const trimmedDescription = details.description.trim();
    const sentences = trimmedDescription
      .split(/[.?!]/)
      .map((entry) => entry.trim())
      .filter((entry) => entry.length);

    const executiveSummary =
      sentences.slice(0, 2).join('. ') ||
      `Launch ${details.name} for the ${details.industry} space using a ${details.methodology} delivery model.`;

    const epicIdeas =
      sentences.slice(0, 3).map((line, index) => `Epic ${index + 1}: ${line}`) ||
      [
        `Epic 1: Customer onboarding excellence`,
        `Epic 2: Operational intelligence`,
        `Epic 3: Continuous compliance guardrails`,
      ];

    const riskNotes = [
      `${details.methodology === 'kanban' ? 'Flow' : 'Sprint'} discipline needs reinforcement across the team.`,
      details.teamSize && details.teamSize > 12
        ? 'Large team size requires clear ownership and coordination rituals.'
        : 'Ensure cross-functional representation to cover compliance, product, and engineering needs.',
      details.targetLaunch
        ? `Target launch on ${details.targetLaunch} assumes continuous stakeholder alignment.`
        : 'Target launch is unset—align on release milestones to manage expectations.',
    ];

    return {
      executiveSummary: executiveSummary.endsWith('.') ? executiveSummary : `${executiveSummary}.`,
      epicIdeas,
      riskNotes,
      customPrompt: '',
    };
  }

  private composeFeatureEnhancementPrompt(
    feature: AgentFeatureSpec,
    project: ProjectWizardSubmission | null,
  ): string {
    const detail = feature.detail ?? null;
    const lines: string[] = [
      'You are Agent_1 refining a single product feature for AutoAgents.',
    ];

    if (project) {
      lines.push(
        '',
        `Project Name: ${project.details.name}`,
        `Project Key: ${project.details.key}`,
        `Industry: ${project.details.industry}`,
        `Methodology: ${project.details.methodology}`,
        `Team Size: ${project.details.teamSize ?? 'Unspecified'}`,
        `Prompt Summary: ${project.details.description}`,
      );

      if (project.aiSummary.executiveSummary.trim().length) {
        lines.push('', `Executive Summary: ${project.aiSummary.executiveSummary.trim()}`);
      }
      if (project.aiSummary.epicIdeas.length) {
        lines.push('', 'Epic Ideas:');
        project.aiSummary.epicIdeas.forEach((idea, index) => lines.push(`${index + 1}. ${idea}`));
      }
      if (project.aiSummary.riskNotes.length) {
        lines.push('', 'Risk Highlights:');
        project.aiSummary.riskNotes.forEach((risk, index) => lines.push(`${index + 1}. ${risk}`));
      }
      if (project.aiSummary.customPrompt?.trim().length) {
        lines.push('', 'Product Owner Guidance:', project.aiSummary.customPrompt.trim());
      }
    }

    lines.push('', 'Current feature draft:');
    lines.push(`Title: ${feature.title}`);
    lines.push(`Description: ${feature.description}`);
    if (feature.acceptanceCriteria?.length) {
      lines.push('Acceptance Criteria:');
      feature.acceptanceCriteria.forEach((criterion, index) => lines.push(`${index + 1}. ${criterion}`));
    }

    if (detail) {
      lines.push(
        '',
        `Problem Statement: ${detail.problemStatement}`,
        `Business Objective: ${detail.businessObjective}`,
        `User Persona: ${detail.userPersona}`,
      );
      if (detail.successMetrics?.length) {
        lines.push(`Success Metrics: ${detail.successMetrics.join('; ')}`);
      }
      if (detail.stakeholders?.length) {
        lines.push(`Stakeholders: ${detail.stakeholders.join('; ')}`);
      }
      if (detail.dependencies?.length) {
        lines.push(`Dependencies: ${detail.dependencies.join('; ')}`);
      }
      if (detail.constraints?.length) {
        lines.push(`Constraints: ${detail.constraints.join('; ')}`);
      }
      if (detail.nonFunctionalRequirements?.length) {
        lines.push(`Non-functional Requirements: ${detail.nonFunctionalRequirements.join('; ')}`);
      }
      if (detail.risks?.length) {
        lines.push('Risks:');
        detail.risks.forEach((risk, index) => {
          const mitigation = risk.mitigation?.trim().length ? ` | Mitigation: ${risk.mitigation}` : '';
          lines.push(`${index + 1}. ${risk.description}${mitigation}`);
        });
      }
    }

    lines.push(
      '',
      'Refine this single feature into an implementation-ready brief.',
      'Return valid JSON with exactly one item in the "features" array, matching this schema:',
      '{',
      '  "summary": "contextual summary of this refinement",',
      '  "features": [',
      '    {',
      '      "title": "Refined feature title",',
      '      "description": "Improved description (2 sentences max)",',
      '      "acceptanceCriteria": ["Given ...", "When ...", "Then ..."]',
      '    }',
      '  ]',
      '}',
      'Ensure acceptance criteria remain specific and testable (3-5 items). Adjust naming only if it improves clarity.',
    );

    return lines.join('\n');
  }

  private composeFeaturePrompt(details: ProjectWizardDetails, aiSummary: ProjectWizardAISummary): string {
    const lines: string[] = [
      `Project Name: ${details.name}`,
      `Project Key: ${details.key}`,
      `Industry: ${details.industry}`,
      `Methodology: ${details.methodology}`,
      `Team Size: ${details.teamSize ?? 'Unspecified'}`,
      `Timezone: ${details.timezone}`,
      `Kick-off: ${details.startDate ?? 'Not set'}`,
      `Target Launch: ${details.targetLaunch ?? 'Not set'}`,
      '',
      `Prompt Summary: ${details.description}`,
      '',
      `Executive Summary: ${aiSummary.executiveSummary}`,
    ];

    if (aiSummary.epicIdeas.length) {
      lines.push('', 'Epic Ideas:');
      aiSummary.epicIdeas.forEach((idea, index) => lines.push(`${index + 1}. ${idea}`));
    }

    if (aiSummary.riskNotes.length) {
      lines.push('', 'Risk Highlights:');
      aiSummary.riskNotes.forEach((risk, index) => lines.push(`${index + 1}. ${risk}`));
    }

    if (aiSummary.customPrompt.trim().length) {
      lines.push('', 'Product Owner Guidance:', aiSummary.customPrompt.trim());
    }

    lines.push('', 'Return valid JSON per the agreed schema.');
    lines.push(
      'Ensure the "features" array contains at least eight distinct items (add more if the scope warrants) covering onboarding, core workflows, administration/compliance, analytics/reporting, integrations/extensibility, and forward-looking innovations.',
    );
    lines.push(
      'Each feature entry must include a concise title, tailored description, and three to five acceptance criteria aligned to this project.',
    );
    return lines.join('\n');
  }

  private composeStoryEnhancementPrompt(
    feature: AgentFeatureSpec | AgentFeatureDetail,
    story: AgentStorySpec,
    project: ProjectWizardSubmission | null,
  ): string {
    let featureSummary: string;
    let featureDescription: string;
    let detail: AgentFeatureDetail | null;

    if ('summary' in feature && 'problemStatement' in feature) {
      featureSummary = feature.summary;
      featureDescription = feature.description;
      detail = feature;
    } else {
      const spec = feature as AgentFeatureSpec;
      featureSummary = spec.title ?? spec.detail?.summary ?? '';
      featureDescription = spec.description ?? spec.detail?.description ?? '';
      detail = spec.detail ?? null;
    }

    const lines: string[] = ['You are Agent_2 refining a single user story for AutoAgents.'];

    if (project) {
      lines.push(
        '',
        `Project Name: ${project.details.name}`,
        `Industry: ${project.details.industry}`,
        `Executive Summary: ${project.aiSummary.executiveSummary}`,
      );
      if (project.aiSummary.customPrompt?.trim().length) {
        lines.push('Product Owner Guidance:', project.aiSummary.customPrompt.trim());
      }
    }

    lines.push(
      '',
      `Feature: ${featureSummary}`,
      `Feature Description: ${featureDescription}`,
    );

    if (detail && 'problemStatement' in detail) {
      lines.push(
        `Problem Statement: ${detail.problemStatement}`,
        `Business Objective: ${detail.businessObjective}`,
        `User Persona: ${detail.userPersona}`,
      );
    }

    lines.push(
      '',
      'Current story draft to refine:',
      `User Story: ${story.userStory}`,
      `Acceptance Criteria: ${story.acceptanceCriteria.join(' | ') || 'None provided'}`,
      `Implementation Notes: ${story.implementationNotes.join(' | ') || 'None provided'}`,
    );

    lines.push(
      '',
      'Refine this story into a concise, testable user story with architecture-aware acceptance criteria and implementation notes at low to medium level of detail.',
      'Return valid JSON with this schema:',
      '{',
      '  "summary": "short summary",',
      '  "stories": [',
      '    {',
      '      "featureTitle": "Name of the feature",',
      '      "userStory": "As a ...",',
      '      "acceptanceCriteria": ["Given ...", "When ...", "Then ..."],',
      '      "implementationNotes": ["Step or component", "..."]',
      '    }',
      '  ]',
      '}',
      'Ensure the acceptance criteria cover architectural concerns (auth, data, integrations) at low and medium levels, and produce between three and five criteria.',
    );

    return lines.join('\n');
  }

  private composeStoryPrompt(
    details: ProjectWizardDetails,
    aiSummary: ProjectWizardAISummary,
    features: AgentFeatureDetail[],
  ): string {
    const lines: string[] = [
      `Project Name: ${details.name}`,
      `Project Key: ${details.key}`,
      `Executive Summary: ${aiSummary.executiveSummary}`,
      '',
      'Approved Features:',
    ];

    features.forEach((feature, index) => {
      lines.push(
        `${index + 1}. ${feature.summary}`,
        `   Problem: ${feature.problemStatement}`,
        `   Business Objective: ${feature.businessObjective}`,
        `   Acceptance Criteria: ${feature.acceptanceCriteria.join('; ') || 'Pending'}`,
        '',
      );
    });

    if (aiSummary.customPrompt.trim().length) {
      lines.push('Product Owner Guidance:', aiSummary.customPrompt.trim(), '');
    }

    lines.push(
      'For each feature above, generate the set of user stories needed to deliver the capability end-to-end. Prioritise low- and medium-level architectural considerations, and include acceptance criteria plus implementation notes for every story.',
    );
    return lines.join('\n');
  }

  private cancelProjectWizardTimers(): void {
    if (this.projectWizardCompletionTimer) {
      clearTimeout(this.projectWizardCompletionTimer);
      this.projectWizardCompletionTimer = null;
    }
    if (this.projectWizardAiTimer) {
      clearTimeout(this.projectWizardAiTimer);
      this.projectWizardAiTimer = null;
    }
  }

  private cancelFeatureFormTimer(): void {
    if (this.featureFormTimer) {
      clearTimeout(this.featureFormTimer);
      this.featureFormTimer = null;
    }
  }

  private uploadFeatureFiles(files: File[], detail: AgentFeatureDetail): void {
    if (!files.length) {
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file, file.name));
    formData.append('featureKey', detail.key || this.createDefaultKey(detail.summary));
    formData.append('summary', detail.summary);

    this.http
      .post(`${this.backendUrl}/uploads/features`, formData)
      .subscribe({
        next: (response) => console.debug('[feature-upload:success]', response),
        error: (error) => console.error('[feature-upload:error]', error),
      });
  }

  private uploadProjectFiles(files: File[], submission: ProjectWizardSubmission): void {
    if (!files.length) {
      return;
    }

    const formData = new FormData();
    files.forEach((file) => formData.append('files', file, file.name));
    formData.append('projectKey', submission.details.key || this.createDefaultKey(submission.details.name));
    formData.append('projectName', submission.details.name);
    formData.append('runId', submission.templateId ?? '');

    this.http
      .post(`${this.backendUrl}/uploads/projects`, formData)
      .subscribe({
        next: (response) => console.debug('[project-upload:success]', response),
        error: (error) => console.error('[project-upload:error]', error),
      });
  }

  private createDefaultKey(seed: string): string {
    const sanitized = seed.trim().toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (!sanitized) {
      return `ITEM-${Date.now()}`;
    }
    return sanitized.slice(0, 8);
  }

  protected onWorkspaceMermaidChange(definition: string): void {
    this.workspaceMermaid.set(definition);
    this.workspaceMermaidSaveMessage.set('Unsaved changes');
  }

  protected onWorkspaceMermaidSave(definition: string): void {
    this.workspaceMermaidSaving.set(true);
    this.workspaceMermaidSaveMessage.set(null);

    const payload: MermaidAssetUpdatePayload = { mermaid: definition };

    this.http
      .post<MermaidAssetResponse>(`${this.backendUrl}/agent/visualizer/mermaid`, payload)
      .subscribe({
        next: (response: MermaidAssetResponse) => {
          const mermaid = response?.mermaid ?? definition;
          this.workspaceMermaid.set(mermaid);
          this.workspaceMermaidUpdatedAt.set(response?.updatedAt ?? null);
          this.workspaceMermaidSaveMessage.set('Mermaid diagram saved.');
          this.mermaidChatInput.set(mermaid);
          this.renderChatMermaid();
        },
        error: (error: unknown) => {
          console.error('[mermaid:save:error]', error);
          this.workspaceMermaidSaveMessage.set('Failed to save Mermaid diagram.');
        },
        complete: () => {
          this.workspaceMermaidSaving.set(false);
        },
      });
  }

  protected onWorkspaceDiagramTypeChange(diagramType: string): void {
    // Regenerate diagram with new type when user switches
    const features = this.workspaceFeatures();
    const stories = this.workspaceStories();
    
    console.debug(`[app] Diagram type changed to ${diagramType} | features=${features.length} | stories=${stories.length}`);
    
    if (features.length && stories.length) {
      console.debug(`[app] Invoking Agent 3 to generate ${diagramType.toUpperCase()} diagram`);
      this.invokeAgent3(features, stories, diagramType);
    } else {
      console.warn(`[app] Cannot generate ${diagramType.toUpperCase()} diagram: missing features (${features.length}) or stories (${stories.length})`);
      // Show user-friendly message
      this.workspaceMermaidSaveMessage.set(
        `Cannot generate ${diagramType.toUpperCase()} diagram: Need at least 1 feature and 1 story. ` +
        `Current: ${features.length} feature(s), ${stories.length} story(s).`
      );
    }
  }

  protected onWorkspaceRegenerateDiagram(diagramType: string): void {
    // Regenerate diagram with current features and stories
    const features = this.workspaceFeatures();
    const stories = this.workspaceStories();
    
    console.debug(`[app] Regenerating ${diagramType.toUpperCase()} diagram | features=${features.length} | stories=${stories.length}`);
    
    if (features.length && stories.length) {
      console.debug(`[app] Invoking Agent 3 to regenerate ${diagramType.toUpperCase()} diagram`);
      this.invokeAgent3(features, stories, diagramType);
    } else {
      console.warn(`[app] Cannot regenerate ${diagramType.toUpperCase()} diagram: missing features (${features.length}) or stories (${stories.length})`);
      // Show user-friendly message
      this.workspaceMermaidSaveMessage.set(
        `Cannot regenerate ${diagramType.toUpperCase()} diagram: Need at least 1 feature and 1 story. ` +
        `Current: ${features.length} feature(s), ${stories.length} story(s).`
      );
    }
  }

  protected workspaceMermaidUpdatedLabel(): string | null {
    const iso = this.workspaceMermaidUpdatedAt();
    if (!iso) {
      return null;
    }
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  }

  private fetchMermaidAsset(): void {
    this.http
      .get<MermaidAssetResponse>(`${this.backendUrl}/agent/visualizer/mermaid`)
      .subscribe({
        next: (response: MermaidAssetResponse) => {
          if (typeof response?.mermaid === 'string' && response.mermaid.trim().length) {
            this.workspaceMermaid.set(response.mermaid);
            this.workspaceMermaidUpdatedAt.set(response.updatedAt ?? null);
            this.workspaceMermaidSaveMessage.set(null);
          }
        },
        error: (error: unknown) => {
          console.error('[mermaid:fetch:error]', error);
        },
      });
  }

  protected onFeatureRegenerated(regeneratedContent: any, messageIdx: number, featureIdx: number): void {
    console.debug('[App] Feature regenerated', { messageIdx, featureIdx, regeneratedContent });
    
    // Update the feature in the message
    this.chatMessages.update((messages) => {
      const updated = [...messages];
      if (updated[messageIdx] && updated[messageIdx].features) {
        const features = [...updated[messageIdx].features!];
        if (features[featureIdx]) {
          features[featureIdx] = {
            ...features[featureIdx],
            ...regeneratedContent,
          };
          updated[messageIdx] = {
            ...updated[messageIdx],
            features,
          };
        }
      }
      return updated;
    });

    // Update latestFeatures if this is the latest message
    const latestMessage = this.chatMessages()[this.chatMessages().length - 1];
    if (latestMessage && latestMessage.features && latestMessage.features[featureIdx]) {
      this.latestFeatures.update((features) => {
        const updated = [...features];
        // Find matching feature by title or index
        if (updated[featureIdx]) {
          updated[featureIdx] = {
            ...updated[featureIdx],
            ...regeneratedContent,
          };
        }
        return updated;
      });
      this.resetAgent1Selections(this.latestFeatures());
    }
  }

  protected onStoryRegenerated(regeneratedContent: any, messageIdx: number, storyIdx: number): void {
    console.debug('[App] Story regenerated', { messageIdx, storyIdx, regeneratedContent });
    
    // Update the story in the message
    this.chatMessages.update((messages) => {
      const updated = [...messages];
      if (updated[messageIdx] && updated[messageIdx].stories) {
        const stories = [...updated[messageIdx].stories!];
        if (stories[storyIdx]) {
          stories[storyIdx] = {
            ...stories[storyIdx],
            ...regeneratedContent,
          };
          updated[messageIdx] = {
            ...updated[messageIdx],
            stories,
          };
        }
      }
      return updated;
    });

    // Update latestStories if this is the latest message
    const latestMessage = this.chatMessages()[this.chatMessages().length - 1];
    if (latestMessage && latestMessage.stories && latestMessage.stories[storyIdx]) {
      this.latestStories.update((stories) => {
        const updated = [...stories];
        // Find matching story by featureTitle or index
        if (updated[storyIdx]) {
          updated[storyIdx] = {
            ...updated[storyIdx],
            ...regeneratedContent,
          };
        }
        return updated;
      });
      this.resetAgent2Selections(this.latestStories());
    }
  }

  protected onFeedbackError(error: string): void {
    console.error('[App] Feedback error', { error });
    // Could show a toast notification here
  }
}
