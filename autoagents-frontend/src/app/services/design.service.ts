import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

import { MermaidStyleConfig } from './mermaid-style.service';

export interface DesignResponse {
  _id: string;
  project_id: string;
  hld_mermaid: string;
  lld_mermaid: string;
  dbd_mermaid: string;
  style_config?: MermaidStyleConfig | null;
  created_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DesignService {
  private readonly apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  generateDesigns(projectId: string): Observable<DesignResponse> {
    return this.http.post<DesignResponse>(
      `${this.apiUrl}/projects/${projectId}/designs/generate`,
      {}
    );
  }

  getLatestDesigns(projectId: string): Observable<DesignResponse> {
    return this.http.get<DesignResponse>(
      `${this.apiUrl}/projects/${projectId}/designs`
    );
  }
}

