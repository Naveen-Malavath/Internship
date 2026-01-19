import { Injectable, signal, inject } from '@angular/core';
import { ProjectSettings, getDefaultSettings } from '../models/settings.model';
import { SettingsService } from './settings.service';

export interface ProjectData {
  projectName: string;
  projectKey: string;
  industry: string;
  teamSize: string;
  executiveSummary: string;
  promptSummary: string;
  finalPrompt: string;
  features: any[];
  stories: any[];
  epicIdeas: string[];
  riskHighlights: string[];
  generatedRisks: string;
  settings: ProjectSettings;  // Per-project settings
}

/**
 * Service to share project data between routes
 * Used to pass newly created project data from Projects page to Workspace page
 */
@Injectable({
  providedIn: 'root'
})
export class ProjectStateService {
  private settingsService = inject(SettingsService);
  private currentProject = signal<ProjectData | null>(null);
  
  setCurrentProject(project: ProjectData): void {
    // Ensure project has settings, use defaults if not provided
    if (!project.settings) {
      project.settings = this.settingsService.getSettingsForNewProject();
    }
    
    console.log('[ProjectStateService] ✅ Setting current project:', project.projectName);
    console.log('[ProjectStateService] 📊 Project data:', {
      features: project.features?.length || 0,
      stories: project.stories?.length || 0,
      industry: project.industry,
      settings: {
        enableStories: project.settings.workflow.enableStories,
        enableWireframes: project.settings.workflow.enableWireframes,
        storiesPerFeature: project.settings.stories.perFeature
      }
    });
    this.currentProject.set(project);
  }
  
  getCurrentProject(): ProjectData | null {
    const project = this.currentProject();
    console.log('[ProjectStateService] 🔍 Getting current project:', project?.projectName || 'null');
    return project;
  }
  
  /**
   * Get current project's settings
   */
  getCurrentProjectSettings(): ProjectSettings | null {
    const project = this.currentProject();
    return project?.settings || null;
  }
  
  /**
   * Update current project's settings
   */
  updateCurrentProjectSettings(settings: ProjectSettings): void {
    const project = this.currentProject();
    if (project) {
      const updated = { ...project, settings };
      this.currentProject.set(updated);
      console.log('[ProjectStateService] ⚙️ Updated project settings:', {
        enableStories: settings.workflow.enableStories,
        enableWireframes: settings.workflow.enableWireframes,
        storiesPerFeature: settings.stories.perFeature
      });
    }
  }
  
  /**
   * Alias for updateCurrentProjectSettings (used by ProjectSettingsComponent)
   */
  updateProjectSettings(settings: ProjectSettings): void {
    this.updateCurrentProjectSettings(settings);
  }
  
  /**
   * Check if stories are enabled for current project
   */
  areStoriesEnabled(): boolean {
    const project = this.currentProject();
    return project?.settings?.workflow?.enableStories ?? true;
  }
  
  /**
   * Check if wireframes are enabled for current project
   */
  areWireframesEnabled(): boolean {
    const project = this.currentProject();
    return project?.settings?.workflow?.enableWireframes ?? true;
  }
  
  /**
   * Get stories per feature setting for current project
   */
  getStoriesPerFeature(): number {
    const project = this.currentProject();
    return project?.settings?.stories?.perFeature ?? 2;
  }
  
  clearCurrentProject(): void {
    console.log('[ProjectStateService] Clearing current project');
    this.currentProject.set(null);
  }
}
