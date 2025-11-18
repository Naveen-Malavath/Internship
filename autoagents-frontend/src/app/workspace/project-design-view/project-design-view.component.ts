import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, inject } from '@angular/core';
import { WorkspaceViewComponent } from '../workspace-view.component';
import { DesignService, DesignResponse } from '../../services/design.service';

@Component({
  selector: 'app-project-design-view',
  standalone: true,
  imports: [CommonModule, WorkspaceViewComponent],
  templateUrl: './project-design-view.component.html',
  styleUrl: './project-design-view.component.scss',
})
export class ProjectDesignViewComponent implements OnInit {
  @Input() projectId!: string;

  private readonly designService = inject(DesignService);

  protected currentDesignType: 'HLD' | 'LLD' | 'DBD' = 'LLD';
  protected designs: DesignResponse | null = null;
  protected currentMermaid: string = '';
  protected isLoading = false;
  protected isGenerating = false;
  protected error: string | null = null;
  protected hasNoDesigns = false;

  ngOnInit(): void {
    if (this.projectId) {
      this.loadDesigns();
    }
  }

  private loadDesigns(): void {
    this.isLoading = true;
    this.error = null;
    this.hasNoDesigns = false;

    this.designService.getLatestDesigns(this.projectId).subscribe({
      next: (designs) => {
        this.designs = designs;
        this.currentMermaid = designs.lld_mermaid || '';
        this.currentDesignType = 'LLD';
        this.isLoading = false;
      },
      error: (err) => {
        this.isLoading = false;
        if (err.status === 404) {
          this.hasNoDesigns = true;
          this.error = null;
        } else {
          this.error = err.message || 'Failed to load designs';
        }
      },
    });
  }

  protected onDesignTypeChange(type: 'HLD' | 'LLD' | 'DBD'): void {
    if (!this.designs) {
      return;
    }

    this.currentDesignType = type;

    switch (type) {
      case 'HLD':
        this.currentMermaid = this.designs.hld_mermaid || '';
        break;
      case 'LLD':
        this.currentMermaid = this.designs.lld_mermaid || '';
        break;
      case 'DBD':
        this.currentMermaid = this.designs.dbd_mermaid || '';
        break;
    }
  }

  protected onGenerateDesigns(): void {
    if (!this.projectId || this.isGenerating) {
      return;
    }

    this.isGenerating = true;
    this.error = null;
    this.hasNoDesigns = false;

    this.designService.generateDesigns(this.projectId).subscribe({
      next: (designs) => {
        this.designs = designs;
        this.currentMermaid = designs.lld_mermaid || '';
        this.currentDesignType = 'LLD';
        this.isGenerating = false;
      },
      error: (err) => {
        this.isGenerating = false;
        this.error = err.error?.detail || err.message || 'Failed to generate designs';
      },
    });
  }

  protected onMermaidChange(mermaid: string): void {
    // Update the current mermaid source when user edits
    this.currentMermaid = mermaid;
    
    // Optionally update the designs object if you want to track edits
    if (this.designs) {
      switch (this.currentDesignType) {
        case 'HLD':
          this.designs.hld_mermaid = mermaid;
          break;
        case 'LLD':
          this.designs.lld_mermaid = mermaid;
          break;
        case 'DBD':
          this.designs.dbd_mermaid = mermaid;
          break;
      }
    }
  }
}

