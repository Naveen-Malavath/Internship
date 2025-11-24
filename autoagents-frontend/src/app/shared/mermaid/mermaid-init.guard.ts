import mermaid from 'mermaid';

let mermaidInitialized = false;

export function initializeMermaidOnce(): void {
  if (mermaidInitialized) {
    return;
  }
  
  mermaid.initialize({
    startOnLoad: false,
    theme: 'base',
    themeVariables: {
      fontSize: '18px',
      fontFamily: 'Arial, sans-serif',
      primaryColor: '#3b82f6',
      primaryTextColor: '#fff',
      primaryBorderColor: '#1e40af',
      lineColor: '#64748b',
      secondaryColor: '#10b981',
      tertiaryColor: '#f59e0b',
    },
    flowchart: {
      useMaxWidth: false,
      htmlLabels: true,
      curve: 'linear',
      padding: 25,
      nodeSpacing: 60,
      rankSpacing: 70,
    },
    er: {
      useMaxWidth: false,
    }
  } as any);
  
  mermaidInitialized = true;
  console.debug('[mermaid-init] Initialized once');
}

