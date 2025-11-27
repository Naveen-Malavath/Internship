import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DbEntityView, DbdRel, AgentConnectionInfo } from '../../shared/mermaid/ast';

@Component({
  selector: 'app-dbd-table-view',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dbd-table-view.component.html',
  styleUrl: './dbd-table-view.component.scss',
})
export class DbdTableViewComponent {
  @Input() entities: DbEntityView[] = [];
  @Input() agentConnections?: AgentConnectionInfo;
  @Input() showAgentConnections = true;

  /**
   * Format cardinality for display
   */
  formatCardinality(card: string): string {
    switch (card) {
      case '||':
        return '1';
      case '|o':
      case 'o|':
        return '0..1';
      case '|{':
      case '}|':
        return 'N';
      case 'o{':
      case '}o':
        return '0..N';
      default:
        return card;
    }
  }

  /**
   * Format a relationship line for display
   * Example: "USER 1:N ORDER (places)"
   */
  formatRelationshipDisplay(rel: DbdRel, entityName: string): string {
    const leftCard = this.formatCardinality(rel.cardLeft);
    const rightCard = this.formatCardinality(rel.cardRight);
    const label = rel.label ? ` (${rel.label})` : '';
    
    // Show relationship from the perspective of the current entity
    if (rel.left === entityName) {
      return `${leftCard}:${rightCard} → ${rel.right}${label}`;
    } else {
      return `${rightCard}:${leftCard} ← ${rel.left}${label}`;
    }
  }

  /**
   * Get constraint display text
   */
  formatConstraint(constraint?: string): string {
    if (!constraint) return '';
    
    // Handle common constraint abbreviations
    const upperConstraint = constraint.toUpperCase();
    if (upperConstraint === 'PK') return 'Primary Key';
    if (upperConstraint === 'FK') return 'Foreign Key';
    if (upperConstraint === 'UK') return 'Unique';
    if (upperConstraint === 'NN' || upperConstraint === 'NOT NULL') return 'Not Null';
    
    return constraint;
  }

  /**
   * Get entity type badge class
   */
  getEntityTypeBadgeClass(entityType?: string): string {
    switch (entityType) {
      case 'primary':
        return 'dbd-entity-card__type-badge--primary';
      case 'secondary':
        return 'dbd-entity-card__type-badge--secondary';
      case 'junction':
        return 'dbd-entity-card__type-badge--junction';
      default:
        return '';
    }
  }

  /**
   * Format entity type for display
   */
  formatEntityType(entityType?: string): string {
    switch (entityType) {
      case 'primary':
        return 'Primary Entity';
      case 'secondary':
        return 'Supporting Entity';
      case 'junction':
        return 'Junction Table';
      default:
        return 'Entity';
    }
  }

  /**
   * Get count of linked features for an entity
   */
  getLinkedFeaturesCount(entity: DbEntityView): number {
    return entity.linkedFeatures?.length || 0;
  }

  /**
   * Get count of linked stories for an entity
   */
  getLinkedStoriesCount(entity: DbEntityView): number {
    return entity.linkedStories?.length || 0;
  }

  /**
   * Check if entity has agent connections
   */
  hasAgentConnections(entity: DbEntityView): boolean {
    return this.getLinkedFeaturesCount(entity) > 0 || this.getLinkedStoriesCount(entity) > 0;
  }

  /**
   * Get total field count across all entities
   */
  getTotalFieldCount(): number {
    return this.entities.reduce((sum, entity) => sum + (entity.fields?.length || 0), 0);
  }

  /**
   * Check if constraint matches a specific type (PK, FK, UK)
   */
  isConstraintType(constraint: string | undefined, type: string): boolean {
    return constraint?.toUpperCase() === type;
  }

  /**
   * Track entities by name for ngFor
   */
  trackByEntityName(_index: number, entity: DbEntityView): string {
    return entity.name;
  }

  /**
   * Track fields by name for ngFor
   */
  trackByFieldName(_index: number, field: { name: string }): string {
    return field.name;
  }

  /**
   * Track relationships by a composite key
   */
  trackByRelation(_index: number, rel: DbdRel): string {
    return `${rel.left}-${rel.cardLeft}-${rel.cardRight}-${rel.right}-${rel.label || ''}`;
  }

  /**
   * Track linked items by id
   */
  trackByLinkedId(_index: number, item: { id: string }): string {
    return item.id;
  }
}

