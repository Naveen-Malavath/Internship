import { Component, inject, OnInit, OnDestroy, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { NavigationService } from '../../services/navigation.service';
import { ActivityService } from '../../services/activity.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="dashboard-container">
      <header class="dashboard-header">
        <h1>Dashboard</h1>
        <p class="subtitle">Welcome to AutoAgents Workspace</p>
      </header>

      <section class="cards-row">
        <div class="card stat-card">
          <div class="card-icon">
            <mat-icon>folder</mat-icon>
          </div>
          <div class="card-content">
            <span class="card-value">{{ projectCount }}</span>
            <span class="card-label">Active Projects</span>
          </div>
        </div>

        <button class="card action-card" (click)="navigateTo('/projects')">
          <div class="card-icon">
            <mat-icon>add_circle</mat-icon>
          </div>
          <span class="card-label">New Project</span>
        </button>
      </section>

      <section class="recent-activity">
        <h2>Recent Activity</h2>
        <div class="activity-list">
          @for (activity of recentActivities(); track activity.id) {
            <div class="activity-item">
              <div class="activity-icon" [class]="activity.type">
                <mat-icon>{{ activity.icon }}</mat-icon>
              </div>
              <div class="activity-content">
                <span class="activity-title">{{ activity.title }}</span>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
          }
        </div>
      </section>
    </div>
  `,
  styles: [`
    .dashboard-container {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .dashboard-header {
      margin-bottom: 2rem;

      h1 {
        font-size: 2rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(90deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }

      .subtitle {
        color: #94a3b8;
        margin: 0;
        font-size: 1rem;
      }
    }

    .cards-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .card {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
      padding: 1.5rem;
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      transition: all 0.2s ease;
      min-height: 120px;

      &:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
      }
    }

    .stat-card {
      flex-direction: row;
      justify-content: flex-start;
      gap: 1rem;
    }

    .action-card {
      cursor: pointer;
      color: #f1f5f9;

      &:hover {
        background: rgba(59, 130, 246, 0.15);

        .card-icon mat-icon {
          color: #60a5fa;
        }
      }
    }

    .card-icon {
      width: 56px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(59, 130, 246, 0.15);
      border-radius: 12px;

      mat-icon {
        font-size: 28px;
        width: 28px;
        height: 28px;
        color: #3b82f6;
        transition: color 0.2s ease;
      }
    }

    .action-card .card-icon {
      background: rgba(148, 163, 184, 0.1);

      mat-icon {
        color: #94a3b8;
      }
    }

    .card-content {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .card-value {
      font-size: 1.75rem;
      font-weight: 700;
      color: #f1f5f9;
    }

    .card-label {
      font-size: 0.875rem;
      color: #94a3b8;
      font-weight: 500;
    }

    .recent-activity {
      margin-bottom: 2rem;

      h2 {
        font-size: 1.25rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0 0 1rem 0;
      }
    }

    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .activity-item {
      display: flex;
      align-items: center;
      gap: 1rem;
      padding: 1rem;
      background: rgba(30, 41, 59, 0.3);
      border-radius: 8px;
      transition: background 0.2s ease;

      &:hover {
        background: rgba(30, 41, 59, 0.5);
      }
    }

    .activity-icon {
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(59, 130, 246, 0.15);
      border-radius: 8px;

      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: #3b82f6;
      }

      &.success mat-icon { color: #10b981; }
      &.success { background: rgba(16, 185, 129, 0.15); }
      
      &.warning mat-icon { color: #f59e0b; }
      &.warning { background: rgba(245, 158, 11, 0.15); }
    }

    .activity-content {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }

    .activity-title {
      font-size: 0.9375rem;
      color: #f1f5f9;
    }

    .activity-time {
      font-size: 0.8125rem;
      color: #64748b;
    }

    @media (max-width: 1024px) {
      .cards-row {
        grid-template-columns: repeat(2, 1fr);
      }
    }

    @media (max-width: 768px) {
      .dashboard-container {
        padding: 1rem;
      }

      .dashboard-header h1 {
        font-size: 1.5rem;
      }

      .cards-row {
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
      }

      .card {
        padding: 1rem;
        min-height: 100px;
      }

      .stat-card {
        flex-direction: column;
        text-align: center;
      }
    }

    @media (max-width: 480px) {
      .cards-row {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  private navService = inject(NavigationService);
  private activityService = inject(ActivityService);

  projectCount = 3;

  // Use real activities from the activity service
  recentActivities = computed(() => this.activityService.getRecentActivities(5));
  
  private timeUpdateInterval: any;

  ngOnInit(): void {
    console.log('[DashboardComponent] Initializing dashboard...');
    console.log('[DashboardComponent] Stats loaded - Projects:', this.projectCount);
    console.log('[DashboardComponent] Activity service connected, activities count:', this.activityService.getActivities().length);
    
    // Edge case: No activities yet, log a welcome activity
    if (this.activityService.getActivities().length === 0) {
      console.log('[DashboardComponent] No activities found, logging welcome message');
      this.activityService.logActivity('Welcome to AutoAgents!', 'waving_hand', 'info');
    }
    
    // Update time labels every minute
    this.timeUpdateInterval = setInterval(() => {
      console.log('[DashboardComponent] Updating activity time labels');
      this.activityService.updateTimeLabels();
    }, 60000); // 60 seconds
  }
  
  ngOnDestroy(): void {
    console.log('[DashboardComponent] Component destroying, cleaning up interval');
    // Edge case: Clean up interval to prevent memory leak
    if (this.timeUpdateInterval) {
      clearInterval(this.timeUpdateInterval);
    }
  }

  navigateTo(route: string): void {
    console.log('[DashboardComponent] Quick action clicked, navigating to:', route);
    this.navService.navigate(route);
  }
}
