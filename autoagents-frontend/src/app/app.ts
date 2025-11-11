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

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, WorkspaceViewComponent, ProjectWizardComponent, FeatureFormComponent],
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
  protected readonly mermaidChatInput = signal('');
  protected readonly mermaidChatError = signal<string | null>(null);
  protected readonly workspaceProject = signal<ProjectWizardSubmission | null>(null);
  protected readonly isProjectWizardOpen = signal(false);
  protected readonly projectWizardSaving = signal(false);
  protected readonly projectWizardAiLoading = signal(false);
  protected readonly projectWizardSummaryDraft = signal<ProjectWizardAISummary | null>(null);
  protected readonly projectWizardLastSubmission = signal<ProjectWizardSubmission | null>(null);

  protected readonly projectWizardTemplates = PROJECT_TEMPLATES;
  protected readonly projectWizardWorkflows = PROJECT_WORKFLOWS;
  protected readonly projectWizardTimezones = PROJECT_TIMEZONES;
  protected readonly projectWizardTeamSizes = PROJECT_TEAM_SIZES;
  protected readonly isFeatureFormOpen = signal(false);
  protected readonly featureFormSaving = signal(false);
  protected readonly featureFormDraft = signal<AgentFeatureDetail | null>(null);
  protected readonly projectWizardFeatureRecommendations = signal<AgentFeatureDetail[]>([]);
  protected readonly projectWizardStoryRecommendations = signal<AgentStorySpec[]>([]);
  protected readonly projectWizardFeaturesLoading = signal(false);
  protected readonly projectWizardStoriesLoading = signal(false);

  @ViewChild('chatMermaidContainer') private chatMermaidContainer?: ElementRef<HTMLDivElement>;

  private readonly http = inject(HttpClient);
  private mermaidChatInitialised = false;
  private mermaidChatRenderIndex = 0;
  private projectWizardCompletionTimer: ReturnType<typeof setTimeout> | null = null;
  private projectWizardAiTimer: ReturnType<typeof setTimeout> | null = null;
  private featureFormTimer: ReturnType<typeof setTimeout> | null = null;

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
    this.latestStories.set([]);
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
    this.latestStories.set([]);
    this.chatInput.set('');
    this.workspaceVisualization.set(null);
    this.workspaceMermaid.set('');
    this.workspaceProject.set(null);
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
    this.latestStories.set(session.latestStories.map((story: AgentStorySpec) => this.cloneStory(story)));
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
    this.latestStories.set([]);
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

    const featuresSnapshot =
      decision === 'keep' || decision === 'keep_all'
        ? this.latestFeatures().map((feature: AgentFeatureSpec) => this.cloneFeature(feature))
        : undefined;

    if ((decision === 'keep' || decision === 'keep_all') && (!featuresSnapshot || !featuresSnapshot.length)) {
      console.warn('[agent1:keep] No features available to store.');
      return;
    }

    if (featuresSnapshot) {
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
            this.agent1RunId.set(response.run_id);
            this.agent1AwaitingDecision.set(true);
            this.clearMermaidDiagram();
          } else {
            this.agent1RunId.set(null);
            this.agent1AwaitingDecision.set(false);
            this.latestFeatures.set(featuresSnapshot ?? []);
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

    const stories = this.latestStories();
    if (decision === 'keep') {
      if (!this.agent2RunId()) {
        console.warn('[agent2:keep] Missing run id to approve.');
        return;
      }
      if (!stories.length) {
        console.warn('[agent2:keep] No stories captured to approve.');
        return;
      }
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
            this.latestStories.set(
              storiesResponse.map((story: AgentStorySpec) => ({
                ...story,
                acceptanceCriteria: [...story.acceptanceCriteria],
                implementationNotes: [...story.implementationNotes],
              })),
            );
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

  private invokeAgent3(features: AgentFeatureSpec[], stories: AgentStorySpec[]): void {
    if (!features.length || !stories.length) {
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
    };

    this.http
      .post<AgentVisualizationResponse>(`${this.backendUrl}/agent/visualizer`, payload)
      .subscribe({
        next: (response: AgentVisualizationResponse) => {
          this.workspaceVisualization.set(response);
          this.workspaceMermaid.set(response.diagrams?.mermaid ?? '');
          this.workspaceMermaidUpdatedAt.set(response.diagrams?.mermaidUpdatedAt ?? null);
          this.workspaceMermaidSaveMessage.set('Diagram generated by Agent 3.');
          this.mermaidChatInput.set(response.diagrams?.mermaid ?? '');
          this.renderChatMermaid();
        },
        error: (error: unknown) => {
          console.error('[agent3:error]', error);
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
    this.isFeatureFormOpen.set(true);
    this.featureFormDraft.set(null);
  }

  protected onFeatureFormCancel(): void {
    this.isFeatureFormOpen.set(false);
    this.cancelFeatureFormTimer();
    this.featureFormSaving.set(false);
  }

  protected onFeatureFormSubmit(submission: FeatureFormSubmission): void {
    if (this.featureFormSaving()) {
      return;
    }

    this.featureFormSaving.set(true);
    this.featureFormDraft.set(submission.detail);

    this.cancelFeatureFormTimer();
    this.featureFormTimer = setTimeout(() => {
      const feature = this.createFeatureFromDetail(submission.detail);
      this.latestFeatures.update((features: AgentFeatureSpec[]) => [...features, feature]);
      if (this.isWorkspaceMode()) {
        this.workspaceFeatures.update((features: AgentFeatureSpec[]) => [
          ...features,
          this.cloneFeature(feature),
        ]);
      }

      this.appendMessage({
        sender: 'assistant',
        agent: 'agent1',
        text: `Manual feature captured: ${submission.detail.summary}`,
        features: [feature],
        runId: null,
      });
      this.uploadFeatureFiles(submission.files, submission.detail);

      this.featureFormSaving.set(false);
      this.isFeatureFormOpen.set(false);
      this.featureFormDraft.set(null);
    }, 650);
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

  private activateProjectWorkspace(submission: ProjectWizardSubmission): void {
    this.workspaceProject.set(submission);
    const prompt = submission.details.description?.trim().length
      ? submission.details.description
      : submission.details.name;
    this.workspacePrompt.set(prompt);
    const featureSpecs = submission.features.map((detail) => this.createFeatureFromDetail(detail));
    const storySpecs = submission.stories.map((story) => this.cloneStory(story));
    this.latestFeatures.set(featureSpecs.map((feature) => this.cloneFeature(feature)));
    this.latestStories.set(storySpecs.map((story) => this.cloneStory(story)));
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
        text: `Project ${submission.details.name} captured ${featureSpecs.length} feature(s) and ${storySpecs.length} story(s).`,
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
    };
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
      `Elevator Pitch: ${details.description}`,
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

    lines.push('', 'Generate 3-5 detailed product features with acceptance criteria tailored to this project.');
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

    lines.push(
      'For each feature above, generate a high quality user story with acceptance criteria and implementation notes.',
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
}
