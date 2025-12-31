import { Injectable, signal } from '@angular/core';

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
}

/**
 * Service to share project data between routes
 * Used to pass newly created project data from Projects page to Workspace page
 */
@Injectable({
  providedIn: 'root'
})
export class ProjectStateService {
  private currentProject = signal<ProjectData | null>(null);
  
  setCurrentProject(project: ProjectData): void {
    console.log('[ProjectStateService] ✅ Setting current project:', project.projectName);
    console.log('[ProjectStateService] 📊 Project data:', {
      features: project.features?.length || 0,
      stories: project.stories?.length || 0,
      industry: project.industry
    });
    this.currentProject.set(project);
  }
  
  getCurrentProject(): ProjectData | null {
    const project = this.currentProject();
    console.log('[ProjectStateService] 🔍 Getting current project:', project?.projectName || 'null');
    return project;
  }
  
  clearCurrentProject(): void {
    console.log('[ProjectStateService] Clearing current project');
    this.currentProject.set(null);
  }
}
