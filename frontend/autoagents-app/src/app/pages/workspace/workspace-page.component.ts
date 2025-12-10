import { Component, signal, inject, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { ProjectWorkspaceComponent, ProjectData } from '../../components/project-workspace/project-workspace.component';
import { CreateProjectModalComponent } from '../../components/create-project-modal/create-project-modal.component';
import { DevModeService } from '../../services/dev-mode.service';
import { MOCK_PROJECT_CONTEXT, MOCK_FEATURES, MOCK_STORIES, MOCK_PROJECT_SUMMARY } from '../../services/dev-data';

@Component({
  selector: 'app-workspace-page',
  standalone: true,
  imports: [CommonModule, MatIconModule, ProjectWorkspaceComponent],
  template: `
    <div class="workspace-page">
      <!-- Workspace Header -->
      <header class="workspace-header">
        <div class="header-content">
          <div class="header-left">
            <h1>Project Workspace</h1>
            @if (activeProject()) {
              <p class="active-project-label">
                Active project · {{ activeProject()?.projectName }} ({{ activeProject()?.projectKey }})
              </p>
            } @else {
              <p class="header-subtitle">No active project. Create or select a project to get started.</p>
            }
          </div>
          <div class="header-actions">
            <!-- Dev Mode Toggle -->
            <div class="dev-mode-toggle" [class.active]="devModeService.isDevMode()">
              <button class="dev-toggle-btn" (click)="toggleDevMode()">
                <span class="toggle-icon">{{ devModeService.isDevMode() ? '🔧' : '⚙️' }}</span>
                <span class="toggle-label">DEV: {{ devModeService.isDevMode() ? 'ON' : 'OFF' }}</span>
              </button>
            </div>
            
            <!-- Quick Start (visible only in dev mode) -->
            @if (devModeService.isDevMode() && !activeProject()) {
              <button class="btn-quick-start" (click)="quickStartDevMode()">
                ⚡ Quick Start
              </button>
            }
            
            <span class="status-badge">
              <mat-icon>check_circle</mat-icon>
              Operational
            </span>
            
            <button class="btn-primary" (click)="openCreateProjectModal()">
              <mat-icon>add</mat-icon>
              New Project
            </button>
          </div>
        </div>
      </header>

      <!-- Main Content -->
      <main class="workspace-main">
        @if (activeProject()) {
          <app-project-workspace [project]="activeProject()!"></app-project-workspace>
        } @else {
          <div class="empty-state">
            <div class="empty-state-content">
              <mat-icon class="empty-icon">workspaces</mat-icon>
              <h2>No Active Project</h2>
              <p>Create a new project or select an existing one from the Projects page to begin working.</p>
              <div class="empty-actions">
                <button class="btn-primary" (click)="openCreateProjectModal()">
                  <mat-icon>add</mat-icon>
                  Create New Project
                </button>
                @if (devModeService.isDevMode()) {
                  <button class="btn-secondary" (click)="quickStartDevMode()">
                    <mat-icon>bolt</mat-icon>
                    Quick Start (Dev)
                  </button>
                }
              </div>
            </div>
          </div>
        }
      </main>
    </div>
  `,
  styles: [`
    .workspace-page {
      min-height: 100%;
      display: flex;
      flex-direction: column;
    }

    .workspace-header {
      padding: 1.5rem 2rem;
      background: rgba(15, 23, 42, 0.5);
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    }

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .header-left {
      h1 {
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0 0 0.5rem 0;
        background: linear-gradient(90deg, #ffffff 0%, #94a3b8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }

      .active-project-label,
      .header-subtitle {
        color: #94a3b8;
        margin: 0;
        font-size: 0.9375rem;
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .dev-mode-toggle {
      .dev-toggle-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0.5rem;
        color: #94a3b8;
        font-size: 0.75rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;

        &:hover {
          background: rgba(255, 255, 255, 0.1);
          border-color: rgba(255, 255, 255, 0.2);
        }
      }

      &.active .dev-toggle-btn {
        background: rgba(245, 158, 11, 0.15);
        border-color: rgba(245, 158, 11, 0.3);
        color: #fbbf24;
      }
    }

    .btn-quick-start {
      padding: 0.5rem 1rem;
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 0.5rem;
      color: #fbbf24;
      font-size: 0.875rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(245, 158, 11, 0.25);
      }
    }

    .status-badge {
      display: flex;
      align-items: center;
      gap: 0.375rem;
      padding: 0.5rem 1rem;
      background: rgba(16, 185, 129, 0.1);
      border-radius: 20px;
      color: #10b981;
      font-size: 0.8125rem;
      font-weight: 500;

      mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
      }
    }

    .btn-primary {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.25rem;
      background: linear-gradient(135deg, #3b82f6, #2563eb);
      border: none;
      border-radius: 10px;
      color: white;
      font-size: 0.9375rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
      }

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    .workspace-main {
      flex: 1;
      overflow: auto;
    }

    .empty-state {
      height: 100%;
      min-height: 500px;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .empty-state-content {
      text-align: center;
      max-width: 500px;

      .empty-icon {
        font-size: 80px;
        width: 80px;
        height: 80px;
        color: #475569;
        margin-bottom: 1.5rem;
      }

      h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0 0 1rem 0;
      }

      p {
        color: #94a3b8;
        margin: 0 0 2rem 0;
        line-height: 1.6;
      }
    }

    .empty-actions {
      display: flex;
      justify-content: center;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .btn-secondary {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.25rem;
      background: rgba(59, 130, 246, 0.1);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 10px;
      color: #60a5fa;
      font-size: 0.9375rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(59, 130, 246, 0.2);
      }

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    @media (max-width: 768px) {
      .workspace-header {
        padding: 1rem;
      }

      .header-content {
        flex-direction: column;
      }

      .header-left h1 {
        font-size: 1.5rem;
      }

      .header-actions {
        width: 100%;
        justify-content: flex-start;
      }
    }
  `]
})
export class WorkspacePageComponent implements OnInit {
  devModeService = inject(DevModeService);
  private dialog = inject(MatDialog);
  
  activeProject = signal<ProjectData | null>(null);

  ngOnInit(): void {
    console.log('[WorkspacePage] Initializing workspace page...');
    console.log('[WorkspacePage] Dev mode:', this.devModeService.isDevMode());
  }

  openCreateProjectModal(): void {
    console.log('[WorkspacePage] Opening create project modal...');
    
    const dialogRef = this.dialog.open(CreateProjectModalComponent, {
      width: '90vw',
      maxWidth: '1400px',
      maxHeight: '85vh',
      panelClass: 'custom-dialog-container',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((result: ProjectData | undefined) => {
      console.log('[WorkspacePage] Dialog closed with result:', result ? 'project created' : 'cancelled');
      if (result) {
        this.activeProject.set(result);
      }
    });
  }

  quickStartDevMode(): void {
    console.log('[WorkspacePage] Quick starting with mock data...');
    
    const mockProject: ProjectData = {
      projectName: MOCK_PROJECT_CONTEXT.projectName,
      projectKey: 'ECOM',
      industry: MOCK_PROJECT_CONTEXT.industry,
      methodology: MOCK_PROJECT_CONTEXT.methodology,
      teamSize: '5-10',
      executiveSummary: MOCK_PROJECT_SUMMARY,
      promptSummary: MOCK_PROJECT_CONTEXT.promptSummary,
      finalPrompt: MOCK_PROJECT_CONTEXT.promptSummary,
      features: MOCK_FEATURES,
      stories: MOCK_STORIES,
      epicIdeas: ['User Authentication', 'Product Catalog', 'Shopping Cart', 'Order Management'],
      riskHighlights: ['Integration complexity', 'Performance at scale', 'Security compliance'],
      generatedRisks: 'Payment integration risks, Third-party API dependencies, Data privacy compliance'
    };
    
    this.activeProject.set(mockProject);
    console.log('[WorkspacePage] Mock project loaded');
  }

  toggleDevMode(): void {
    console.log('[WorkspacePage] Toggling dev mode...');
    this.devModeService.toggleDevMode();
  }
}
