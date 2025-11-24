import { 
  DiagramRoot, 
  HldNode, 
  HldEdge, 
  LldClass, 
  LldClassMember,
  DbdEntity,
  DbdEntityField,
  DbdRel,
  LldRel
} from './ast';

function sanitizeName(name: string): string {
  if (!name || typeof name !== 'string') return '';
  return name
    .replace(/^[+\-#]+/, '')
    .replace(/[^\w\s]/g, '')
    .trim()
    .replace(/\s+/g, ' ');
}

function dedupeArray<T>(arr: T[], key: (x: T) => string): T[] {
  const seen = new Set<string>();
  const result: T[] = [];
  for (const item of arr) {
    const k = key(item);
    if (!seen.has(k)) {
      seen.add(k);
      result.push(item);
    }
  }
  return result;
}

export function buildHLD(context: string, stories: string[], features: string[]): DiagramRoot {
  const nodes: HldNode[] = [];
  const edges: HldEdge[] = [];

  nodes.push({ id: 'User', label: 'User/Client', group: 'Presentation' });
  nodes.push({ id: 'Frontend', label: 'Frontend Layer', group: 'Presentation' });
  nodes.push({ id: 'APIGateway', label: 'API Gateway', group: 'Application' });
  nodes.push({ id: 'Backend', label: 'Backend Services', group: 'Application' });
  nodes.push({ id: 'Database', label: 'Database', group: 'Data' });
  
  edges.push({ from: 'User', to: 'Frontend', label: 'interacts' });
  edges.push({ from: 'Frontend', to: 'APIGateway', label: 'requests' });
  edges.push({ from: 'APIGateway', to: 'Backend', label: 'routes' });
  edges.push({ from: 'Backend', to: 'Database', label: 'persists' });

  const groupMap: Record<string, string> = {
    auth: 'Security',
    account: 'Core',
    payment: 'Finance',
    notification: 'Communication',
    statement: 'Reporting',
    user: 'Identity',
    transaction: 'Finance',
    bill: 'Finance',
    report: 'Reporting',
    admin: 'Administration'
  };

  const seenFeatures = new Set<string>();

  if (features && Array.isArray(features)) {
    for (const feature of features) {
      const sanitized = sanitizeName(feature);
      if (!sanitized || seenFeatures.has(sanitized)) continue;
      seenFeatures.add(sanitized);

      let group = 'Core';
      const lower = sanitized.toLowerCase();
      for (const [keyword, grp] of Object.entries(groupMap)) {
        if (lower.includes(keyword)) {
          group = grp;
          break;
        }
      }

      const nodeId = `Feature_${sanitized.replace(/\s+/g, '_')}`;
      nodes.push({ id: nodeId, label: sanitized, group });
      edges.push({ from: 'Backend', to: nodeId, label: 'implements' });
    }
  }

  return {
    mode: 'hld',
    hld: { 
      nodes: dedupeArray(nodes, n => n.id), 
      edges: dedupeArray(edges, e => `${e.from}_${e.to}`) 
    }
  };
}

// ==================== LLD LOGIC ====================

function extractNouns(text: string): string[] {
  if (!text || typeof text !== 'string') return [];
  
  const common = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'be', 'been', 'are', 'were', 'have', 'has', 'had', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must']);
  
  const words = text.toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(w => w.length > 2 && !common.has(w));
  
  const capitalizedWords = (text.match(/\b[A-Z][a-z]+\b/g) || [])
    .map(w => w.toLowerCase());
  
  const verbList = ['create', 'update', 'delete', 'get', 'post', 'put', 'fetch', 'send', 'receive', 'process', 'handle', 'manage', 'add', 'remove', 'edit', 'view', 'list', 'search', 'filter', 'sort', 'validate', 'verify', 'authenticate', 'authorize', 'login', 'logout', 'register', 'submit', 'approve', 'reject', 'cancel', 'confirm'];
  
  const nouns = [...new Set([...capitalizedWords, ...words.filter(w => !verbList.includes(w))])];
  
  return nouns.slice(0, 10);
}

function extractVerbs(text: string): string[] {
  if (!text || typeof text !== 'string') return [];
  
  const actionVerbs = ['create', 'update', 'delete', 'get', 'fetch', 'list', 'search', 'find', 'add', 'remove', 'edit', 'save', 'load', 'send', 'receive', 'process', 'handle', 'manage', 'validate', 'verify', 'authenticate', 'authorize', 'login', 'logout', 'register', 'submit', 'approve', 'reject', 'cancel', 'confirm', 'generate', 'calculate', 'compute', 'check', 'view', 'display', 'show', 'hide', 'enable', 'disable', 'activate', 'deactivate'];
  
  const lower = text.toLowerCase();
  const foundVerbs: string[] = [];
  
  for (const verb of actionVerbs) {
    if (lower.includes(verb)) {
      foundVerbs.push(verb);
    }
  }
  
  return [...new Set(foundVerbs)];
}

function capitalizeFirst(str: string): string {
  if (!str || typeof str !== 'string') return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function extractEntitiesFromFeatures(features: string[]): Map<string, string[]> {
  const entityToActions = new Map<string, string[]>();
  
  if (!features || !Array.isArray(features)) {
    return entityToActions;
  }
  
  for (const feature of features) {
    if (!feature) continue;
    
    const sanitized = sanitizeName(feature);
    if (!sanitized) continue;
    
    const nouns = extractNouns(sanitized);
    const verbs = extractVerbs(sanitized);
    
    if (nouns.length === 0) {
      if (!entityToActions.has('App')) {
        entityToActions.set('App', []);
      }
      if (verbs.length > 0) {
        entityToActions.get('App')!.push(...verbs);
      } else {
        entityToActions.get('App')!.push('execute');
      }
      continue;
    }
    
    const primaryEntity = capitalizeFirst(nouns[0]);
    
    if (!entityToActions.has(primaryEntity)) {
      entityToActions.set(primaryEntity, []);
    }
    
    if (verbs.length > 0) {
      entityToActions.get(primaryEntity)!.push(...verbs);
    } else {
      entityToActions.get(primaryEntity)!.push('get', 'create');
    }
  }
  
  return entityToActions;
}

export function buildLLD(context: string, stories: string[], features: string[]): DiagramRoot {
  const classes: LldClass[] = [];
  const rels: LldRel[] = [];
  
  if (!features || !Array.isArray(features) || features.length === 0) {
    classes.push({
      name: 'ApplicationService',
      members: [
        { kind: 'method', name: 'initialize', visibility: '+', params: [], returns: 'void' },
        { kind: 'method', name: 'execute', visibility: '+', params: [], returns: 'void' }
      ]
    });
    
    return { mode: 'lld', lld: { classes, rels } };
  }
  
  const entityToActions = extractEntitiesFromFeatures(features);
  
  const safeContext = context || '';
  const safeStories = Array.isArray(stories) ? stories : [];
  const allText = [safeContext, ...features, ...safeStories].filter(t => t).join(' ');
  
  if (allText.trim()) {
    const contextNouns = extractNouns(allText);
    
    for (const noun of contextNouns.slice(0, 3)) {
      const entityName = capitalizeFirst(noun);
      if (entityName && !entityToActions.has(entityName)) {
        entityToActions.set(entityName, ['get', 'create', 'update']);
      }
    }
  }
  
  if (entityToActions.size === 0) {
    entityToActions.set('App', ['execute', 'process']);
  }
  
  for (const [entityName, actions] of entityToActions.entries()) {
    if (!entityName) continue;
    
    const members: LldClassMember[] = [];
    
    const repoName = `${entityName.toLowerCase()}Repository`;
    members.push({
      kind: 'field',
      name: repoName,
      type: 'Repository',
      visibility: '-'
    });
    
    const uniqueActions = [...new Set(actions)].filter(a => a);
    
    if (uniqueActions.length === 0) {
      uniqueActions.push('execute');
    }
    
    for (const action of uniqueActions.slice(0, 6)) {
      const methodName = action + entityName;
      members.push({
        kind: 'method',
        name: methodName,
        visibility: '+',
        params: [],
        returns: entityName
      });
    }
    
    classes.push({
      name: `${entityName}Service`,
      members
    });
  }
  
  if (classes.length > 1) {
    const maxRels = Math.min(classes.length - 1, 3);
    for (let i = 1; i <= maxRels; i++) {
      rels.push({
        from: classes[0].name,
        to: classes[i].name,
        type: 'assoc'
      });
    }
  }
  
  return { mode: 'lld', lld: { classes, rels } };
}

// ==================== DBD LOGIC ====================

function normalizeEntityName(name: string): string {
  if (!name || typeof name !== 'string') return '';
  
  const normalized = name
    .replace(/[^\w]/g, '_')
    .toUpperCase();
  
  if (normalized.length <= 5) {
    return normalized;
  }
  
  if (normalized.endsWith('S') && !normalized.endsWith('SS')) {
    return normalized.slice(0, -1);
  }
  
  return normalized;
}

function inferFieldsForEntity(entityName: string, context: string): DbdEntityField[] {
  const fields: DbdEntityField[] = [];
  const lower = (entityName || '').toLowerCase();
  
  fields.push({ name: 'id', type: 'uuid' });
  
  const commonFields = [
    { keywords: ['user', 'customer', 'client', 'person', 'member'], fields: ['name', 'email', 'phone', 'status'] },
    { keywords: ['order', 'purchase', 'transaction', 'payment'], fields: ['amount', 'status', 'date'] },
    { keywords: ['product', 'item', 'good'], fields: ['name', 'description', 'price', 'quantity'] },
    { keywords: ['account', 'profile'], fields: ['username', 'email', 'status', 'balance'] },
    { keywords: ['invoice', 'bill', 'statement'], fields: ['number', 'amount', 'date', 'status'] },
    { keywords: ['booking', 'reservation', 'appointment'], fields: ['date', 'time', 'status'] },
    { keywords: ['review', 'rating', 'feedback'], fields: ['rating', 'comment', 'date'] },
    { keywords: ['category', 'type', 'class'], fields: ['name', 'description'] }
  ];
  
  let matched = false;
  for (const pattern of commonFields) {
    for (const keyword of pattern.keywords) {
      if (lower.includes(keyword)) {
        for (const field of pattern.fields) {
          if (!fields.find(f => f.name === field)) {
            fields.push({ name: field, type: inferFieldType(field) });
          }
        }
        matched = true;
        break;
      }
    }
    if (matched) break;
  }
  
  if (fields.length === 1) {
    fields.push(
      { name: 'name', type: 'varchar' },
      { name: 'description', type: 'text' },
      { name: 'status', type: 'varchar' }
    );
  }
  
  fields.push(
    { name: 'created_at', type: 'datetime' },
    { name: 'updated_at', type: 'datetime' }
  );
  
  return fields.slice(0, 8);
}

function inferFieldType(fieldName: string): DbdEntityField['type'] {
  if (!fieldName || typeof fieldName !== 'string') return 'varchar';
  
  const lower = fieldName.toLowerCase();
  if (lower === 'id') return 'uuid';
  if (lower.endsWith('_id')) return 'uuid';
  if (lower.includes('email')) return 'varchar';
  if (lower.includes('name') || lower.includes('title')) return 'varchar';
  if (lower.includes('amount') || lower.includes('price') || lower.includes('balance')) return 'float';
  if (lower.includes('quantity') || lower.includes('count')) return 'int';
  if (lower.includes('number') && !lower.includes('phone')) return 'varchar';
  if (lower.includes('phone')) return 'varchar';
  if (lower.includes('created_at') || lower.includes('updated_at') || lower.includes('timestamp')) return 'datetime';
  if (lower.includes('date') || lower.includes('time')) return 'datetime';
  if (lower.includes('active') || lower.includes('enabled') || lower.includes('is_') || lower.includes('has_')) return 'bool';
  if (lower.includes('description') || lower.includes('comment') || lower.includes('notes') || lower.includes('content')) return 'text';
  if (lower.includes('status') || lower.includes('type') || lower.includes('category')) return 'varchar';
  if (lower.includes('rating') || lower.includes('score')) return 'int';
  if (lower.includes('metadata') || lower.includes('config') || lower.includes('settings')) return 'json';
  return 'varchar';
}

function findRelationships(entities: string[]): DbdRel[] {
  const rels: DbdRel[] = [];
  const seenRels = new Set<string>();
  
  if (!entities || !Array.isArray(entities) || entities.length < 2) {
    return rels;
  }
  
  const relationshipPatterns = [
    { parent: ['user', 'customer', 'client'], children: ['order', 'account', 'profile', 'booking', 'review'] },
    { parent: ['account', 'profile'], children: ['transaction', 'payment', 'statement'] },
    { parent: ['order', 'purchase'], children: ['item', 'product', 'payment'] },
    { parent: ['category', 'type'], children: ['product', 'item', 'post', 'article'] },
    { parent: ['product', 'service'], children: ['review', 'rating'] }
  ];
  
  for (let i = 0; i < entities.length; i++) {
    for (let j = i + 1; j < entities.length; j++) {
      const e1 = entities[i];
      const e2 = entities[j];
      
      if (!e1 || !e2) continue;
      
      const e1Lower = e1.toLowerCase();
      const e2Lower = e2.toLowerCase();
      
      for (const pattern of relationshipPatterns) {
        const e1IsParent = pattern.parent.some(p => e1Lower.includes(p));
        const e2IsChild = pattern.children.some(c => e2Lower.includes(c));
        
        if (e1IsParent && e2IsChild) {
          const relKey = `${e1}_${e2}`;
          if (!seenRels.has(relKey)) {
            rels.push({
              left: e1,
              right: e2,
              cardLeft: '||',
              cardRight: 'o{',
              label: 'has'
            });
            seenRels.add(relKey);
          }
          break;
        }
        
        const e2IsParent = pattern.parent.some(p => e2Lower.includes(p));
        const e1IsChild = pattern.children.some(c => e1Lower.includes(c));
        
        if (e2IsParent && e1IsChild) {
          const relKey = `${e2}_${e1}`;
          if (!seenRels.has(relKey)) {
            rels.push({
              left: e2,
              right: e1,
              cardLeft: '||',
              cardRight: 'o{',
              label: 'has'
            });
            seenRels.add(relKey);
          }
          break;
        }
      }
    }
  }
  
  return rels;
}

export function buildDBD(context: string, stories: string[], features: string[]): DiagramRoot {
  const entities: DbdEntity[] = [];
  const rels: DbdRel[] = [];
  
  if (!features || !Array.isArray(features) || features.length === 0) {
    const defaultEntity: DbdEntity = {
      name: 'APPLICATION_DATA',
      fields: [
        { name: 'id', type: 'uuid' },
        { name: 'name', type: 'varchar' },
        { name: 'value', type: 'text' },
        { name: 'created_at', type: 'datetime' }
      ]
    };
    entities.push(defaultEntity);
    return { mode: 'dbd', dbd: { entities, rels } };
  }
  
  const safeContext = context || '';
  const safeStories = Array.isArray(stories) ? stories : [];
  const allText = [safeContext, ...features, ...safeStories].filter(t => t).join(' ');
  
  if (!allText.trim()) {
    const defaultEntity: DbdEntity = {
      name: 'DATA',
      fields: [
        { name: 'id', type: 'uuid' },
        { name: 'value', type: 'varchar' },
        { name: 'created_at', type: 'datetime' }
      ]
    };
    entities.push(defaultEntity);
    return { mode: 'dbd', dbd: { entities, rels } };
  }
  
  const nouns = extractNouns(allText);
  
  const entityNames = new Set<string>();
  
  for (const noun of nouns.slice(0, 6)) {
    if (!noun) continue;
    const normalized = normalizeEntityName(noun);
    if (normalized && normalized.length > 2) {
      entityNames.add(normalized);
    }
  }
  
  if (entityNames.size === 0) {
    entityNames.add('USER');
    entityNames.add('DATA');
  }
  
  const entityList = Array.from(entityNames);
  
  for (const entityName of entityList) {
    if (!entityName) continue;
    const fields = inferFieldsForEntity(entityName, allText);
    entities.push({ name: entityName, fields });
  }
  
  const detectedRels = findRelationships(entityList);
  rels.push(...detectedRels);
  
  if (rels.length === 0 && entities.length > 1) {
    rels.push({
      left: entities[0].name,
      right: entities[1].name,
      cardLeft: '||',
      cardRight: 'o{',
      label: 'relates'
    });
  }
  
  return { mode: 'dbd', dbd: { entities, rels } };
}
