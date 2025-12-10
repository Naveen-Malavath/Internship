import { Component, inject, signal, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatDialog } from '@angular/material/dialog';
import { NavigationService } from '../../services/navigation.service';
import { CreateProjectModalComponent } from '../../components/create-project-modal/create-project-modal.component';

interface Project {
  id: string;
  name: string;
  key: string;
  status: 'active' | 'paused' | 'completed';
  progress: number;
  lastUpdated: string;
  features: number;
  stories: number;
}

@Component({
  selector: 'app-projects',
  standalone: true,
  imports: [CommonModule, FormsModule, MatIconModule],
  template: `
    <div class="projects-container">
      <header class="page-header">
        <div class="header-content">
          <h1>Projects</h1>
          <p class="subtitle">Manage your AutoAgents projects</p>
        </div>
        <button class="btn-primary" (click)="openCreateProject()">
          <mat-icon>add</mat-icon>
          <span>New Project</span>
        </button>
      </header>

      <section class="projects-filters">
        <div class="search-box">
          <mat-icon>search</mat-icon>
          <input 
            type="text" 
            placeholder="Search projects..."
            [(ngModel)]="searchQuery"
            (input)="onSearchChange()">
        </div>
        <div class="filter-buttons">
          @for (filter of filters; track filter.value) {
            <button 
              class="filter-btn"
              [class.active]="activeFilter() === filter.value"
              (click)="setFilter(filter.value)">
              {{ filter.label }}
            </button>
          }
        </div>
      </section>

      <section class="projects-grid">
        @if (filteredProjects().length === 0) {
          <div class="empty-state">
            <mat-icon>folder_off</mat-icon>
            <h3>No projects found</h3>
            <p>{{ searchQuery ? 'Try a different search term' : 'Create your first project to get started' }}</p>
            @if (!searchQuery) {
              <button class="btn-secondary" (click)="openCreateProject()">
                <mat-icon>add</mat-icon>
                Create Project
              </button>
            }
          </div>
        } @else {
          @for (project of filteredProjects(); track project.id) {
            <div class="project-card" (click)="openProject(project)">
              <div class="card-header">
                <div class="project-info">
                  <h3>{{ project.name }}</h3>
                  <span class="project-key">{{ project.key }}</span>
                </div>
                <span class="status-badge" [class]="project.status">
                  {{ project.status }}
                </span>
              </div>
              
              <div class="progress-section">
                <div class="progress-bar">
                  <div class="progress-fill" [style.width.%]="project.progress"></div>
                </div>
                <span class="progress-text">{{ project.progress }}% complete</span>
              </div>

              <div class="card-stats">
                <div class="stat">
                  <mat-icon>flag</mat-icon>
                  <span>{{ project.features }} Features</span>
                </div>
                <div class="stat">
                  <mat-icon>article</mat-icon>
                  <span>{{ project.stories }} Stories</span>
                </div>
              </div>

              <div class="card-footer">
                <span class="last-updated">Updated {{ project.lastUpdated }}</span>
                <button class="btn-icon" (click)="openProjectMenu($event, project)">
                  <mat-icon>more_vert</mat-icon>
                </button>
              </div>
            </div>
          }
        }
      </section>
    </div>
  `,
  styles: [`
    .projects-container {
      padding: 2rem;
      max-width: 1400px;
      margin: 0 auto;
    }

    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 2rem;
      gap: 1rem;
      flex-wrap: wrap;

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

    .btn-primary {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
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
        font-size: 20px;
        width: 20px;
        height: 20px;
      }
    }

    .projects-filters {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }

    .search-box {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      padding: 0.75rem 1rem;
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 10px;
      flex: 1;
      max-width: 400px;

      mat-icon {
        color: #64748b;
        font-size: 20px;
        width: 20px;
        height: 20px;
      }

      input {
        flex: 1;
        background: transparent;
        border: none;
        color: #f1f5f9;
        font-size: 0.9375rem;
        outline: none;

        &::placeholder {
          color: #64748b;
        }
      }
    }

    .filter-buttons {
      display: flex;
      gap: 0.5rem;
    }

    .filter-btn {
      padding: 0.5rem 1rem;
      background: transparent;
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 8px;
      color: #94a3b8;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.05);
        color: #f1f5f9;
      }

      &.active {
        background: rgba(59, 130, 246, 0.15);
        border-color: rgba(59, 130, 246, 0.3);
        color: #60a5fa;
      }
    }

    .projects-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }

    .project-card {
      background: rgba(30, 41, 59, 0.5);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 1.5rem;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(30, 41, 59, 0.8);
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
      }
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 1rem;
    }

    .project-info {
      h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0 0 0.25rem 0;
      }

      .project-key {
        font-size: 0.8125rem;
        color: #64748b;
        font-family: 'Fira Code', monospace;
      }
    }

    .status-badge {
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;

      &.active {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
      }

      &.paused {
        background: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
      }

      &.completed {
        background: rgba(59, 130, 246, 0.15);
        color: #3b82f6;
      }
    }

    .progress-section {
      margin-bottom: 1rem;
    }

    .progress-bar {
      height: 6px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 3px;
      overflow: hidden;
      margin-bottom: 0.5rem;
    }

    .progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #3b82f6, #60a5fa);
      border-radius: 3px;
      transition: width 0.3s ease;
    }

    .progress-text {
      font-size: 0.8125rem;
      color: #94a3b8;
    }

    .card-stats {
      display: flex;
      gap: 1.5rem;
      margin-bottom: 1rem;
    }

    .stat {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      color: #94a3b8;
      font-size: 0.875rem;

      mat-icon {
        font-size: 16px;
        width: 16px;
        height: 16px;
      }
    }

    .card-footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-top: 1rem;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
    }

    .last-updated {
      font-size: 0.8125rem;
      color: #64748b;
    }

    .btn-icon {
      width: 32px;
      height: 32px;
      border: none;
      border-radius: 6px;
      background: transparent;
      color: #94a3b8;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #f1f5f9;
      }

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    .empty-state {
      grid-column: 1 / -1;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 4rem 2rem;
      text-align: center;

      mat-icon {
        font-size: 64px;
        width: 64px;
        height: 64px;
        color: #475569;
        margin-bottom: 1rem;
      }

      h3 {
        font-size: 1.25rem;
        color: #f1f5f9;
        margin: 0 0 0.5rem 0;
      }

      p {
        color: #94a3b8;
        margin: 0 0 1.5rem 0;
      }
    }

    .btn-secondary {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 10px;
      color: #60a5fa;
      font-size: 0.9375rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        background: rgba(59, 130, 246, 0.25);
      }

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    @media (max-width: 768px) {
      .projects-container {
        padding: 1rem;
      }

      .page-header h1 {
        font-size: 1.5rem;
      }

      .projects-filters {
        flex-direction: column;
        align-items: stretch;
      }

      .search-box {
        max-width: none;
      }

      .filter-buttons {
        overflow-x: auto;
        padding-bottom: 0.5rem;
      }

      .projects-grid {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class ProjectsComponent implements OnInit {
  private navService = inject(NavigationService);
  private dialog = inject(MatDialog);

  searchQuery = '';
  activeFilter = signal<string>('all');
  
  filters = [
    { label: 'All', value: 'all' },
    { label: 'Active', value: 'active' },
    { label: 'Paused', value: 'paused' },
    { label: 'Completed', value: 'completed' }
  ];

  projects = signal<Project[]>([
    {
      id: '1',
      name: 'E-Commerce Platform',
      key: 'ECOM',
      status: 'active',
      progress: 65,
      lastUpdated: '2 hours ago',
      features: 12,
      stories: 48
    },
    {
      id: '2',
      name: 'Mobile Banking App',
      key: 'MBA',
      status: 'active',
      progress: 32,
      lastUpdated: 'Yesterday',
      features: 8,
      stories: 24
    },
    {
      id: '3',
      name: 'Healthcare Portal',
      key: 'HCP',
      status: 'paused',
      progress: 45,
      lastUpdated: '3 days ago',
      features: 15,
      stories: 56
    },
    {
      id: '4',
      name: 'Social Media Dashboard',
      key: 'SMD',
      status: 'completed',
      progress: 100,
      lastUpdated: 'Last week',
      features: 10,
      stories: 40
    }
  ]);

  filteredProjects = signal<Project[]>([]);

  ngOnInit(): void {
    console.log('[ProjectsComponent] Initializing...');
    console.log('[ProjectsComponent] Projects loaded:', this.projects().length);
    this.updateFilteredProjects();
    
    // Update badge in navigation
    this.navService.updateBadge('projects', this.projects().length);
  }

  updateFilteredProjects(): void {
    const filter = this.activeFilter();
    const query = this.searchQuery.toLowerCase();
    
    console.log('[ProjectsComponent] Updating filtered projects - filter:', filter, 'query:', query);
    
    let filtered = this.projects();
    
    // Apply status filter
    if (filter !== 'all') {
      filtered = filtered.filter((p: Project) => p.status === filter);
    }
    
    // Apply search query
    if (query) {
      filtered = filtered.filter((p: Project) => 
        p.name.toLowerCase().includes(query) || 
        p.key.toLowerCase().includes(query)
      );
    }
    
    console.log('[ProjectsComponent] Filtered projects count:', filtered.length);
    this.filteredProjects.set(filtered);
  }

  setFilter(filter: string): void {
    console.log('[ProjectsComponent] Setting filter:', filter);
    this.activeFilter.set(filter);
    this.updateFilteredProjects();
  }

  onSearchChange(): void {
    console.log('[ProjectsComponent] Search query changed:', this.searchQuery);
    this.updateFilteredProjects();
  }

  openCreateProject(): void {
    console.log('[ProjectsComponent] Opening create project modal');
    this.dialog.open(CreateProjectModalComponent, {
      width: '90vw',
      maxWidth: '1400px',
      maxHeight: '85vh',
      panelClass: 'custom-dialog-container',
      disableClose: false
    });
  }

  openProject(project: Project): void {
    console.log('[ProjectsComponent] Opening project:', project.name);
    this.navService.navigate('/workspace');
  }

  openProjectMenu(event: Event, project: Project): void {
    event.stopPropagation();
    console.log('[ProjectsComponent] Opening project menu for:', project.name);
    // TODO: Implement project menu
  }
}
