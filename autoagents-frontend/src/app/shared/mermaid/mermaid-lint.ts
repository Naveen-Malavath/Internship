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
}

export type ValidationResponse = ValidationResult | ValidationError;

export type RenderMode = 'hld' | 'lld' | 'dbd';

const INIT_DIRECTIVE = '%%{init: {"theme":"base","flowchart":{"htmlLabels":true,"curve":"linear"}} }%%';

export function stripBomAndZwsp(s: string): string {
  return s.replace(/^\uFEFF/, '').replace(/\u200B/g, '');
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
    }
    
    return { ok: false, message: shortReason, line };
  }
}
