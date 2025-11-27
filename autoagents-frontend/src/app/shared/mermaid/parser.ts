/**
 * Mermaid erDiagram Parser
 * Parses mermaid erDiagram text into DbdDiagram AST
 */

import { DbdDiagram, DbdEntity, DbdEntityField, DbdFieldType, DbdRel, DbdCardinality } from './ast';

/**
 * Parse mermaid erDiagram text into DbdDiagram AST
 */
export function parseErDiagram(mermaidText: string): DbdDiagram {
  const entities: DbdEntity[] = [];
  const rels: DbdRel[] = [];
  const entityMap = new Map<string, DbdEntity>();

  if (!mermaidText || typeof mermaidText !== 'string') {
    return { entities, rels };
  }

  // Normalize line endings and remove comments
  const lines = mermaidText
    .replace(/\r\n/g, '\n')
    .split('\n')
    .map(line => line.replace(/%%.*$/, '').trim())
    .filter(line => line.length > 0);

  let currentEntity: DbdEntity | null = null;
  let inEntityBlock = false;

  for (const line of lines) {
    // Skip directive lines (%%{init:...}%%) and diagram declaration
    if (line.startsWith('%%{') || line === 'erDiagram' || line.startsWith('erDiagram ')) {
      continue;
    }

    // Check for entity block start: ENTITY_NAME {
    const entityStartMatch = line.match(/^([A-Za-z_][A-Za-z0-9_]*)\s*\{$/);
    if (entityStartMatch) {
      const entityName = entityStartMatch[1];
      currentEntity = entityMap.get(entityName) || { name: entityName, fields: [] };
      if (!entityMap.has(entityName)) {
        entityMap.set(entityName, currentEntity);
        entities.push(currentEntity);
      }
      inEntityBlock = true;
      continue;
    }

    // Check for entity block end: }
    if (line === '}' && inEntityBlock) {
      currentEntity = null;
      inEntityBlock = false;
      continue;
    }

    // Parse field inside entity block: type fieldName [constraint]
    if (inEntityBlock && currentEntity) {
      const fieldMatch = line.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s+(.+))?$/);
      if (fieldMatch) {
        const [, rawType, fieldName, constraint] = fieldMatch;
        const fieldType = mapFieldType(rawType);
        const field: DbdEntityField = {
          name: fieldName,
          type: fieldType,
        };
        if (constraint) {
          field.constraint = constraint.trim();
        }
        currentEntity.fields.push(field);
      }
      continue;
    }

    // Parse relationship line: ENTITY1 cardinality--cardinality ENTITY2 : label
    // Examples: USER ||--o{ ORDER : places
    //           PRODUCT }|--|{ ORDER
    const relMatch = line.match(
      /^([A-Za-z_][A-Za-z0-9_]*)\s+(\|\||[|o}\{]{1,2})--(\|\||[|o}\{]{1,2})\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*:\s*(.+))?$/
    );
    if (relMatch) {
      const [, leftEntity, cardLeftRaw, cardRightRaw, rightEntity, label] = relMatch;
      
      const cardLeft = parseCardinality(cardLeftRaw);
      const cardRight = parseCardinality(cardRightRaw);
      
      const rel: DbdRel = {
        left: leftEntity,
        right: rightEntity,
        cardLeft,
        cardRight,
      };
      if (label) {
        rel.label = label.trim();
      }
      rels.push(rel);

      // Also ensure entities exist in the map (may be defined only via relationships)
      if (!entityMap.has(leftEntity)) {
        const entity: DbdEntity = { name: leftEntity, fields: [] };
        entityMap.set(leftEntity, entity);
        entities.push(entity);
      }
      if (!entityMap.has(rightEntity)) {
        const entity: DbdEntity = { name: rightEntity, fields: [] };
        entityMap.set(rightEntity, entity);
        entities.push(entity);
      }
    }
  }

  return { entities, rels };
}

/**
 * Map mermaid field type string to DbdFieldType
 */
function mapFieldType(rawType: string): DbdFieldType {
  const normalized = rawType.toLowerCase();
  
  switch (normalized) {
    case 'string':
    case 'varchar':
      return 'varchar';
    case 'int':
    case 'integer':
      return 'int';
    case 'float':
    case 'double':
    case 'decimal':
      return 'float';
    case 'bool':
    case 'boolean':
      return 'bool';
    case 'datetime':
    case 'date':
    case 'time':
      return 'datetime';
    case 'timestamp':
      return 'timestamp';
    case 'uuid':
      return 'uuid';
    case 'text':
      return 'text';
    case 'number':
      return 'number';
    case 'json':
    case 'jsonb':
      return 'json';
    default:
      return 'varchar';
  }
}

/**
 * Parse cardinality notation to DbdCardinality type
 */
function parseCardinality(raw: string): DbdCardinality {
  // Normalize the cardinality string
  const card = raw.trim();
  
  switch (card) {
    case '||':
      return '||';
    case '|o':
    case 'o|':
      return card as DbdCardinality;
    case '|{':
    case '}|':
      return card as DbdCardinality;
    case 'o{':
    case '}o':
      return card as DbdCardinality;
    default:
      // Default to one-to-one if unrecognized
      return '||';
  }
}

/**
 * Format a relationship for display
 * Example: "USER ||--o{ ORDER : places" -> "1:N places"
 */
export function formatRelationship(rel: DbdRel): string {
  const cardinalityDesc = getCardinalityDescription(rel.cardLeft, rel.cardRight);
  const label = rel.label ? ` (${rel.label})` : '';
  return `${rel.left} ${cardinalityDesc} ${rel.right}${label}`;
}

/**
 * Get human-readable cardinality description
 */
function getCardinalityDescription(left: DbdCardinality, right: DbdCardinality): string {
  const leftDesc = cardinalityToSymbol(left);
  const rightDesc = cardinalityToSymbol(right);
  return `${leftDesc}:${rightDesc}`;
}

/**
 * Convert cardinality to simple symbol (1, 0..1, N, 0..N)
 */
function cardinalityToSymbol(card: DbdCardinality): string {
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
      return '?';
  }
}

