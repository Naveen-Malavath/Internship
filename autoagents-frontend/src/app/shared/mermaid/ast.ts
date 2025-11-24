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

export type DbdFieldType = 'string' | 'int' | 'float' | 'bool' | 'datetime' | 'uuid' | 'text' | 'number' | 'varchar' | 'json' | 'timestamp';

export interface DbdEntityField {
  name: string;
  type: DbdFieldType;
  constraint?: string;
}

export interface DbdEntity {
  name: string;
  fields: DbdEntityField[];
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

