import { Component, signal, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { CreateProjectModalComponent } from './components/create-project-modal/create-project-modal.component';
import { ProjectWorkspaceComponent, ProjectData } from './components/project-workspace/project-workspace.component';
import { DevModeService } from './services/dev-mode.service';
import { MOCK_PROJECT_CONTEXT, MOCK_FEATURES, MOCK_STORIES, MOCK_PROJECT_SUMMARY } from './services/dev-data';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, CommonModule, ProjectWorkspaceComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('autoagents-app');
  protected readonly activeProject = signal<ProjectData | null>(null);
  
  // Dev mode service
  devModeService = inject(DevModeService);

  constructor(private dialog: MatDialog) {}

  openCreateProjectModal() {
    const dialogRef = this.dialog.open(CreateProjectModalComponent, {
      width: '90vw',
      maxWidth: '1400px',
      maxHeight: '85vh',
      panelClass: 'custom-dialog-container',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((result: ProjectData | undefined) => {
      if (result) {
        this.activeProject.set(result);
      }
    });
  }
  
  // DEV MODE: Quick start with mock data - bypass entire modal
  quickStartDevMode() {
    console.log('[DEV MODE] Quick starting with mock data...');
    
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
  }
  
  toggleDevMode() {
    this.devModeService.toggleDevMode();
  }
}
