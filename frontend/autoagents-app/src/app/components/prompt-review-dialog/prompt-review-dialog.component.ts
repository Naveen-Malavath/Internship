import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

export interface PromptReviewDialogData {
  prompt: string;
}

@Component({
  selector: 'app-prompt-review-dialog',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule,
    MatDialogModule, 
    MatButtonModule, 
    MatIconModule
  ],
  template: `
    <div class="prompt-review-container">
      <div class="dialog-header">
        <div>
          <h2 class="dialog-title">Review Final Prompt</h2>
          <p class="dialog-subtitle">Review and edit the prompt that will be sent to the AI model</p>
        </div>
        <button mat-icon-button [mat-dialog-close]="null" class="close-button">
          <mat-icon>close</mat-icon>
        </button>
      </div>

      <div class="dialog-content">
        <div class="prompt-editor">
          <textarea 
            class="prompt-textarea" 
            [(ngModel)]="editablePrompt"
            placeholder="Generated prompt will appear here..."></textarea>
          <div class="prompt-info">
            <span class="char-count">{{ editablePrompt.length }} characters</span>
          </div>
        </div>
      </div>

      <div class="dialog-footer">
        <button mat-button [mat-dialog-close]="null" class="cancel-button">
          Cancel
        </button>
        <button 
          mat-raised-button 
          class="proceed-button" 
          (click)="onProceed()"
          [disabled]="!editablePrompt.trim()">
          <mat-icon>send</mat-icon>
          Proceed to Features
        </button>
      </div>
    </div>
  `,
  styles: [`
    .prompt-review-container {
      background: linear-gradient(135deg, #0f1429 0%, #1a2137 50%, #0f1429 100%);
      border-radius: 1rem;
      width: 800px;
      max-width: 90vw;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      color: #ffffff;
    }

    .dialog-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 2rem 2.5rem 1.5rem;
      border-bottom: 1px solid rgba(71, 85, 105, 0.2);
    }

    .dialog-title {
      font-size: 1.75rem;
      font-weight: 700;
      margin: 0 0 0.5rem 0;
      color: #ffffff;
    }

    .dialog-subtitle {
      font-size: 0.9375rem;
      color: #94a3b8;
      margin: 0;
    }

    .close-button {
      color: #94a3b8;
      margin-top: -0.5rem;
      
      &:hover {
        color: #ffffff;
      }
    }

    .dialog-content {
      flex: 1;
      overflow-y: auto;
      padding: 2rem 2.5rem;
      
      /* Custom scrollbar */
      &::-webkit-scrollbar {
        width: 10px;
      }
      
      &::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: rgba(71, 85, 105, 0.6);
        border-radius: 10px;
        
        &:hover {
          background: rgba(71, 85, 105, 0.8);
        }
      }
    }

    .prompt-editor {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .prompt-textarea {
      width: 100%;
      min-height: 400px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(71, 85, 105, 0.5);
      border-radius: 0.75rem;
      padding: 1.25rem;
      color: #e2e8f0;
      font-family: 'Courier New', monospace;
      font-size: 0.875rem;
      line-height: 1.7;
      resize: vertical;
      white-space: pre-wrap;
      word-wrap: break-word;
      
      &:focus {
        outline: none;
        border-color: rgba(59, 130, 246, 0.6);
        background: rgba(15, 23, 42, 0.95);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
      }
      
      &::placeholder {
        color: #64748b;
      }
      
      /* Custom scrollbar for textarea */
      &::-webkit-scrollbar {
        width: 10px;
      }
      
      &::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 5px;
      }
      
      &::-webkit-scrollbar-thumb {
        background: rgba(71, 85, 105, 0.6);
        border-radius: 5px;
        
        &:hover {
          background: rgba(71, 85, 105, 0.8);
        }
      }
    }

    .prompt-info {
      display: flex;
      justify-content: flex-end;
    }

    .char-count {
      font-size: 0.875rem;
      color: #64748b;
      font-weight: 500;
    }

    .dialog-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem 2.5rem;
      border-top: 1px solid rgba(71, 85, 105, 0.2);
    }

    .cancel-button {
      color: #94a3b8;
      
      &:hover {
        color: #ffffff;
        background: rgba(71, 85, 105, 0.2);
      }
    }

    .proceed-button {
      display: inline-flex;
      align-items: center;
      gap: 0.625rem;
      padding: 0.75rem 2rem;
      background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
      color: #ffffff;
      font-size: 1rem;
      font-weight: 600;
      border-radius: 0.5rem;
      transition: all 0.3s ease;
      box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
      
      &:hover:not(:disabled) {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        box-shadow: 0 8px 20px rgba(59, 130, 246, 0.5);
        transform: translateY(-2px);
      }
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
      }
      
      mat-icon {
        font-size: 1.25rem;
        width: 1.25rem;
        height: 1.25rem;
      }
    }

    @media (max-width: 768px) {
      .prompt-review-container {
        width: 95vw;
      }
      
      .dialog-header,
      .dialog-content,
      .dialog-footer {
        padding-left: 1.5rem;
        padding-right: 1.5rem;
      }
      
      .dialog-title {
        font-size: 1.5rem;
      }
      
      .prompt-textarea {
        min-height: 300px;
        font-size: 0.8125rem;
      }
    }
  `]
})
export class PromptReviewDialogComponent {
  editablePrompt: string;

  constructor(
    @Inject(MAT_DIALOG_DATA) public data: PromptReviewDialogData,
    private dialogRef: MatDialogRef<PromptReviewDialogComponent>
  ) {
    this.editablePrompt = data.prompt;
  }

  onProceed() {
    this.dialogRef.close({ proceed: true, prompt: this.editablePrompt });
  }
}
