import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MAT_DIALOG_DATA, MatDialogModule } from '@angular/material/dialog';

export interface LoadingDialogData {
  message: string;
}

@Component({
  selector: 'app-loading-dialog',
  standalone: true,
  imports: [CommonModule, MatDialogModule],
  template: `
    <div class="loading-container">
      <div class="loading-animation">
        <div class="pulse-ring"></div>
        <div class="pulse-ring delay-1"></div>
        <div class="pulse-ring delay-2"></div>
        <div class="loading-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z" 
                  fill="currentColor" class="star"/>
          </svg>
        </div>
      </div>
      <h2 class="loading-title">{{ data.message }}</h2>
      <p class="loading-subtitle">AI is crafting your content...</p>
      <div class="progress-bar">
        <div class="progress-fill"></div>
      </div>
    </div>
  `,
  styles: [`
    .loading-container {
      padding: 3rem;
      text-align: center;
      background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 100%);
      border-radius: 1rem;
      min-width: 400px;
      position: relative;
      overflow: hidden;
    }

    .loading-container::before {
      content: '';
      position: absolute;
      top: -50%;
      left: -50%;
      width: 200%;
      height: 200%;
      background: radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
      animation: rotate 10s linear infinite;
    }

    @keyframes rotate {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }

    .loading-animation {
      position: relative;
      width: 120px;
      height: 120px;
      margin: 0 auto 2rem;
    }

    .pulse-ring {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 100%;
      height: 100%;
      border: 3px solid rgba(59, 130, 246, 0.4);
      border-radius: 50%;
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }

    .pulse-ring.delay-1 {
      animation-delay: 0.5s;
    }

    .pulse-ring.delay-2 {
      animation-delay: 1s;
    }

    @keyframes pulse {
      0% {
        transform: translate(-50%, -50%) scale(0.5);
        opacity: 1;
      }
      100% {
        transform: translate(-50%, -50%) scale(1.5);
        opacity: 0;
      }
    }

    .loading-icon {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 48px;
      height: 48px;
      color: #3b82f6;
      animation: float 3s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% {
        transform: translate(-50%, -50%) translateY(0px);
      }
      50% {
        transform: translate(-50%, -50%) translateY(-10px);
      }
    }

    .star {
      animation: sparkle 2s ease-in-out infinite;
      transform-origin: center;
    }

    @keyframes sparkle {
      0%, 100% {
        opacity: 1;
        transform: scale(1);
      }
      50% {
        opacity: 0.7;
        transform: scale(1.2);
      }
    }

    .loading-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #ffffff;
      margin: 0 0 0.5rem 0;
      position: relative;
      z-index: 1;
    }

    .loading-subtitle {
      font-size: 1rem;
      color: #94a3b8;
      margin: 0 0 2rem 0;
      position: relative;
      z-index: 1;
    }

    .progress-bar {
      width: 100%;
      height: 4px;
      background: rgba(71, 85, 105, 0.3);
      border-radius: 2px;
      overflow: hidden;
      position: relative;
      z-index: 1;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #3b82f6 0%, #2563eb 50%, #3b82f6 100%);
      background-size: 200% 100%;
      animation: progress 2s linear infinite;
      border-radius: 2px;
    }

    @keyframes progress {
      0% {
        background-position: 0% 0%;
      }
      100% {
        background-position: 200% 0%;
      }
    }
  `]
})
export class LoadingDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: LoadingDialogData) {}
}
