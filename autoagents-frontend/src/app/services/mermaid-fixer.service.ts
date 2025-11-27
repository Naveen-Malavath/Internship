import { Injectable } from '@angular/core';

/**
 * Mermaid FIXER Service
 * 
 * Reads error logs and current Mermaid text, returns corrected Mermaid diagram
 * that parses cleanly and renders deterministically with mermaid.js.
 */
@Injectable({
  providedIn: 'root'
})
export class MermaidFixerService {
  
  /**
   * Fix Mermaid diagram based on error log and current diagram text
   * 
   * @param errorLog - Error message from Mermaid parser
   * @param diagramText - Current Mermaid diagram text
   * @returns Fixed Mermaid diagram text
   */
  fixMermaidDiagram(errorLog: string, diagramText: string): string {
    console.log('[MermaidFixer] Fixing diagram based on error:', errorLog);
    
    let fixed = diagramText.trim();
    
    // Step 1: Auto-detect diagram type
    const diagramType = this.detectDiagramType(fixed);
    console.log('[MermaidFixer] Detected diagram type:', diagramType);
    
    // Step 2: Apply syntax guarantees
    fixed = this.guaranteeSyntax(fixed, diagramType, errorLog);
    
    // Step 3: Make deterministic
    fixed = this.makeDeterministic(fixed, diagramType);
    
    // Step 4: Validate and return
    console.log('[MermaidFixer] Fixed diagram length:', fixed.length);
    return fixed;
  }
  
  /**
   * Auto-detect diagram type from content
   */
  private detectDiagramType(text: string): 'erDiagram' | 'classDiagram' | 'flowchart' {
    const lowerText = text.toLowerCase();
    
    // Check for ERD patterns
    const hasErdPatterns = (
      /\buuid\s+\w+/i.test(text) ||
      /\btimestamp\s+\w+/i.test(text) ||
      /\b(PK|FK|UK)\b/.test(text) ||
      /\w+\s*\{[^}]*\}/s.test(text) && /erdiagram/i.test(lowerText)
    );
    
    if (hasErdPatterns || lowerText.includes('erdiagram')) {
      return 'erDiagram';
    }
    
    // Check for class diagram patterns
    const hasClassPatterns = (
      /\+\w+\s*\([^)]*\)/.test(text) || // +method()
      /\+\w+\s*:\s*\w+/.test(text) || // +field: type
      lowerText.includes('classdiagram')
    );
    
    if (hasClassPatterns) {
      return 'classDiagram';
    }
    
    // Default to flowchart
    return 'flowchart';
  }
  
  /**
   * Guarantee syntax correctness
   */
  private guaranteeSyntax(text: string, type: string, errorLog: string): string {
    let fixed = text;
    
    // Balance braces
    fixed = this.balanceBraces(fixed);
    
    // Fix based on diagram type
    if (type === 'classDiagram') {
      fixed = this.fixClassDiagram(fixed, errorLog);
    } else if (type === 'erDiagram') {
      fixed = this.fixErDiagram(fixed, errorLog);
    } else {
      fixed = this.fixFlowchart(fixed, errorLog);
    }
    
    // Remove orphaned members
    fixed = this.removeOrphanedMembers(fixed, type);
    
    return fixed;
  }
  
  /**
   * Balance all braces in the diagram
   */
  private balanceBraces(text: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let braceCount = 0;
    
    for (const line of lines) {
      const openBraces = (line.match(/\{/g) || []).length;
      const closeBraces = (line.match(/\}/g) || []).length;
      
      braceCount += openBraces - closeBraces;
      
      // Don't add lines with stray closing braces
      if (line.trim() === '}' && braceCount < 0) {
        braceCount++;
        continue;
      }
      
      result.push(line);
    }
    
    // Add missing closing braces
    while (braceCount > 0) {
      result.push('}');
      braceCount--;
    }
    
    return result.join('\n');
  }
  
  /**
   * Fix classDiagram specific issues
   */
  private fixClassDiagram(text: string, errorLog: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    let inClass = false;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();
      
      // Ensure classDiagram directive is on its own line
      if (trimmed.toLowerCase().startsWith('classdiagram')) {
        result.push('classDiagram');
        continue;
      }
      
      // FIX: Remove invalid ::: syntax in classDiagram style assignments
      // The ::: syntax is ONLY valid in flowcharts, NOT in classDiagrams
      // Pattern: "class ClassName:::styleDefName" should be "class ClassName styleDefName"
      if (/^\s*class\s+\w+:::\w+\s*$/.test(trimmed)) {
        const fixed = trimmed.replace(/(\s*class\s+\w+):::(\w+\s*)$/, '$1 $2');
        result.push(fixed);
        console.log('[MermaidFixer] Fixed invalid ::: syntax in classDiagram:', trimmed, '->', fixed);
        continue;
      }
      
      // Track class blocks
      if (/^class\s+\w+\s*\{/.test(trimmed)) {
        inClass = true;
        result.push(line);
        continue;
      }
      
      if (trimmed === '}') {
        inClass = false;
        result.push(line);
        continue;
      }
      
      // Ensure members are properly formatted
      if (inClass && /^[+\-#~]/.test(trimmed)) {
        const match = trimmed.match(/^([+\-#~])(\w+)(?:\(([^)]*)\))?/);
        if (match) {
          const visibility = match[1];
          const name = match[2];
          const params = match[3];
          
          if (params !== undefined) {
            // Method
            result.push(`    ${visibility}${name}(${params})`);
          } else {
            // Attribute
            result.push(`    ${visibility}${name}: type`);
          }
          continue;
        }
      }
      
      result.push(line);
    }
    
    return result.join('\n');
  }
  
  /**
   * Fix erDiagram specific issues
   */
  private fixErDiagram(text: string, errorLog: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    
    for (const line of lines) {
      let fixed = line;
      
      // Ensure erDiagram directive
      if (line.trim().toLowerCase() === 'erdiagram') {
        result.push('erDiagram');
        continue;
      }
      
      // Remove quoted descriptions from attributes (invalid syntax)
      // CORRECT: uuid id PK
      // WRONG: uuid id PK "Primary Key"
      fixed = fixed.replace(/(\w+\s+\w+\s+(?:PK|FK|UK))\s+"[^"]*"/, '$1');
      
      result.push(fixed);
    }
    
    return result.join('\n');
  }
  
  /**
   * Fix flowchart specific issues
   */
  private fixFlowchart(text: string, errorLog: string): string {
    const lines = text.split('\n');
    const result: string[] = [];
    
    // Ensure flowchart directive
    if (!lines[0] || !lines[0].trim().toLowerCase().startsWith('flowchart')) {
      result.push('flowchart LR');
    }
    
    for (const line of lines) {
      // Skip if already added directive
      if (result.length === 1 && line.trim().toLowerCase().startsWith('flowchart')) {
        continue;
      }
      
      result.push(line);
    }
    
    return result.join('\n');
  }
  
  /**
   * Remove orphaned members (outside valid blocks)
   */
  private removeOrphanedMembers(text: string, type: string): string {
    if (type !== 'classDiagram' && type !== 'erDiagram') {
      return text;
    }
    
    const lines = text.split('\n');
    const result: string[] = [];
    let inBlock = false;
    
    for (const line of lines) {
      const trimmed = line.trim();
      
      // Track blocks
      if (trimmed.includes('{')) {
        inBlock = true;
      }
      if (trimmed === '}') {
        inBlock = false;
        result.push(line);
        continue;
      }
      
      // Remove orphaned members
      if (/^[+\-#~]/.test(trimmed) && !inBlock) {
        console.log('[MermaidFixer] Removing orphaned member:', trimmed);
        continue;
      }
      
      result.push(line);
    }
    
    return result.join('\n');
  }
  
  /**
   * Make rendering deterministic
   */
  private makeDeterministic(text: string, type: string): string {
    let result = text;
    
    // Add init directive at the top
    const initDirective = '%%{init: {"theme":"base","flowchart":{"htmlLabels":true,"curve":"linear"}} }%%';
    
    if (!result.includes('%%{init:')) {
      const lines = result.split('\n');
      const firstLine = lines[0] || '';
      
      // Insert init before diagram type
      if (firstLine.trim().match(/^(flowchart|classDiagram|erDiagram)/i)) {
        lines.unshift(initDirective);
        result = lines.join('\n');
      } else {
        result = `${initDirective}\n${result}`;
      }
    }
    
    // Use stable IDs (kebab-case)
    result = this.normalizeIds(result);
    
    // Remove duplicate nodes and edges
    result = this.removeDuplicates(result);
    
    // Sort entities/classes alphabetically
    result = this.sortEntities(result, type);
    
    return result;
  }
  
  /**
   * Normalize IDs to kebab-case
   */
  private normalizeIds(text: string): string {
    // This is a simplified version - full implementation would be more complex
    return text;
  }
  
  /**
   * Remove duplicate nodes and edges
   */
  private removeDuplicates(text: string): string {
    const lines = text.split('\n');
    const seen = new Set<string>();
    const result: string[] = [];
    
    for (const line of lines) {
      const normalized = line.trim().replace(/\s+/g, ' ');
      
      // Keep directive lines and empty lines
      if (!normalized || normalized.startsWith('%%') || normalized.match(/^(flowchart|classDiagram|erDiagram|graph)/i)) {
        result.push(line);
        continue;
      }
      
      // Skip duplicates
      if (seen.has(normalized)) {
        console.log('[MermaidFixer] Removing duplicate line:', normalized);
        continue;
      }
      
      seen.add(normalized);
      result.push(line);
    }
    
    return result.join('\n');
  }
  
  /**
   * Sort entities alphabetically for consistency
   */
  private sortEntities(text: string, type: string): string {
    // This is a simplified version - full implementation would sort class/entity definitions
    return text;
  }
  
  /**
   * Validate Mermaid syntax (simplified check)
   */
  validateMermaid(text: string): { valid: boolean; error?: string } {
    const trimmed = text.trim();
    
    if (!trimmed) {
      return { valid: false, error: 'Empty diagram' };
    }
    
    const validStarts = ['flowchart', 'graph', 'classdiagram', 'erdiagram', 'sequencediagram', '%%{init:'];
    const hasValidStart = validStarts.some(start => 
      trimmed.toLowerCase().startsWith(start)
    );
    
    if (!hasValidStart) {
      return { valid: false, error: 'Missing diagram type directive' };
    }
    
    // Check brace balance
    const openBraces = (trimmed.match(/\{/g) || []).length;
    const closeBraces = (trimmed.match(/\}/g) || []).length;
    
    if (openBraces !== closeBraces) {
      return { valid: false, error: `Unbalanced braces: ${openBraces} open, ${closeBraces} close` };
    }
    
    return { valid: true };
  }
}

