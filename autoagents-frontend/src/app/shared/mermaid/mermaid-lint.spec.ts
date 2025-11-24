import {
  normalizeMermaid,
  detectDiagramType,
  braceStats,
  autoFixBraces,
  dedupeEdges,
  validateWithMermaid
} from './mermaid-lint';

describe('mermaid-lint', () => {
  describe('normalizeMermaid', () => {
    it('should trim whitespace', () => {
      const input = '  \n  flowchart TD\n  A --> B  \n  ';
      const result = normalizeMermaid(input);
      expect(result).not.toMatch(/^\s+/);
      expect(result).not.toMatch(/\s+$/);
    });

    it('should collapse multiple blank lines', () => {
      const input = 'flowchart TD\n\n\n\nA --> B';
      const result = normalizeMermaid(input);
      expect(result).not.toContain('\n\n\n');
    });

    it('should add init directive if missing', () => {
      const input = 'flowchart TD\nA --> B';
      const result = normalizeMermaid(input);
      expect(result).toContain('%%{init:');
    });

    it('should remove duplicate init directives', () => {
      const input = '%%{init: {"theme":"base"}}\n%%{init: {"theme":"dark"}}\nflowchart TD\nA --> B';
      const result = normalizeMermaid(input);
      const matches = result.match(/%%\{init:/g);
      expect(matches?.length).toBe(1);
    });

    it('should add direction to flowchart without direction', () => {
      const input = 'flowchart\nA --> B';
      const result = normalizeMermaid(input);
      expect(result).toMatch(/flowchart LR/i);
    });
  });

  describe('detectDiagramType', () => {
    it('should detect ER diagram', () => {
      const input = 'erDiagram\nUSERS {\n  string id\n}';
      expect(detectDiagramType(input)).toBe('er');
    });

    it('should detect class diagram', () => {
      const input = 'classDiagram\nclass Animal {\n  +String name\n}';
      expect(detectDiagramType(input)).toBe('class');
    });

    it('should detect flowchart', () => {
      const input = 'flowchart TD\nA --> B';
      expect(detectDiagramType(input)).toBe('flow');
    });

    it('should detect ER by entity syntax', () => {
      const input = 'USERS {\n  string id\n}\nPOSTS {\n  string id\n}';
      expect(detectDiagramType(input)).toBe('er');
    });

    it('should detect class by class keyword', () => {
      const input = 'class Animal {\n  +name: String\n}';
      expect(detectDiagramType(input)).toBe('class');
    });
  });

  describe('braceStats', () => {
    it('should count balanced braces correctly', () => {
      const input = 'class A {\n  +method()\n}';
      const stats = braceStats(input);
      expect(stats.open).toBe(1);
      expect(stats.close).toBe(1);
      expect(stats.balanced).toBe(true);
    });

    it('should detect unbalanced braces', () => {
      const input = 'class A {\n  +method()\nclass B {\n  +method()\n}';
      const stats = braceStats(input);
      expect(stats.open).toBe(2);
      expect(stats.close).toBe(1);
      expect(stats.balanced).toBe(false);
    });

    it('should identify first mismatch line', () => {
      const input = 'class A {\n  +method()\n}\n}';
      const stats = braceStats(input);
      expect(stats.balanced).toBe(false);
      expect(stats.firstMismatchLine).toBeDefined();
    });

    it('should skip init directive lines', () => {
      const input = '%%{init: {"theme":"base"}}\nclass A {\n  +method()\n}';
      const stats = braceStats(input);
      expect(stats.open).toBe(1);
      expect(stats.close).toBe(1);
      expect(stats.balanced).toBe(true);
    });
  });

  describe('autoFixBraces', () => {
    it('should fix missing closing brace in ER diagram', () => {
      const input = 'USERS {\n  string id\n  string name';
      const result = autoFixBraces(input, 'er');
      expect(result.fixed).toContain('}');
      expect(result.fixedCount).toBeGreaterThan(0);
    });

    it('should fix missing closing brace in class diagram', () => {
      const input = 'class Animal {\n  +name: String\n  +age: Int';
      const result = autoFixBraces(input, 'class');
      expect(result.fixed).toContain('}');
      expect(result.fixedCount).toBeGreaterThan(0);
    });

    it('should remove stray closing braces', () => {
      const input = 'class A {\n  +method()\n}\n}';
      const result = autoFixBraces(input, 'class');
      const braces = result.fixed.match(/\}/g);
      expect(braces?.length).toBe(1);
    });

    it('should not modify balanced diagrams', () => {
      const input = 'class A {\n  +method()\n}';
      const result = autoFixBraces(input, 'class');
      expect(result.fixedCount).toBe(0);
    });
  });

  describe('dedupeEdges', () => {
    it('should remove duplicate edges', () => {
      const input = 'flowchart TD\nA --> B\nA --> B\nB --> C';
      const result = dedupeEdges(input);
      const edges = result.match(/A --> B/g);
      expect(edges?.length).toBe(1);
    });

    it('should preserve non-duplicate edges', () => {
      const input = 'flowchart TD\nA --> B\nB --> C\nC --> D';
      const result = dedupeEdges(input);
      expect(result).toContain('A --> B');
      expect(result).toContain('B --> C');
      expect(result).toContain('C --> D');
    });
  });

  describe('validateWithMermaid', () => {
    it('should return ok for valid diagram', () => {
      const input = 'graph TD\nA --> B';
      const result = validateWithMermaid(input);
      expect(result.ok).toBe(true);
    });

    it('should return error for invalid diagram', () => {
      const input = 'graph TD\nA --> --> B';
      const result = validateWithMermaid(input);
      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.message).toBeDefined();
        expect(result.message.length).toBeGreaterThan(0);
      }
    });

    it('should return error for empty input', () => {
      const input = '';
      const result = validateWithMermaid(input);
      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.message).toBe('empty input');
      }
    });

    it('should provide short reason for errors', () => {
      const input = 'graph TD\nA --> --> B';
      const result = validateWithMermaid(input);
      expect(result.ok).toBe(false);
      if (!result.ok) {
        expect(result.message).not.toContain('Parse error');
        expect(result.message.length).toBeLessThan(50);
      }
    });
  });
});

