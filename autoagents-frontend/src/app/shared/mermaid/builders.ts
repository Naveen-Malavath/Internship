import { 
  DiagramRoot, 
  HldNode, 
  HldEdge, 
  LldClass, 
  LldClassMember,
  DbdEntity,
  DbdEntityField,
  DbdRel,
  LldRel,
  LldArchNode,
  LldArchEdge,
  LldArchDiagram,
  LldArchLayer
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

/**
 * Determine the layer for a component based on its name
 */
function inferLayer(name: string): LldArchLayer {
  const lower = name.toLowerCase();
  
  // Frontend layer
  if (lower.includes('component') || lower.includes('view') || lower.includes('page') || 
      lower.includes('ui') || lower.includes('form') || lower.includes('dialog') ||
      lower.includes('modal') || lower.includes('widget') || lower.includes('panel')) {
    return 'frontend';
  }
  
  // Database layer
  if (lower.includes('repository') || lower.includes('dao') || lower.includes('model') ||
      lower.includes('entity') || lower.includes('schema') || lower.includes('database') ||
      lower.includes('db') || lower.includes('store') || lower.includes('cache')) {
    return 'database';
  }
  
  // Integration layer
  if (lower.includes('gateway') || lower.includes('api') || lower.includes('client') ||
      lower.includes('adapter') || lower.includes('external') || lower.includes('integration') ||
      lower.includes('webhook') || lower.includes('connector')) {
    return 'integration';
  }
  
  // Infrastructure layer
  if (lower.includes('config') || lower.includes('logger') || lower.includes('util') ||
      lower.includes('helper') || lower.includes('middleware') || lower.includes('interceptor') ||
      lower.includes('guard') || lower.includes('pipe')) {
    return 'infrastructure';
  }
  
  // Default to backend
  return 'backend';
}

/**
 * Build LLD as an architecture diagram (flowchart style like HLD)
 * Groups components into layers: frontend, backend, database, integration
 */
export function buildLLD(context: string, stories: string[], features: string[]): DiagramRoot {
  const nodes: LldArchNode[] = [];
  const edges: LldArchEdge[] = [];
  const classes: LldClass[] = [];
  const rels: LldRel[] = [];
  
  // Always add core infrastructure nodes
  nodes.push({ id: 'AppModule', label: 'App Module', layer: 'frontend', type: 'component' });
  nodes.push({ id: 'RouterModule', label: 'Router Module', layer: 'frontend', type: 'component' });
  nodes.push({ id: 'APIGateway', label: 'API Gateway', layer: 'integration', type: 'gateway' });
  nodes.push({ id: 'AuthService', label: 'Auth Service', layer: 'backend', type: 'service' });
  nodes.push({ id: 'ConfigService', label: 'Config Service', layer: 'infrastructure', type: 'service' });
  nodes.push({ id: 'LoggerService', label: 'Logger Service', layer: 'infrastructure', type: 'service' });
  
  // Core edges for infrastructure
  edges.push({ from: 'AppModule', to: 'RouterModule', label: 'imports' });
  edges.push({ from: 'RouterModule', to: 'APIGateway', label: 'routes to' });
  edges.push({ from: 'APIGateway', to: 'AuthService', label: 'authenticates' });
  
  if (!features || !Array.isArray(features) || features.length === 0) {
    // Add default components
    nodes.push({ id: 'HomeComponent', label: 'Home Component', layer: 'frontend', type: 'component' });
    nodes.push({ id: 'AppService', label: 'App Service', layer: 'backend', type: 'service' });
    nodes.push({ id: 'DataRepository', label: 'Data Repository', layer: 'database', type: 'repository' });
    nodes.push({ id: 'Database', label: 'Database', layer: 'database', type: 'database' });
    
    edges.push({ from: 'RouterModule', to: 'HomeComponent', label: 'navigates' });
    edges.push({ from: 'HomeComponent', to: 'AppService', label: 'calls' });
    edges.push({ from: 'AppService', to: 'DataRepository', label: 'uses' });
    edges.push({ from: 'DataRepository', to: 'Database', label: 'persists' });
    
    return { 
      mode: 'lld', 
      lld: { 
        classes, 
        rels,
        arch: { nodes, edges }
      } 
    };
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
  
  // Generate architecture components for each entity
  for (const [entityName] of entityToActions.entries()) {
    if (!entityName) continue;
    
    const baseId = entityName.replace(/\s+/g, '');
    
    // Frontend component
    const componentId = `${baseId}Component`;
    nodes.push({ 
      id: componentId, 
      label: `${entityName} Component`, 
      layer: 'frontend', 
      type: 'component' 
    });
    
    // Backend service
    const serviceId = `${baseId}Service`;
    nodes.push({ 
      id: serviceId, 
      label: `${entityName} Service`, 
      layer: 'backend', 
      type: 'service' 
    });
    
    // Backend controller
    const controllerId = `${baseId}Controller`;
    nodes.push({ 
      id: controllerId, 
      label: `${entityName} Controller`, 
      layer: 'backend', 
      type: 'controller' 
    });
    
    // Repository
    const repoId = `${baseId}Repository`;
    nodes.push({ 
      id: repoId, 
      label: `${entityName} Repository`, 
      layer: 'database', 
      type: 'repository' 
    });
    
    // Edges for this entity's architecture
    edges.push({ from: 'RouterModule', to: componentId, label: 'routes' });
    edges.push({ from: componentId, to: serviceId, label: 'injects' });
    edges.push({ from: 'APIGateway', to: controllerId, label: 'routes' });
    edges.push({ from: controllerId, to: serviceId, label: 'delegates' });
    edges.push({ from: serviceId, to: repoId, label: 'uses' });
  }
  
  // Add shared database node
  nodes.push({ id: 'Database', label: 'Database', layer: 'database', type: 'database' });
  nodes.push({ id: 'CacheService', label: 'Cache Service', layer: 'database', type: 'cache' });
  
  // Connect all repositories to database
  for (const node of nodes) {
    if (node.type === 'repository') {
      edges.push({ from: node.id, to: 'Database', label: 'persists' });
      edges.push({ from: node.id, to: 'CacheService', label: 'caches' });
    }
  }
  
  // Add external integrations based on context
  const lowerContext = allText.toLowerCase();
  if (lowerContext.includes('payment') || lowerContext.includes('stripe') || lowerContext.includes('paypal')) {
    nodes.push({ id: 'PaymentGateway', label: 'Payment Gateway', layer: 'integration', type: 'gateway' });
    edges.push({ from: 'APIGateway', to: 'PaymentGateway', label: 'processes' });
  }
  if (lowerContext.includes('email') || lowerContext.includes('notification') || lowerContext.includes('mail')) {
    nodes.push({ id: 'NotificationService', label: 'Notification Service', layer: 'integration', type: 'service' });
    edges.push({ from: 'APIGateway', to: 'NotificationService', label: 'sends' });
  }
  if (lowerContext.includes('storage') || lowerContext.includes('file') || lowerContext.includes('upload') || lowerContext.includes('image')) {
    nodes.push({ id: 'StorageService', label: 'Cloud Storage', layer: 'integration', type: 'service' });
    edges.push({ from: 'APIGateway', to: 'StorageService', label: 'stores' });
  }
  
  return { 
    mode: 'lld', 
    lld: { 
      classes, 
      rels,
      arch: { nodes: dedupeArray(nodes, n => n.id), edges: dedupeArray(edges, e => `${e.from}_${e.to}`) }
    } 
  };
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
  
  // Primary key field
  fields.push({ name: 'id', type: 'uuid', constraint: 'PK' });
  
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
            const constraint = inferFieldConstraint(field);
            fields.push({ name: field, type: inferFieldType(field), ...(constraint && { constraint }) });
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

/**
 * Infer field constraint based on naming conventions
 */
function inferFieldConstraint(fieldName: string): string | undefined {
  if (!fieldName || typeof fieldName !== 'string') return undefined;
  
  const lower = fieldName.toLowerCase();
  if (lower === 'id') return 'PK';
  if (lower.endsWith('_id')) return 'FK';
  return undefined;
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
        { name: 'id', type: 'uuid', constraint: 'PK' },
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
        { name: 'id', type: 'uuid', constraint: 'PK' },
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
