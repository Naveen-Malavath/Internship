import { Injectable } from '@angular/core';
import { AgentFeatureSpec, AgentStorySpec, AgentVisualizationResponse } from '../types';

/**
 * Workspace Navigation Helper
 * 
 * Provides utility methods to navigate to workspace with Agent-3 visualizations
 */
@Injectable({
  providedIn: 'root'
})
export class WorkspaceNavigationService {
  
  /**
   * Prepare workspace state for navigation
   * 
   * @param context - Original user prompt/context
   * @param features - Approved features from Agent-1
   * @param stories - Approved stories from Agent-2
   * @param mermaidCode - Optional pre-generated Mermaid code
   * @returns State object for navigation
   */
  prepareWorkspaceState(
    context: string,
    features: AgentFeatureSpec[],
    stories: AgentStorySpec[],
    mermaidCode?: string,
    visualization?: AgentVisualizationResponse
  ): WorkspaceState {
    return {
      context,
      features,
      stories,
      mermaidCode,
      visualization,
      timestamp: Date.now()
    };
  }
  
  /**
   * Navigate to workspace programmatically
   * (In a real Angular Router setup)
   */
  navigateToWorkspace(state: WorkspaceState): void {
    // In this app, workspace is toggled via signal, not router
    // This is a placeholder for apps using Angular Router
    console.log('[WorkspaceNav] Navigate to workspace with state:', {
      featuresCount: state.features.length,
      storiesCount: state.stories.length,
      hasMermaid: !!state.mermaidCode
    });
    
    // Example Router navigation (if using Angular Router):
    // this.router.navigate(['/workspace'], { state });
  }
  
  /**
   * Check if workspace state is valid
   */
  isValidWorkspaceState(state: Partial<WorkspaceState>): boolean {
    return !!(
      state.features &&
      state.stories &&
      state.features.length > 0 &&
      state.stories.length > 0
    );
  }
}

/**
 * Workspace state interface for navigation
 */
export interface WorkspaceState {
  context: string;
  features: AgentFeatureSpec[];
  stories: AgentStorySpec[];
  mermaidCode?: string;
  visualization?: AgentVisualizationResponse;
  timestamp: number;
}

