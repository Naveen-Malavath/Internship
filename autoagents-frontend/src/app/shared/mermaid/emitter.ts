import { DiagramRoot, HldNode, HldEdge, LldClass, LldClassMember, DbdEntity, DbdRel, LldRel } from './ast';

const INIT_DIRECTIVE = '%%{init: {"theme":"base","flowchart":{"htmlLabels":true,"curve":"linear"}} }%%';

function kebabCase(s: string): string {
  return s
    .replace(/([a-z])([A-Z])/g, '$1_$2')
    .replace(/[^a-zA-Z0-9]+/g, '_')
    .toLowerCase()
    .replace(/^_+|_+$/g, '');
}

function sortAlpha<T>(arr: T[], key: (x: T) => string): T[] {
  return [...arr].sort((a, b) => key(a).localeCompare(key(b)));
}

export function emitHLD(root: DiagramRoot): string {
  if (!root.hld) {
    return `${INIT_DIRECTIVE}\nflowchart LR\n  A[No data]`;
  }

  const { nodes, edges } = root.hld;
  const lines: string[] = [INIT_DIRECTIVE, 'flowchart LR'];

  const nodesByGroup: Record<string, HldNode[]> = {};
  const ungrouped: HldNode[] = [];

  for (const node of nodes) {
    if (node.group) {
      if (!nodesByGroup[node.group]) {
        nodesByGroup[node.group] = [];
      }
      nodesByGroup[node.group].push(node);
    } else {
      ungrouped.push(node);
    }
  }

  const sortedGroups = Object.keys(nodesByGroup).sort();

  for (const group of sortedGroups) {
    lines.push(`  subgraph ${kebabCase(group)}["${group}"]`);
    const groupNodes = sortAlpha(nodesByGroup[group], n => n.id);
    for (const node of groupNodes) {
      lines.push(`    ${kebabCase(node.id)}["${node.label}"]`);
    }
    lines.push('  end');
  }

  const sortedUngrouped = sortAlpha(ungrouped, n => n.id);
  for (const node of sortedUngrouped) {
    lines.push(`  ${kebabCase(node.id)}["${node.label}"]`);
  }

  const sortedEdges = sortAlpha(edges, e => `${e.from}_${e.to}_${e.label || ''}`);
  for (const edge of sortedEdges) {
    const fromId = kebabCase(edge.from);
    const toId = kebabCase(edge.to);
    if (edge.label) {
      lines.push(`  ${fromId} -->|${edge.label}| ${toId}`);
    } else {
      lines.push(`  ${fromId} --> ${toId}`);
    }
  }

  return lines.join('\n');
}

function emitLldMember(m: LldClassMember): string {
  const vis = m.visibility || '+';
  
  if (m.kind === 'field') {
    const typeStr = m.type ? `: ${m.type}` : '';
    return `    ${vis}${m.name}${typeStr}`;
  }
  
  const paramsStr = m.params && m.params.length > 0
    ? m.params.map(p => `${p.name}${p.type ? ': ' + p.type : ''}`).join(', ')
    : '';
  const returnStr = m.returns ? `: ${m.returns}` : '';
  return `    ${vis}${m.name}(${paramsStr})${returnStr}`;
}

function emitLldRelation(rel: LldRel): string {
  const fromId = kebabCase(rel.from);
  const toId = kebabCase(rel.to);
  
  switch (rel.type) {
    case 'inherit':
      return `  ${toId} <|-- ${fromId}`;
    case 'assoc':
      return `  ${fromId} --> ${toId}`;
    case 'agg':
      return `  ${fromId} o-- ${toId}`;
    case 'comp':
      return `  ${fromId} *-- ${toId}`;
    case 'dep':
      return `  ${fromId} ..> ${toId}`;
    default:
      return `  ${fromId} --> ${toId}`;
  }
}

export function emitLLD(root: DiagramRoot): string {
  if (!root.lld) {
    return `${INIT_DIRECTIVE}\nclassDiagram\n  class Empty {\n  }`;
  }

  const { classes, rels } = root.lld;
  const lines: string[] = [INIT_DIRECTIVE, 'classDiagram'];

  const sortedClasses = sortAlpha(classes, c => c.name);

  for (const cls of sortedClasses) {
    lines.push(`  class ${cls.name} {`);
    
    const sortedMembers = sortAlpha(cls.members, m => m.name);
    for (const member of sortedMembers) {
      lines.push(emitLldMember(member));
    }
    
    lines.push('  }');
  }

  const sortedRels = sortAlpha(rels, r => `${r.from}_${r.type}_${r.to}`);
  for (const rel of sortedRels) {
    lines.push(emitLldRelation(rel));
  }

  return lines.join('\n');
}

function mapDbdFieldType(type: string): string {
  const normalized = type.toLowerCase();
  if (normalized.includes('uuid') || normalized.includes('guid')) return 'uuid';
  if (normalized.includes('int') || normalized.includes('number')) return 'int';
  if (normalized.includes('float') || normalized.includes('decimal')) return 'float';
  if (normalized.includes('bool')) return 'bool';
  if (normalized.includes('datetime') || normalized.includes('timestamp')) return 'datetime';
  if (normalized.includes('varchar')) return 'varchar';
  if (normalized.includes('json')) return 'json';
  if (normalized.includes('text')) return 'text';
  return 'string';
}

export function emitDBD(root: DiagramRoot): string {
  if (!root.dbd) {
    return `${INIT_DIRECTIVE}\nerDiagram\n  EMPTY {\n    string placeholder\n  }`;
  }

  const { entities, rels } = root.dbd;
  const lines: string[] = [INIT_DIRECTIVE, 'erDiagram'];

  const sortedRels = sortAlpha(rels, r => `${r.left}_${r.right}_${r.label || ''}`);
  for (const rel of sortedRels) {
    const labelPart = rel.label ? ` : ${rel.label}` : '';
    lines.push(`  ${rel.left} ${rel.cardLeft}--${rel.cardRight} ${rel.right}${labelPart}`);
  }

  if (rels.length > 0) {
    lines.push('');
  }

  const sortedEntities = sortAlpha(entities, e => e.name);
  for (const entity of sortedEntities) {
    lines.push(`  ${entity.name} {`);
    
    const sortedFields = sortAlpha(entity.fields, f => f.name);
    for (const field of sortedFields) {
      const mappedType = mapDbdFieldType(field.type);
      const constraint = field.constraint ? ` ${field.constraint}` : '';
      lines.push(`    ${mappedType} ${field.name}${constraint}`);
    }
    
    lines.push('  }');
  }

  return lines.join('\n');
}

