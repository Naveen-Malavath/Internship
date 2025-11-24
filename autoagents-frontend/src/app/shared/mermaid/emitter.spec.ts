import { emitHLD, emitLLD, emitDBD } from './emitter';
import { DiagramRoot, LldClass, LldClassMember, DbdEntity, DbdRel } from './ast';
import { validateWithMermaid } from './mermaid-lint';

describe('Mermaid Emitters', () => {
  describe('emitLLD', () => {
    it('should never output top-level visibility tokens', () => {
      const root: DiagramRoot = {
        mode: 'lld',
        lld: {
          classes: [
            {
              name: 'TestService',
              members: [
                { kind: 'field', name: 'username', type: 'String', visibility: '+' },
                { kind: 'method', name: 'login', visibility: '+', params: [], returns: 'void' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = emitLLD(root);
      const lines = output.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();
        
        if (trimmed.startsWith('%%{init:') || trimmed === 'classDiagram') {
          continue;
        }

        if (trimmed.match(/^class\s+\w+\s*\{/)) {
          continue;
        }

        if (trimmed === '}') {
          continue;
        }

        const isTopLevel = !line.startsWith('    ');
        if (isTopLevel && !trimmed.match(/^[A-Z]/)) {
          if (trimmed.match(/^[+\-#]/)) {
            fail(`Top-level visibility token found at line ${i + 1}: ${line}`);
          }
        }
      }

      expect(true).toBe(true);
    });

    it('should have balanced braces for multiple classes', () => {
      const classes: LldClass[] = [];
      for (let i = 0; i < 10; i++) {
        classes.push({
          name: `Service${i}`,
          members: [
            { kind: 'field', name: `field${i}`, type: 'String', visibility: '+' }
          ]
        });
      }

      const root: DiagramRoot = {
        mode: 'lld',
        lld: { classes, rels: [] }
      };

      const output = emitLLD(root);
      const openCount = (output.match(/\{/g) || []).length;
      const closeCount = (output.match(/\}/g) || []).length;

      expect(openCount).toBe(closeCount);
      expect(openCount).toBe(10);
    });

    it('should pass mermaid validation', () => {
      const root: DiagramRoot = {
        mode: 'lld',
        lld: {
          classes: [
            {
              name: 'AuthService',
              members: [
                { kind: 'field', name: 'apiKey', type: 'String', visibility: '-' },
                { kind: 'method', name: 'authenticate', visibility: '+', params: [{ name: 'user', type: 'User' }], returns: 'Token' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = emitLLD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
    });

    it('should handle regression case: no top-level +String or +Object', () => {
      const root: DiagramRoot = {
        mode: 'lld',
        lld: {
          classes: [
            {
              name: 'Service',
              members: [
                { kind: 'field', name: 'config', type: 'Object', visibility: '+' },
                { kind: 'field', name: 'name', type: 'String', visibility: '+' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = emitLLD(root);
      const lines = output.split('\n');

      for (const line of lines) {
        const trimmed = line.trim();
        if (!line.startsWith('    ')) {
          expect(trimmed).not.toMatch(/^\+String/);
          expect(trimmed).not.toMatch(/^\+Object/);
        }
      }

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should handle regression case: no top-level -routingEngine +authenticateRequest', () => {
      const root: DiagramRoot = {
        mode: 'lld',
        lld: {
          classes: [
            {
              name: 'RouterService',
              members: [
                { kind: 'field', name: 'routingEngine', type: 'Engine', visibility: '-' },
                { kind: 'method', name: 'authenticateRequest', visibility: '+', params: [], returns: 'boolean' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = emitLLD(root);
      const lines = output.split('\n');

      for (const line of lines) {
        const trimmed = line.trim();
        if (!line.startsWith('    ')) {
          expect(trimmed).not.toMatch(/^-routingEngine/);
          expect(trimmed).not.toMatch(/^\+authenticateRequest/);
        }
      }

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });
  });

  describe('emitDBD', () => {
    it('should never output visibility tokens', () => {
      const root: DiagramRoot = {
        mode: 'dbd',
        dbd: {
          entities: [
            {
              name: 'USER',
              fields: [
                { name: 'id', type: 'uuid', constraint: 'PK' },
                { name: 'email', type: 'string' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = emitDBD(root);

      expect(output).not.toContain('+');
      expect(output).not.toContain('-');
      expect(output).not.toContain('#');

      const validation = validateWithMermaid(output);
      expect(validation.ok).toBe(true);
    });

    it('should have balanced braces for all entities', () => {
      const entities: DbdEntity[] = [];
      for (let i = 0; i < 5; i++) {
        entities.push({
          name: `ENTITY${i}`,
          fields: [
            { name: 'id', type: 'uuid', constraint: 'PK' },
            { name: `field${i}`, type: 'string' }
          ]
        });
      }

      const root: DiagramRoot = {
        mode: 'dbd',
        dbd: { entities, rels: [] }
      };

      const output = emitDBD(root);
      const openCount = (output.match(/\{/g) || []).length;
      const closeCount = (output.match(/\}/g) || []).length;

      expect(openCount).toBe(closeCount);
      expect(openCount).toBe(5);
    });

    it('should pass mermaid validation', () => {
      const root: DiagramRoot = {
        mode: 'dbd',
        dbd: {
          entities: [
            {
              name: 'USER',
              fields: [
                { name: 'id', type: 'uuid', constraint: 'PK' },
                { name: 'email', type: 'string' }
              ]
            },
            {
              name: 'ACCOUNT',
              fields: [
                { name: 'id', type: 'uuid', constraint: 'PK' },
                { name: 'user_id', type: 'uuid', constraint: 'FK' }
              ]
            }
          ],
          rels: [
            { left: 'USER', right: 'ACCOUNT', cardLeft: '||', cardRight: 'o{', label: 'owns' }
          ]
        }
      };

      const output = emitDBD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
    });
  });

  describe('emitHLD', () => {
    it('should pass mermaid validation', () => {
      const root: DiagramRoot = {
        mode: 'hld',
        hld: {
          nodes: [
            { id: 'Frontend', label: 'Frontend', group: 'Presentation' },
            { id: 'Backend', label: 'Backend', group: 'Application' }
          ],
          edges: [
            { from: 'Frontend', to: 'Backend', label: 'requests' }
          ]
        }
      };

      const output = emitHLD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
    });

    it('should group nodes correctly', () => {
      const root: DiagramRoot = {
        mode: 'hld',
        hld: {
          nodes: [
            { id: 'Node1', label: 'Node 1', group: 'Group A' },
            { id: 'Node2', label: 'Node 2', group: 'Group A' },
            { id: 'Node3', label: 'Node 3', group: 'Group B' }
          ],
          edges: []
        }
      };

      const output = emitHLD(root);

      expect(output).toContain('subgraph group_a["Group A"]');
      expect(output).toContain('subgraph group_b["Group B"]');
    });
  });

  describe('BOM and ZWSP handling', () => {
    it('should handle text with BOM character', () => {
      const root: DiagramRoot = {
        mode: 'lld',
        lld: {
          classes: [
            {
              name: 'TestClass',
              members: [
                { kind: 'field', name: 'field', type: 'String', visibility: '+' }
              ]
            }
          ],
          rels: []
        }
      };

      const output = '\uFEFF' + emitLLD(root);
      const validation = validateWithMermaid(output);

      expect(validation.ok).toBe(true);
    });
  });
});

