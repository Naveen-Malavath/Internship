import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Request/Response DTOs for Narrow V1 (single module)
export interface CodingRequestDto {
  moduleName: string;
  dbdMermaid: string;
  apiMermaid: string;
  stories: string[];
}

export interface GeneratedFileDto {
  path: string;
  content: string;
}

export interface CodingResponseDto {
  files: GeneratedFileDto[];
}

// Request DTO for Full Backend Project (ZIP download)
export interface FullBackendRequestDto {
  projectName: string;
  dbdMermaid: string;
  apiMermaid: string;
  stories: string[];
}

// Request DTO for Full Project (Backend + Frontend ZIP download)
export interface FullProjectRequestDto {
  projectName: string;
  dbdMermaid: string;
  apiMermaid: string;
  stories: string[];
  wireframes: string[];
}

// Request DTO for Full Frontend Project (returns JSON, not ZIP)
export interface FullFrontendRequestDto {
  projectName: string;
  wireframes: string[];
  apiMermaid: string;
  stories: string[];
  mermaidDiagrams?: {
    hld?: string;
    lld?: string;
    dbd?: string;
    api?: string;
    component?: string;
    sequence?: string;
    dfd?: string;
  };
}

@Injectable({ providedIn: 'root' })
export class CodeGenerationService {
  // Use same URL pattern as existing ApiService
  private apiUrl = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

  constructor(private http: HttpClient) {}

  /**
   * Generate backend module code (models, schemas, routes) from Mermaid diagrams and stories.
   * Narrow V1: Single module generation only.
   */
  generateModule(request: CodingRequestDto): Observable<CodingResponseDto> {
    return this.http.post<CodingResponseDto>(
      `${this.apiUrl}/api/coding/generate-module`,
      {
        module_name: request.moduleName,
        dbd_mermaid: request.dbdMermaid,
        api_mermaid: request.apiMermaid,
        stories: request.stories
      }
    );
  }

  /**
   * Generate full backend project and download as ZIP.
   * Returns the ZIP file as a Blob for browser download.
   */
  generateFullBackendZip(request: FullBackendRequestDto): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/api/coding/generate-backend-project-zip`,
      {
        project_name: request.projectName,
        dbd_mermaid: request.dbdMermaid,
        api_mermaid: request.apiMermaid,
        stories: request.stories
      },
      {
        responseType: 'blob' as 'json'
      }
    ) as Observable<Blob>;
  }

  /**
   * Generate full project (backend + frontend) and download as ZIP.
   * Returns the ZIP file as a Blob for browser download.
   */
  generateFullProjectZip(request: FullProjectRequestDto): Observable<Blob> {
    return this.http.post(
      `${this.apiUrl}/api/coding/generate-full-project-zip`,
      {
        project_name: request.projectName,
        dbd_mermaid: request.dbdMermaid,
        api_mermaid: request.apiMermaid,
        stories: request.stories,
        wireframes: request.wireframes
      },
      {
        responseType: 'blob' as 'json'
      }
    ) as Observable<Blob>;
  }

  /**
   * Generate full Angular frontend project from wireframes, diagrams, and stories.
   * Returns JSON with generated files (not ZIP).
   */
  generateFrontendProject(request: FullFrontendRequestDto): Observable<CodingResponseDto> {
    return this.http.post<CodingResponseDto>(
      `${this.apiUrl}/api/coding/generate-frontend-project`,
      {
        project_name: request.projectName,
        wireframes: request.wireframes,
        api_mermaid: request.apiMermaid,
        stories: request.stories,
        mermaid_diagrams: request.mermaidDiagrams
      }
    );
  }
}

