import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AgentVisualizationRequestPayload, AgentVisualizationResponse, AgentFeatureSpec, AgentStorySpec } from '../types';

/**
 * Agent-3 Service
 * 
 * Handles Mermaid diagram generation from features and stories
 */
@Injectable({
  providedIn: 'root'
})
export class Agent3Service {
  private readonly backendUrl = 'http://localhost:8000';
  
  constructor(private http: HttpClient) {}
  
  /**
   * Generate Mermaid diagram from context, stories, and features
   * 
   * @param payload - Context, features, stories, and diagram type
   * @returns Observable with visualization response containing Mermaid code
   */
  generateMermaid(payload: {
    context?: string;
    stories: AgentStorySpec[];
    features: AgentFeatureSpec[];
    diagramType?: 'hld' | 'lld' | 'database';
  }): Observable<AgentVisualizationResponse> {
    const requestPayload: AgentVisualizationRequestPayload = {
      prompt: payload.context || '',
      features: payload.features,
      stories: payload.stories,
      diagramType: payload.diagramType || 'hld'
    };
    
    console.log('[Agent3Service] Generating Mermaid diagram:', {
      diagramType: requestPayload.diagramType,
      featuresCount: payload.features.length,
      storiesCount: payload.stories.length
    });
    
    return this.http.post<AgentVisualizationResponse>(
      `${this.backendUrl}/agent/visualizer`,
      requestPayload
    );
  }
  
  /**
   * Generate multiple diagram types at once
   */
  generateAllDiagrams(payload: {
    context?: string;
    stories: AgentStorySpec[];
    features: AgentFeatureSpec[];
  }): Observable<{
    hld: AgentVisualizationResponse;
    lld: AgentVisualizationResponse;
    database: AgentVisualizationResponse;
  }> {
    // This would require backend support for batch generation
    // For now, we'll just return HLD
    throw new Error('Batch generation not yet implemented');
  }
}

