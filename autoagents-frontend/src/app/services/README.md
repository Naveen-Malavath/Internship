# AutoAgents Frontend Services

This directory contains injectable services used throughout the AutoAgents application.

## Services

### `Agent3Service`
Handles communication with Agent-3 (Mermaid diagram generation) backend endpoint.

**Usage:**
```typescript
import { Agent3Service } from './services/agent3.service';

constructor(private agent3: Agent3Service) {}

generateDiagram() {
  this.agent3.generateMermaid({
    context: 'E-commerce platform',
    features: this.features,
    stories: this.stories,
    diagramType: 'hld'
  }).subscribe(response => {
    console.log('Mermaid diagram:', response.diagrams.mermaid);
  });
}
```

### `MermaidFixerService`
Fixes common Mermaid parsing errors and ensures deterministic rendering.

**Usage:**
```typescript
import { MermaidFixerService } from './services/mermaid-fixer.service';

constructor(private fixer: MermaidFixerService) {}

fixDiagram() {
  const errorLog = 'Syntax error in line 5: Unexpected token';
  const brokenDiagram = `graph TD\n  A[Start\n  B[End]`;
  
  const fixed = this.fixer.fixMermaidDiagram(errorLog, brokenDiagram);
  console.log('Fixed diagram:', fixed);
  
  // Validate
  const validation = this.fixer.validateMermaid(fixed);
  if (validation.valid) {
    console.log('Diagram is valid!');
  }
}
```

### `WorkspaceNavigationService`
Provides helpers for navigating to workspace with Agent-3 data.

**Usage:**
```typescript
import { WorkspaceNavigationService } from './services/workspace-navigation.service';

constructor(private workspaceNav: WorkspaceNavigationService) {}

openInWorkspace() {
  const state = this.workspaceNav.prepareWorkspaceState(
    this.context,
    this.features,
    this.stories,
    this.mermaidCode
  );
  
  if (this.workspaceNav.isValidWorkspaceState(state)) {
    this.workspaceNav.navigateToWorkspace(state);
  }
}
```

### `MermaidStyleService`
Handles Mermaid diagram styling and theme configuration.

### `DesignService`
Manages HLD/LLD/DBD design generation and persistence.

### `FeedbackService`
Handles feedback submission and content regeneration.

## Testing Services

All services are registered with `providedIn: 'root'` for singleton behavior. To test:

```typescript
import { TestBed } from '@angular/core/testing';
import { Agent3Service } from './services/agent3.service';
import { HttpClientTestingModule } from '@angular/common/http/testing';

describe('Agent3Service', () => {
  let service: Agent3Service;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule]
    });
    service = TestBed.inject(Agent3Service);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
```

## Adding New Services

1. Create service file: `your-service.service.ts`
2. Use Angular CLI: `ng generate service services/your-service`
3. Implement service logic with `@Injectable({ providedIn: 'root' })`
4. Document usage in this README
5. Add unit tests in `your-service.service.spec.ts`

