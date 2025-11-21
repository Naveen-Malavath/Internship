import { CommonModule } from '@angular/common';
import {
  Component,
  Input,
  Output,
  EventEmitter,
  OnInit,
  OnDestroy,
  signal,
  computed,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { FeedbackService } from '../services/feedback.service';
import { FeedbackRequest, FeedbackResponse, FeedbackHistoryEntry } from '../types';

@Component({
  selector: 'feedback-chatbot',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './feedback-chatbot.component.html',
  styleUrl: './feedback-chatbot.component.scss',
})
export class FeedbackChatbotComponent implements OnInit, OnDestroy {
  @Input() itemId: string = '';
  @Input() itemType: 'feature' | 'story' | 'visualization' = 'feature';
  @Input() projectId: string = '';
  @Input() originalContent: any = null; // Original feature/story/visualization data
  @Input() projectContext: string = ''; // Original project prompt
  @Output() contentRegenerated = new EventEmitter<any>();
  @Output() errorOccurred = new EventEmitter<string>();

  // State management
  feedbackText = signal<string>('');
  isSubmitting = signal<boolean>(false);
  isRegenerating = signal<boolean>(false);
  errorMessage = signal<string | null>(null);
  successMessage = signal<string | null>(null);
  regenerationCount = signal<number>(0);
  feedbackHistory = signal<FeedbackHistoryEntry[]>([]);
  currentVersion = signal<number>(0);
  previousVersions = signal<any[]>([]);
  isExpanded = signal<boolean>(false);
  isHistoryExpanded = signal<boolean>(false);
  private readonly REGENERATION_TIMEOUT = 60000; // 60 seconds
  private regenerationTimeoutId: ReturnType<typeof setTimeout> | null = null;

  constructor(private feedbackService: FeedbackService) {
    console.debug('[FeedbackChatbot] Component initialized', {
      itemId: this.itemId,
      itemType: this.itemType,
      projectId: this.projectId,
    });
  }

  ngOnInit(): void {
    console.debug('[FeedbackChatbot] ngOnInit called', {
      itemId: this.itemId,
      itemType: this.itemType,
    });
    this.loadFeedbackHistory();
    this.loadRegenerationCount();
  }

  ngOnDestroy(): void {
    console.debug('[FeedbackChatbot] ngOnDestroy called');
    if (this.regenerationTimeoutId) {
      clearTimeout(this.regenerationTimeoutId);
    }
  }

  async onSubmitFeedback(): Promise<void> {
    const feedback = this.feedbackText().trim();
    if (!feedback) {
      this.errorMessage.set('Please provide feedback before submitting.');
      console.warn('[FeedbackChatbot] Empty feedback submission attempted');
      return;
    }

    if (this.isSubmitting()) {
      console.warn('[FeedbackChatbot] Submission already in progress');
      return;
    }

    console.debug('[FeedbackChatbot] Submitting feedback', {
      itemId: this.itemId,
      itemType: this.itemType,
      feedbackLength: feedback.length,
    });

    this.isSubmitting.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    try {
      const request: FeedbackRequest = {
        itemId: this.itemId,
        itemType: this.itemType,
        projectId: this.projectId,
        feedback: feedback,
        originalContent: this.originalContent,
        projectContext: this.projectContext,
      };

      console.debug('[FeedbackChatbot] Feedback request prepared', {
        itemId: request.itemId,
        itemType: request.itemType,
        hasOriginalContent: !!request.originalContent,
        hasProjectContext: !!request.projectContext,
      });

      const response = await this.feedbackService.submitFeedback(request).toPromise();

      if (response) {
        console.debug('[FeedbackChatbot] Feedback submitted successfully', {
          feedbackId: response.feedbackId,
          regenerationCount: response.regenerationCount,
        });

        this.successMessage.set('Feedback submitted successfully!');
        this.feedbackText.set('');
        this.regenerationCount.set(response.regenerationCount);

        // Add to history
        const historyEntry: FeedbackHistoryEntry = {
          id: response.feedbackId,
          itemId: this.itemId,
          itemType: this.itemType,
          feedback: feedback,
          timestamp: new Date().toISOString(),
          status: 'submitted',
        };
        this.feedbackHistory.update((history) => [historyEntry, ...history]);

        // Auto-regenerate if requested
        if (response.autoRegenerate) {
          await this.regenerateContent();
        }
      }
    } catch (error: any) {
      console.error('[FeedbackChatbot] Error submitting feedback', error);
      const errorMsg =
        error?.error?.message ||
        error?.message ||
        'Failed to submit feedback. Please try again.';
      this.errorMessage.set(errorMsg);
      this.errorOccurred.emit(errorMsg);
    } finally {
      this.isSubmitting.set(false);
    }
  }

  async regenerateContent(): Promise<void> {
    if (this.isRegenerating()) {
      console.warn('[FeedbackChatbot] Regeneration already in progress');
      return;
    }

    console.debug('[FeedbackChatbot] Starting content regeneration', {
      itemId: this.itemId,
      itemType: this.itemType,
      currentVersion: this.currentVersion(),
    });

    this.isRegenerating.set(true);
    this.errorMessage.set(null);
    this.successMessage.set(null);

    // Set timeout for regeneration
    this.regenerationTimeoutId = setTimeout(() => {
      if (this.isRegenerating()) {
        console.error('[FeedbackChatbot] Regeneration timeout exceeded', {
          timeout: this.REGENERATION_TIMEOUT,
        });
        this.isRegenerating.set(false);
        this.errorMessage.set(
          'Regeneration is taking longer than expected. Please try again or contact support.'
        );
        this.errorOccurred.emit('Regeneration timeout');
      }
    }, this.REGENERATION_TIMEOUT);

    try {
      // Save current version before regenerating
      if (this.originalContent) {
        this.previousVersions.update((versions) => [
          { ...this.originalContent, version: this.currentVersion() },
          ...versions,
        ]);
      }

      const request: FeedbackRequest = {
        itemId: this.itemId,
        itemType: this.itemType,
        projectId: this.projectId,
        feedback: this.feedbackHistory()[0]?.feedback || '',
        originalContent: this.originalContent,
        projectContext: this.projectContext,
        regenerate: true,
      };

      console.debug('[FeedbackChatbot] Regeneration request prepared', {
        itemId: request.itemId,
        itemType: request.itemType,
        hasFeedback: !!request.feedback,
      });

      const response = await this.feedbackService
        .regenerateContent(request)
        .toPromise();

      if (response) {
        console.debug('[FeedbackChatbot] Content regenerated successfully', {
          newContent: response.regeneratedContent,
          version: response.version,
        });

        // Update state
        this.currentVersion.update((v) => v + 1);
        this.regenerationCount.set(response.regenerationCount);
        this.originalContent = response.regeneratedContent;

        // Update history
        if (this.feedbackHistory().length > 0) {
          this.feedbackHistory.update((history) => {
            const updated = [...history];
            if (updated[0]) {
              updated[0] = {
                ...updated[0],
                status: 'regenerated',
                regeneratedAt: new Date().toISOString(),
              };
            }
            return updated;
          });
        }

        this.successMessage.set('Content regenerated successfully!');
        this.contentRegenerated.emit(response.regeneratedContent);

        // Clear timeout
        if (this.regenerationTimeoutId) {
          clearTimeout(this.regenerationTimeoutId);
          this.regenerationTimeoutId = null;
        }
      }
    } catch (error: any) {
      console.error('[FeedbackChatbot] Error regenerating content', error);

      // Clear timeout
      if (this.regenerationTimeoutId) {
        clearTimeout(this.regenerationTimeoutId);
        this.regenerationTimeoutId = null;
      }

      let errorMsg = 'Failed to regenerate content. Please try again.';
      if (error?.error?.code === 'LLM_FAILURE') {
        errorMsg =
          'The AI service encountered an error. Please try again in a moment.';
      } else if (error?.error?.message) {
        errorMsg = error.error.message;
      } else if (error?.message) {
        errorMsg = error.message;
      }

      this.errorMessage.set(errorMsg);
      this.errorOccurred.emit(errorMsg);
    } finally {
      this.isRegenerating.set(false);
    }
  }

  async undoLastRegeneration(): Promise<void> {
    if (this.previousVersions().length === 0) {
      this.errorMessage.set('No previous version available to restore.');
      console.warn('[FeedbackChatbot] No previous version to undo');
      return;
    }

    console.debug('[FeedbackChatbot] Undoing last regeneration', {
      previousVersionsCount: this.previousVersions().length,
    });

    const previousVersion = this.previousVersions()[0];
    this.originalContent = previousVersion;
    this.previousVersions.update((versions) => versions.slice(1));
    this.currentVersion.update((v) => Math.max(0, v - 1));

    this.successMessage.set('Previous version restored.');
    this.contentRegenerated.emit(previousVersion);

    console.debug('[FeedbackChatbot] Undo completed', {
      restoredVersion: this.currentVersion(),
    });
  }

  private async loadFeedbackHistory(): Promise<void> {
    try {
      console.debug('[FeedbackChatbot] Loading feedback history', {
        itemId: this.itemId,
        itemType: this.itemType,
      });

      const history = await this.feedbackService
        .getFeedbackHistory(this.itemId, this.itemType)
        .toPromise();

      if (history) {
        this.feedbackHistory.set(history);
        console.debug('[FeedbackChatbot] Feedback history loaded', {
          count: history.length,
        });
      }
    } catch (error) {
      console.error('[FeedbackChatbot] Error loading feedback history', error);
      // Don't show error to user, just log it
    }
  }

  private async loadRegenerationCount(): Promise<void> {
    try {
      console.debug('[FeedbackChatbot] Loading regeneration count', {
        itemId: this.itemId,
        itemType: this.itemType,
      });

      const count = await this.feedbackService
        .getRegenerationCount(this.itemId, this.itemType)
        .toPromise();

      if (count !== undefined) {
        this.regenerationCount.set(count);
        console.debug('[FeedbackChatbot] Regeneration count loaded', {
          count: count,
        });
      }
    } catch (error) {
      console.error('[FeedbackChatbot] Error loading regeneration count', error);
      // Don't show error to user, just log it
    }
  }

  clearMessages(): void {
    this.errorMessage.set(null);
    this.successMessage.set(null);
  }

  toggleExpanded(): void {
    this.isExpanded.update(value => !value);
    if (!this.isExpanded()) {
      this.isHistoryExpanded.set(false);
    }
  }

  toggleHistory(): void {
    this.isHistoryExpanded.update(value => !value);
  }
}

