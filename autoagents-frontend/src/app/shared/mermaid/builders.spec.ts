import { buildHLD, buildLLD, buildDBD } from './builders';
import { emitHLD, emitLLD, emitDBD } from './emitter';
import { validateWithMermaid } from './mermaid-lint';

describe('Mermaid Builders', () => {
  describe('buildHLD', () => {
    it('should create valid HLD diagram', () => {
      const root = buildHLD('Test context', ['Story 1', 'Story 2'], ['Auth Feature', 'Payment Feature']);
      const output = emitHLD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
      expect(root.mode).toBe('hld');
      expect(root.hld).toBeDefined();
      expect(root.hld!.nodes.length).toBeGreaterThan(0);
    });

    it('should dedupe nodes and edges', () => {
      const root = buildHLD('', [], ['Auth', 'Auth', 'Payment']);
      
      const nodeIds = root.hld!.nodes.map(n => n.id);
      const uniqueIds = new Set(nodeIds);
      
      expect(nodeIds.length).toBe(uniqueIds.size);
    });

    it('should assign features to appropriate groups', () => {
      const root = buildHLD('', [], ['Authentication Service', 'Payment Gateway', 'Notification System']);
      
      const authNode = root.hld!.nodes.find(n => n.label.includes('Authentication'));
      const paymentNode = root.hld!.nodes.find(n => n.label.includes('Payment'));
      
      expect(authNode).toBeDefined();
      expect(paymentNode).toBeDefined();
    });
  });

  describe('buildLLD', () => {
    it('should create valid LLD diagram', () => {
      const root = buildLLD('Test context', [], ['User authentication', 'Account management', 'Payment processing']);
      const output = emitLLD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
      expect(root.mode).toBe('lld');
      expect(root.lld).toBeDefined();
      expect(root.lld!.classes.length).toBeGreaterThan(0);
    });

    it('should never create top-level members', () => {
      const root = buildLLD('', [], ['Feature with +String type', 'Another -Object feature']);
      const output = emitLLD(root);
      
      const lines = output.split('\n');
      for (const line of lines) {
        const trimmed = line.trim();
        if (!line.startsWith('    ')) {
          expect(trimmed).not.toMatch(/^[+\-#]\w+/);
        }
      }

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should place all members inside classes', () => {
      const root = buildLLD('', [], ['Authentication', 'Authorization']);
      
      for (const cls of root.lld!.classes) {
        expect(cls.members.length).toBeGreaterThan(0);
        
        for (const member of cls.members) {
          expect(member.name).toBeTruthy();
          expect(['field', 'method']).toContain(member.kind);
        }
      }

      const output = emitLLD(root);
      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should handle features with visibility tokens in names', () => {
      const root = buildLLD('', [], ['+PublicFeature', '-PrivateFeature', '#ProtectedFeature']);
      const output = emitLLD(root);

      const lines = output.split('\n');
      for (const line of lines) {
        if (!line.startsWith('    ') && !line.includes('%%{init:') && line.trim() !== 'classDiagram') {
          const trimmed = line.trim();
          if (trimmed.match(/^class\s+/)) {
            continue;
          }
          expect(trimmed).not.toMatch(/^[+\-#]/);
        }
      }

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should create AuthService for auth-related features', () => {
      const root = buildLLD('', [], ['User login', 'Password reset', 'Two-factor authentication']);
      
      const authService = root.lld!.classes.find(c => c.name === 'AuthService');
      expect(authService).toBeDefined();
      expect(authService!.members.length).toBeGreaterThan(0);
    });
  });

  describe('buildDBD', () => {
    it('should create valid DBD diagram', () => {
      const root = buildDBD('Test context', [], []);
      const output = emitDBD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
      expect(root.mode).toBe('dbd');
      expect(root.dbd).toBeDefined();
      expect(root.dbd!.entities.length).toBeGreaterThan(0);
    });

    it('should never include visibility tokens', () => {
      const root = buildDBD('', [], ['Feature 1', 'Feature 2']);
      const output = emitDBD(root);

      expect(output).not.toContain('+');
      expect(output).not.toContain('-');
      expect(output).not.toContain('#');

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should have balanced braces', () => {
      const root = buildDBD('', [], []);
      const output = emitDBD(root);

      const openCount = (output.match(/\{/g) || []).length;
      const closeCount = (output.match(/\}/g) || []).length;

      expect(openCount).toBe(closeCount);
    });

    it('should infer field types correctly', () => {
      const root = buildDBD('', [], []);
      
      const userEntity = root.dbd!.entities.find(e => e.name === 'USER');
      expect(userEntity).toBeDefined();
      
      const idField = userEntity!.fields.find(f => f.name === 'id');
      const emailField = userEntity!.fields.find(f => f.name === 'email');
      
      expect(idField?.type).toBe('uuid');
      expect(emailField?.type).toBe('string');
    });

    it('should create relationships between entities', () => {
      const root = buildDBD('', [], []);
      
      expect(root.dbd!.rels.length).toBeGreaterThan(0);
      
      const userAccountRel = root.dbd!.rels.find(r => r.left === 'USER' && r.right === 'ACCOUNT');
      expect(userAccountRel).toBeDefined();
    });
  });

  describe('Regression tests', () => {
    it('should handle input that previously produced classDiagram +String +Object', () => {
      const root = buildLLD('', [], ['String processing', 'Object management']);
      const output = emitLLD(root);

      const lines = output.split('\n');
      let foundInvalid = false;
      
      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed === 'classDiagram' || trimmed.startsWith('%%{init:')) {
          continue;
        }
        
        if (!line.startsWith('    ')) {
          if (trimmed.match(/^[+\-#](String|Object)/)) {
            foundInvalid = true;
            break;
          }
        }
      }

      expect(foundInvalid).toBe(false);
      
      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should handle input that previously produced -routingEngine +authenticateRequest at top level', () => {
      const root = buildLLD('', [], ['Routing engine implementation', 'Request authentication']);
      const output = emitLLD(root);

      const lines = output.split('\n');
      for (const line of lines) {
        if (!line.startsWith('    ') && !line.includes('%%{init:') && line.trim() !== 'classDiagram') {
          const trimmed = line.trim();
          expect(trimmed).not.toMatch(/^-routingEngine/);
          expect(trimmed).not.toMatch(/^\+authenticateRequest/);
        }
      }

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should handle BOM character at start of file', () => {
      const root = buildLLD('', [], ['Test feature']);
      let output = emitLLD(root);
      output = '\uFEFF' + output;

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should handle ZWSP characters', () => {
      const root = buildLLD('', [], ['Test\u200Bfeature']);
      const output = emitLLD(root);

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });
  });
});

