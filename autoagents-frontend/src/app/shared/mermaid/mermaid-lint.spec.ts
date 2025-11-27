import {
  normalizeMermaid,
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

  // NOTE: Tests for detectDiagramType, braceStats, autoFixBraces, and dedupeEdges
  // have been removed as these functions no longer exist in mermaid-lint.ts

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

