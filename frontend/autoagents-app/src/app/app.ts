import { Component, signal, inject, OnInit } from '@angular/core';
import { RouterOutlet, RouterLink, Router, NavigationEnd } from '@angular/router';
import { CommonModule, Location } from '@angular/common';
import { MatDialog } from '@angular/material/dialog';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CreateProjectModalComponent } from './components/create-project-modal/create-project-modal.component';
import { ProjectData } from './components/project-workspace/project-workspace.component';
import { SidebarNavComponent } from './components/sidebar-nav/sidebar-nav.component';
import { NavigationService } from './services/navigation.service';
import { DevModeService } from './services/dev-mode.service';
import { MOCK_PROJECT_CONTEXT, MOCK_FEATURES, MOCK_STORIES, MOCK_PROJECT_SUMMARY } from './services/dev-data';
import { filter } from 'rxjs/operators';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, CommonModule, MatIconModule, MatTooltipModule, SidebarNavComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App implements OnInit {
  protected readonly title = signal('autoagents-app');
  protected readonly activeProject = signal<ProjectData | null>(null);
  
  // Services
  navService = inject(NavigationService);
  devModeService = inject(DevModeService);
  private location = inject(Location);
  private router = inject(Router);
  
  // Navigation state
  canGoBack = signal(false);
  canGoForward = signal(false);
  private navigationHistory: string[] = [];
  private currentIndex = -1;
  private isNavigatingBackOrForward = false;

  constructor(private dialog: MatDialog) {}

  ngOnInit(): void {
    console.log('[App] Application initializing...');
    console.log('[App] Navigation service initialized');
    console.log('[App] Dev mode:', this.devModeService.isDevMode());
    
    // Track navigation history for back/forward functionality
    this.router.events.pipe(
      filter(event => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      console.log('[App] Navigation event:', event.url);
      
      const currentUrl = event.url;
      
      // Check if this was triggered by our back/forward buttons
      if (this.isNavigatingBackOrForward) {
        console.log('[App] Back/Forward navigation detected, updating state only');
        this.isNavigatingBackOrForward = false;
        this.updateNavigationState();
        return;
      }
      
      // Check if we're navigating to a URL that's already in our history
      const existingIndex = this.navigationHistory.indexOf(currentUrl);
      
      if (existingIndex !== -1 && existingIndex !== this.currentIndex) {
        // User used browser back/forward buttons
        console.log('[App] Browser back/forward detected, syncing index');
        this.currentIndex = existingIndex;
      } else if (this.currentIndex === -1 || this.navigationHistory[this.currentIndex] !== currentUrl) {
        // New navigation - add to history
        // Remove any forward history if we're navigating from middle of stack
        if (this.currentIndex < this.navigationHistory.length - 1) {
          this.navigationHistory = this.navigationHistory.slice(0, this.currentIndex + 1);
        }
        
        this.navigationHistory.push(currentUrl);
        this.currentIndex = this.navigationHistory.length - 1;
        
        console.log('[App] Navigation history updated:', {
          history: this.navigationHistory,
          currentIndex: this.currentIndex
        });
      }
      
      this.updateNavigationState();
    });
  }

  openCreateProjectModal() {
    console.log('[App] Opening create project modal...');
    const dialogRef = this.dialog.open(CreateProjectModalComponent, {
      width: '90vw',
      maxWidth: '1400px',
      maxHeight: '85vh',
      panelClass: 'custom-dialog-container',
      disableClose: false
    });

    dialogRef.afterClosed().subscribe((result: ProjectData | undefined) => {
      console.log('[App] Dialog closed, result:', result ? 'project created' : 'cancelled');
      if (result) {
        this.activeProject.set(result);
      }
    });
  }
  
  // DEV MODE: Quick start with mock data - bypass entire modal
  quickStartDevMode() {
    console.log('[App] [DEV MODE] Quick starting with mock data...');
    
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
    console.log('[App] Mock project set');
  }
  
  toggleDevMode() {
    console.log('[App] Toggling dev mode...');
    this.devModeService.toggleDevMode();
  }
  
  /**
   * Navigate back in browser history
   * Edge cases handled:
   * - No history available
   * - Already at first page
   */
  navigateBack() {
    console.log('[App] Navigate back clicked');
    
    // Edge case: Check if we can go back
    if (!this.canGoBack()) {
      console.warn('[App] Cannot go back - no history available');
      return;
    }
    
    try {
      this.isNavigatingBackOrForward = true;
      this.currentIndex--;
      this.location.back();
      console.log('[App] Navigated back successfully, new index:', this.currentIndex);
    } catch (error) {
      console.error('[App] Error navigating back:', error);
      this.isNavigatingBackOrForward = false;
      this.currentIndex++; // Revert on error
    }
  }
  
  /**
   * Navigate forward in browser history
   * Edge cases handled:
   * - No forward history
   * - Already at latest page
   */
  navigateForward() {
    console.log('[App] Navigate forward clicked');
    
    // Edge case: Check if we can go forward
    if (!this.canGoForward()) {
      console.warn('[App] Cannot go forward - no forward history');
      return;
    }
    
    try {
      this.isNavigatingBackOrForward = true;
      this.currentIndex++;
      this.location.forward();
      console.log('[App] Navigated forward successfully, new index:', this.currentIndex);
    } catch (error) {
      console.error('[App] Error navigating forward:', error);
      this.isNavigatingBackOrForward = false;
      this.currentIndex--; // Revert on error
    }
  }
  
  /**
   * Update navigation button states
   * Determines if back/forward arrows should be enabled
   */
  private updateNavigationState() {
    // Edge case: No history yet
    if (this.navigationHistory.length === 0) {
      this.canGoBack.set(false);
      this.canGoForward.set(false);
      return;
    }
    
    // Can go back if we're not at the first item
    const hasBackHistory = this.currentIndex > 0;
    this.canGoBack.set(hasBackHistory);
    
    // Can go forward if we're not at the last item
    const hasForwardHistory = this.currentIndex < this.navigationHistory.length - 1;
    this.canGoForward.set(hasForwardHistory);
    
    console.log('[App] Navigation state updated:', {
      canGoBack: this.canGoBack(),
      canGoForward: this.canGoForward(),
      currentIndex: this.currentIndex,
      historyLength: this.navigationHistory.length
    });
  }
}
