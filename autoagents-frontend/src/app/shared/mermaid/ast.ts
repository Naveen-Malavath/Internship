export type DiagramMode = 'hld' | 'lld' | 'dbd';

export interface HldNode {
  id: string;
  label: string;
  group?: string;
}

export interface HldEdge {
  from: string;
  to: string;
  label?: string;
}

export type LldMemberKind = 'field' | 'method';

export type LldVisibility = '+' | '-' | '#';

export interface LldMethodParam {
  name: string;
  type?: string;
}

export interface LldClassMember {
  kind: LldMemberKind;
  name: string;
  type?: string;
  visibility?: LldVisibility;
  params?: LldMethodParam[];
  returns?: string;
}

export interface LldClass {
  name: string;
  members: LldClassMember[];
  stereotypes?: string[];
}

export type LldRelType = 'inherit' | 'assoc' | 'agg' | 'comp' | 'dep';

export interface LldRel {
  from: string;
  to: string;
  type: LldRelType;
}

// LLD Architecture types for flowchart-style diagrams (same visual style as HLD)
export type LldArchLayer = 'frontend' | 'backend' | 'database' | 'integration' | 'infrastructure';

export interface LldArchNode {
  id: string;
  label: string;
  layer: LldArchLayer;
  type?: 'component' | 'service' | 'repository' | 'controller' | 'model' | 'gateway' | 'database' | 'cache';
}

export interface LldArchEdge {
  from: string;
  to: string;
  label?: string;
}

export interface LldArchDiagram {
  nodes: LldArchNode[];
  edges: LldArchEdge[];
}

export type DbdFieldType = 'string' | 'int' | 'float' | 'bool' | 'datetime' | 'uuid' | 'text' | 'number' | 'varchar' | 'json' | 'timestamp';

export interface DbdEntityField {
  name: string;
  type: DbdFieldType;
  constraint?: string;
  description?: string;
}

export interface DbdEntity {
  name: string;
  fields: DbdEntityField[];
  description?: string;
  entityType?: 'primary' | 'secondary' | 'junction';
  /** Feature IDs that reference this entity (e.g., ['F1', 'F2']) */
  featureSources?: string[];
  /** Story IDs that reference this entity (e.g., ['S1', 'S2']) */
  storySources?: string[];
}

export type DbdCardinality = '||' | '|o' | 'o|' | '|{' | '}|' | 'o{' | '}o';

export interface DbdRel {
  left: string;
  right: string;
  cardLeft: DbdCardinality;
  cardRight: DbdCardinality;
  label?: string;
}

export interface HldDiagram {
  nodes: HldNode[];
  edges: HldEdge[];
}

export interface LldDiagram {
  classes: LldClass[];
  rels: LldRel[];
  // Architecture diagram data (flowchart style like HLD)
  arch?: LldArchDiagram;
}

export interface DbdDiagram {
  entities: DbdEntity[];
  rels: DbdRel[];
}

export interface DiagramRoot {
  mode: DiagramMode;
  hld?: HldDiagram;
  lld?: LldDiagram;
  dbd?: DbdDiagram;
}

/**
 * View model for displaying a database entity in table format
 * Used by the DBD Table View component
 */
export interface DbEntityView {
  name: string;
  fields: DbdEntityField[];
  relationships: DbdRel[];  // Relationships where this entity is involved (left or right)
  approved?: boolean;       // Whether this entity is from an approved feature/story
  description?: string;     // Entity description
  entityType?: 'primary' | 'secondary' | 'junction';  // Entity classification
  /** Features from Agent-1 that map to this entity */
  linkedFeatures?: { id: string; text: string }[];
  /** Stories from Agent-2 that map to this entity */
  linkedStories?: { id: string; text: string }[];
}

/**
 * Metadata for Agent-1 features and Agent-2 stories connection
 */
export interface AgentConnectionInfo {
  agent1Features: { id: string; text: string; entities: string[] }[];
  agent2Stories: { id: string; text: string; entities: string[] }[];
}

