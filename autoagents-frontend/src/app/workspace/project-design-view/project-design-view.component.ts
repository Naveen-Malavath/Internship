import { CommonModule } from '@angular/common';
import { Component, Input, OnInit, OnChanges, SimpleChanges, inject } from '@angular/core';
import { WorkspaceViewComponent } from '../workspace-view.component';
import { DbdTableViewComponent } from '../dbd-table-view/dbd-table-view.component';
import { DesignService, DesignResponse } from '../../services/design.service';
import { MermaidStyleConfig } from '../../services/mermaid-style.service';
import { DbEntityView, DbdRel } from '../../shared/mermaid/ast';
import { parseErDiagram } from '../../shared/mermaid/parser';
import { buildLLD } from '../../shared/mermaid/builders';
import { emitLLD } from '../../shared/mermaid/emitter';

/**
 * Approved feature structure (simplified from WizardFeature)
 */
export interface ApprovedFeature {
  summary: string;
  approved: boolean;
}

/**
 * Approved story structure (simplified from WizardStory)
 */
export interface ApprovedStory {
  featureTitle: string;
  userStory: string;
  approved: boolean;
}

@Component({
  selector: 'app-project-design-view',
  standalone: true,
  imports: [CommonModule, WorkspaceViewComponent, DbdTableViewComponent],
  templateUrl: './project-design-view.component.html',
  styleUrl: './project-design-view.component.scss',
})
export class ProjectDesignViewComponent implements OnInit, OnChanges {
  @Input() projectId!: string;
  @Input() approvedFeatures: ApprovedFeature[] = [];
  @Input() approvedStories: ApprovedStory[] = [];

  private readonly designService = inject(DesignService);
  protected designGenerationCounter = 0; // Track design generations to force cache refresh

  protected currentDesignType: 'HLD' | 'LLD' | 'DBD' = 'LLD';
  protected dbdViewMode: 'graph' | 'table' = 'graph';
  protected designs: DesignResponse | null = null;
  protected currentMermaid: string | null = null;
  protected currentStyleConfig: MermaidStyleConfig | null = null;
  protected isLoadingDesigns = false;
  protected error: string | null = null;
  protected hasNoDesigns = false;
  protected dbEntities: DbEntityView[] = [];

  ngOnInit(): void {
    if (this.projectId) {
      this.loadDesigns();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    // When DBD mermaid or approved features change, rebuild entity views
    if (changes['approvedFeatures'] || changes['approvedStories']) {
      this.updateDbEntities();
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
        
        // Update DB entities for table view
        this.updateDbEntities();
        
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

    // When switching to DBD, update the entity views for table mode
    if (type === 'DBD') {
      this.updateDbEntities();
    }
  }

  /**
   * Helper method to safely get mermaid string for a given type.
   * Returns null if the mermaid string is empty or undefined.
   * For LLD, always generates flowchart-style architecture diagram (same style as HLD).
   */
  private getMermaidForType(type: 'HLD' | 'LLD' | 'DBD', designs: DesignResponse): string | null {
    let mermaid: string | undefined;
    switch (type) {
      case 'HLD':
        mermaid = designs.hld_mermaid;
        break;
      case 'LLD':
        // Always generate flowchart-style LLD using our architecture builder
        // This matches the HLD visual style (same layout, colors, subgraphs)
        mermaid = this.generateFlowchartLLD();
        break;
      case 'DBD':
        mermaid = designs.dbd_mermaid;
        break;
    }
    // Return null for empty/undefined strings, not empty string
    return mermaid && mermaid.trim() !== '' ? mermaid : null;
  }

  /**
   * Generate flowchart-style LLD architecture diagram.
   * Uses the same visual style as HLD (flowchart with subgraphs and layers).
   */
  private generateFlowchartLLD(): string {
    // Extract feature titles and story texts from approved items
    const featureTitles = this.approvedFeatures
      .filter(f => f.approved)
      .map(f => f.summary || '');
    
    const storyTexts = this.approvedStories
      .filter(s => s.approved)
      .map(s => s.userStory || '');

    // Build LLD using our architecture builder
    const root = buildLLD('', storyTexts, featureTitles);
    return emitLLD(root);
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
        
        // Update DB entities for table view
        this.updateDbEntities();
        
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
          // Update DB entities when DBD mermaid changes
          this.updateDbEntities();
          break;
      }
    }
  }

  /**
   * Toggle DBD view mode between graph and table
   */
  protected onDbdViewModeChange(mode: 'graph' | 'table'): void {
    this.dbdViewMode = mode;
    if (mode === 'table') {
      this.updateDbEntities();
    }
  }

  /**
   * Parse DBD mermaid text and build DbEntityView array with approval status
   */
  private updateDbEntities(): void {
    const dbdMermaid = this.designs?.dbd_mermaid;
    if (!dbdMermaid) {
      this.dbEntities = [];
      return;
    }

    // Parse the mermaid erDiagram text
    const diagram = parseErDiagram(dbdMermaid);
    
    // Build approved keywords from features and stories
    const approvedKeywords = this.buildApprovedKeywords();

    // Convert to DbEntityView with relationships and approval status
    this.dbEntities = diagram.entities.map(entity => {
      // Find all relationships involving this entity
      const relationships: DbdRel[] = diagram.rels.filter(
        rel => rel.left === entity.name || rel.right === entity.name
      );

      // Determine if this entity is approved based on feature/story keywords
      const approved = this.isEntityApproved(entity.name, approvedKeywords);

      return {
        name: entity.name,
        fields: entity.fields,
        relationships,
        approved,
      };
    });
  }

  /**
   * Build a set of keywords from approved features and stories
   */
  private buildApprovedKeywords(): Set<string> {
    const keywords = new Set<string>();

    // Add keywords from approved features
    for (const feature of this.approvedFeatures) {
      if (feature.approved && feature.summary) {
        // Extract words from the feature summary
        const words = this.extractKeywords(feature.summary);
        words.forEach(word => keywords.add(word));
      }
    }

    // Add keywords from approved stories
    for (const story of this.approvedStories) {
      if (story.approved) {
        if (story.featureTitle) {
          const words = this.extractKeywords(story.featureTitle);
          words.forEach(word => keywords.add(word));
        }
        if (story.userStory) {
          const words = this.extractKeywords(story.userStory);
          words.forEach(word => keywords.add(word));
        }
      }
    }

    return keywords;
  }

  /**
   * Extract meaningful keywords from text (nouns, likely entity names)
   */
  private extractKeywords(text: string): string[] {
    if (!text) return [];
    
    // Split by non-word characters and filter
    return text
      .split(/[\s,.\-_:;!?()[\]{}'"]+/)
      .map(word => word.toLowerCase().trim())
      .filter(word => word.length > 2); // Only words with 3+ characters
  }

  /**
   * Check if an entity name matches any approved keywords
   */
  private isEntityApproved(entityName: string, approvedKeywords: Set<string>): boolean {
    if (approvedKeywords.size === 0) {
      return false;
    }

    const normalizedName = entityName.toLowerCase().replace(/_/g, '');
    
    // Check if entity name matches any keyword
    for (const keyword of approvedKeywords) {
      if (normalizedName.includes(keyword) || keyword.includes(normalizedName)) {
        return true;
      }
    }

    // Also check individual words in the entity name (for names like USER_ACCOUNT)
    const entityWords = entityName.toLowerCase().split('_');
    for (const word of entityWords) {
      if (word.length > 2 && approvedKeywords.has(word)) {
        return true;
      }
    }

    return false;
  }
}

