import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, inject } from '@angular/core';
import { WorkspaceViewComponent } from '../workspace-view.component';
import { DesignService, DesignResponse } from '../../services/design.service';
import { MermaidStyleConfig } from '../../services/mermaid-style.service';

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
  protected designGenerationCounter = 0; // Track design generations to force cache refresh

  protected currentDesignType: 'HLD' | 'LLD' | 'DBD' = 'LLD';
  protected designs: DesignResponse | null = null;
  protected currentMermaid: string | null = null;
  protected currentStyleConfig: MermaidStyleConfig | null = null;
  protected isLoadingDesigns = false;
  protected error: string | null = null;
  protected hasNoDesigns = false;

  ngOnInit(): void {
    if (this.projectId) {
      this.loadDesigns();
    }
  }

  private loadDesigns(): void {
    // Set loading flag but do NOT change currentMermaid
    this.isLoadingDesigns = true;
    this.error = null;
    this.hasNoDesigns = false;

    this.designService.getLatestDesigns(this.projectId).subscribe({
      next: (designs) => {
        // Update stored designs first
        this.designs = designs;
        
        // Only update currentMermaid after successful response
        // Use helper method to get mermaid for current type, preserving existing if not available
        const mermaidForType = this.getMermaidForType(this.currentDesignType, designs);
        if (mermaidForType !== null) {
          this.currentMermaid = mermaidForType;
        }
        // If no mermaid for current type, try LLD as fallback
        if (this.currentMermaid === null && designs.lld_mermaid) {
          this.currentMermaid = designs.lld_mermaid;
          this.currentDesignType = 'LLD';
        }
        
        // Update style config (convert undefined to null)
        this.currentStyleConfig = designs.style_config ?? null;
        
        this.isLoadingDesigns = false;
      },
      error: (err) => {
        // On error, show error message but do NOT clear currentMermaid
        this.isLoadingDesigns = false;
        if (err.status === 404) {
          this.hasNoDesigns = true;
          this.error = null;
        } else {
          this.error = err.message || 'Failed to load designs';
        }
        // currentMermaid remains unchanged - last diagram stays visible
      },
    });
  }

  protected onDesignTypeChange(type: 'HLD' | 'LLD' | 'DBD'): void {
    if (!this.designs) {
      return;
    }

    this.currentDesignType = type;

    // Get mermaid for the selected type, preserving currentMermaid if not available
    const mermaidForType = this.getMermaidForType(type, this.designs);
    if (mermaidForType !== null) {
      this.currentMermaid = mermaidForType;
    }
    // If no mermaid for selected type, keep currentMermaid unchanged
  }

  /**
   * Helper method to safely get mermaid string for a given type.
   * Returns null if the mermaid string is empty or undefined.
   */
  private getMermaidForType(type: 'HLD' | 'LLD' | 'DBD', designs: DesignResponse): string | null {
    let mermaid: string | undefined;
    switch (type) {
      case 'HLD':
        mermaid = designs.hld_mermaid;
        break;
      case 'LLD':
        mermaid = designs.lld_mermaid;
        break;
      case 'DBD':
        mermaid = designs.dbd_mermaid;
        break;
    }
    // Return null for empty/undefined strings, not empty string
    return mermaid && mermaid.trim() !== '' ? mermaid : null;
  }

  protected onGenerateDesigns(): void {
    if (!this.projectId || this.isLoadingDesigns) {
      console.warn(`[project-design-view] Cannot generate designs: projectId=${this.projectId}, isLoading=${this.isLoadingDesigns}`);
      return;
    }

    console.log(`[project-design-view] Generating designs for project ${this.projectId}`);
    
    // Set loading flag but do NOT change currentMermaid
    this.isLoadingDesigns = true;
    this.error = null;
    this.hasNoDesigns = false;

    const startTime = performance.now();
    
    this.designService.generateDesigns(this.projectId).subscribe({
      next: (designs) => {
        const elapsed = performance.now() - startTime;
        console.log(`[project-design-view] Designs generated successfully in ${elapsed.toFixed(2)}ms`, {
          hasHLD: !!designs.hld_mermaid,
          hasLLD: !!designs.lld_mermaid,
          hasDBD: !!designs.dbd_mermaid,
          hldLength: designs.hld_mermaid?.length || 0,
          lldLength: designs.lld_mermaid?.length || 0,
          dbdLength: designs.dbd_mermaid?.length || 0,
        });
        
        // Increment generation counter to signal cache invalidation
        this.designGenerationCounter++;
        console.log(`[project-design-view] Design generation counter: ${this.designGenerationCounter}`);
        
        // Update stored designs first
        this.designs = designs;
        
        // Only update currentMermaid after successful response
        // Use helper method to get mermaid for current type
        const mermaidForType = this.getMermaidForType(this.currentDesignType, designs);
        if (mermaidForType !== null) {
          this.currentMermaid = mermaidForType;
          console.log(`[project-design-view] Updated currentMermaid for type ${this.currentDesignType} (${mermaidForType.length} chars)`);
        }
        // If no mermaid for current type, try LLD as fallback
        if (this.currentMermaid === null && designs.lld_mermaid) {
          this.currentMermaid = designs.lld_mermaid;
          this.currentDesignType = 'LLD';
          console.log(`[project-design-view] Fallback to LLD diagram`);
        }
        
        // Update style config (convert undefined to null)
        this.currentStyleConfig = designs.style_config ?? null;
        
        this.isLoadingDesigns = false;
      },
      error: (err) => {
        const elapsed = performance.now() - startTime;
        console.error(`[project-design-view] Failed to generate designs after ${elapsed.toFixed(2)}ms:`, err);
        
        // On error, show error message but do NOT clear currentMermaid
        this.isLoadingDesigns = false;
        const errorMessage = err.error?.detail || err.message || 'Failed to generate designs';
        this.error = errorMessage;
        console.error(`[project-design-view] Error details:`, {
          status: err.status,
          statusText: err.statusText,
          message: errorMessage,
        });
        // currentMermaid remains unchanged - last diagram stays visible
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

