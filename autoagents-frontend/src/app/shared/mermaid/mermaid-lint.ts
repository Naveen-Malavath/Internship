import mermaid from 'mermaid';

export interface BraceStats {
  open: number;
  close: number;
  balanced: boolean;
  firstMismatchLine?: number;
}

export interface ValidationResult {
  ok: true;
}

export interface ValidationError {
  ok: false;
  message: string;
  line?: number;
  details?: string;
}

export type ValidationResponse = ValidationResult | ValidationError;

export type RenderMode = 'hld' | 'lld' | 'dbd';

const INIT_DIRECTIVE = '%%{init: {"theme":"base","flowchart":{"htmlLabels":true,"curve":"linear"}} }%%';

export function stripBomAndZwsp(s: string): string {
  return s.replace(/^\uFEFF/, '').replace(/\u200B/g, '');
}

/**
 * Check for balanced braces in the mermaid text
 */
export function checkBraceBalance(text: string): BraceStats {
  const lines = text.split('\n');
  let openCount = 0;
  let closeCount = 0;
  let firstMismatchLine: number | undefined;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    for (const char of line) {
      if (char === '{') {
        openCount++;
      } else if (char === '}') {
        closeCount++;
        // Track if we close more than we've opened
        if (closeCount > openCount && firstMismatchLine === undefined) {
          firstMismatchLine = i + 1;
        }
      }
    }
  }
  
  return {
    open: openCount,
    close: closeCount,
    balanced: openCount === closeCount,
    firstMismatchLine: openCount !== closeCount ? firstMismatchLine : undefined,
  };
}

/**
 * Check for potential cycle issues in graph/flowchart diagrams
 */
export function checkForCycles(text: string): { hasCycle: boolean; message?: string } {
  // Simple cycle detection for common patterns
  const lines = text.split('\n');
  const edges: Map<string, Set<string>> = new Map();
  
  for (const line of lines) {
    // Match edge patterns: A --> B, A -> B, A --- B, etc.
    const edgeMatch = line.match(/^\s*(\w+)\s*(?:-->|->|---|-\.->|==>|-.->)\s*(\w+)/);
    if (edgeMatch) {
      const [, from, to] = edgeMatch;
      if (!edges.has(from)) {
        edges.set(from, new Set());
      }
      edges.get(from)!.add(to);
    }
  }
  
  // Check for direct self-loops
  for (const [node, targets] of edges) {
    if (targets.has(node)) {
      return { 
        hasCycle: true, 
        message: `Self-loop detected: ${node} connects to itself` 
      };
    }
  }
  
  // Check for simple two-node cycles (A -> B -> A)
  for (const [nodeA, targetsA] of edges) {
    for (const nodeB of targetsA) {
      const targetsB = edges.get(nodeB);
      if (targetsB?.has(nodeA)) {
        return { 
          hasCycle: true, 
          message: `Cycle detected between ${nodeA} and ${nodeB}` 
        };
      }
    }
  }
  
  return { hasCycle: false };
}

/**
 * Attempt to fix common mermaid syntax issues
 */
export function autoFixMermaid(text: string): { fixed: string; changes: string[] } {
  const changes: string[] = [];
  let fixed = text;
  
  // Fix unbalanced braces
  const braceStats = checkBraceBalance(fixed);
  if (!braceStats.balanced) {
    const diff = braceStats.open - braceStats.close;
    if (diff > 0) {
      // Add missing closing braces
      fixed = fixed + '\n' + '}'.repeat(diff);
      changes.push(`Added ${diff} missing closing brace(s)`);
    } else if (diff < 0) {
      // Remove extra closing braces (from the end)
      const lines = fixed.split('\n');
      let removed = 0;
      for (let i = lines.length - 1; i >= 0 && removed < Math.abs(diff); i--) {
        if (lines[i].trim() === '}') {
          lines.splice(i, 1);
          removed++;
        }
      }
      fixed = lines.join('\n');
      changes.push(`Removed ${removed} extra closing brace(s)`);
    }
  }
  
  // Remove orphaned class members (methods/fields outside class blocks)
  if (fixed.includes('classDiagram')) {
    const lines = fixed.split('\n');
    const cleanedLines: string[] = [];
    let inClass = false;
    let braceDepth = 0;
    
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Track class block state
      if (/^class\s+\w+.*\{/.test(trimmed)) {
        inClass = true;
        braceDepth++;
      } else if (trimmed === '}' && inClass) {
        braceDepth--;
        if (braceDepth === 0) {
          inClass = false;
        }
      }
      
      // Check for orphaned members
      if (/^[+\-#~]\w/.test(trimmed) && !inClass) {
        changes.push(`Removed orphaned class member: ${trimmed.substring(0, 40)}...`);
        continue; // Skip this line
      }
      
      cleanedLines.push(line);
    }
    
    fixed = cleanedLines.join('\n');
  }
  
  return { fixed, changes };
}

export function normalizeMermaid(text: string): string {
  if (!text) return '';
  
  let normalized = stripBomAndZwsp(text.trim());
  
  normalized = normalized.replace(/\n\n+/g, '\n\n');
  
  const lines = normalized.split('\n');
  const seenInit = new Set<string>();
  const cleanedLines: string[] = [];
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    if (trimmed.startsWith('%%{init:')) {
      if (!seenInit.has('init')) {
        cleanedLines.push(trimmed);
        seenInit.add('init');
      }
      continue;
    }
    
    cleanedLines.push(line);
  }
  
  normalized = cleanedLines.join('\n');
  
  if (!normalized.includes('%%{init:')) {
    const firstLine = normalized.split('\n')[0];
    if (firstLine.match(/^(flowchart|graph|classDiagram|erDiagram)/i)) {
      normalized = `${INIT_DIRECTIVE}\n${normalized}`;
    } else {
      normalized = `${INIT_DIRECTIVE}\n${normalized}`;
    }
  }
  
  const firstDiagramLine = normalized.split('\n').find(l => 
    l.trim().match(/^(flowchart|graph)\s*$/i)
  );
  
  if (firstDiagramLine && firstDiagramLine.trim().match(/^(flowchart|graph)\s*$/i)) {
    normalized = normalized.replace(
      /^(%%\{init:.*?\}%%\n)?(flowchart|graph)\s*$/im,
      (match, init, directive) => {
        const initPart = init || '';
        return `${initPart}${directive} LR`;
      }
    );
  }
  
  return normalized;
}

export function validateWithMermaid(text: string): ValidationResponse {
  if (!text || !text.trim()) {
    return { ok: false, message: 'empty input' };
  }
  
  // Pre-validation checks
  const braceStats = checkBraceBalance(text);
  if (!braceStats.balanced) {
    return { 
      ok: false, 
      message: 'unbalanced braces',
      line: braceStats.firstMismatchLine,
      details: `Found ${braceStats.open} opening and ${braceStats.close} closing braces`
    };
  }
  
  // Check for cycle issues in graph diagrams
  if (text.includes('graph') || text.includes('flowchart')) {
    const cycleCheck = checkForCycles(text);
    if (cycleCheck.hasCycle) {
      return {
        ok: false,
        message: 'cycle detected',
        details: cycleCheck.message
      };
    }
  }
  
  try {
    mermaid.parse(text);
    return { ok: true };
  } catch (error: any) {
    const errorMsg = error?.message || error?.toString() || 'unknown error';
    const lineMatch = errorMsg.match(/line (\d+)/i);
    const line = lineMatch ? parseInt(lineMatch[1], 10) : undefined;
    
    let shortReason = 'syntax error';
    
    if (errorMsg.toLowerCase().includes('unbalanced')) {
      shortReason = 'unbalanced braces';
    } else if (errorMsg.toLowerCase().includes('expecting')) {
      shortReason = 'unexpected token';
    } else if (errorMsg.toLowerCase().includes('lexer')) {
      shortReason = 'invalid syntax';
    } else if (errorMsg.toLowerCase().includes('parse')) {
      shortReason = 'structure error';
    } else if (errorMsg.toLowerCase().includes('cycle')) {
      shortReason = 'cycle detected';
    } else if (errorMsg.toLowerCase().includes('parent')) {
      shortReason = 'invalid parent reference';
    }
    
    return { ok: false, message: shortReason, line, details: errorMsg };
  }
}
