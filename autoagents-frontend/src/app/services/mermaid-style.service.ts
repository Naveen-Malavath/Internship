/**
 * Mermaid Style Service
 * 
 * Converts backend style configuration into Mermaid initialization options
 * and applies dynamic styling based on domain/prompt analysis.
 */

export interface MermaidStyleConfig {
  theme: string;
  nodeShape: string;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  backgroundColor: string;
  arrowStyle: string;
  fontSize: string;
  fontFamily: string;
  domain: string;
}

export interface MermaidInitConfig {
  startOnLoad: boolean;
  theme: string;
  themeVariables: {
    fontSize: string;
    fontFamily: string;
    primaryColor: string;
    primaryTextColor: string;
    primaryBorderColor: string;
    lineColor: string;
    secondaryColor: string;
    tertiaryColor: string;
    background?: string;
  };
  flowchart: {
    useMaxWidth: boolean;
    htmlLabels: boolean;
    curve: string;
    padding: number;
    nodeSpacing: number;
    rankSpacing: number;
  };
}

export class MermaidStyleService {
  /**
   * Convert backend style configuration to Mermaid initialization config
   */
  static generateMermaidConfig(
    styleConfig: MermaidStyleConfig | null | undefined,
    options: {
      isLLD?: boolean;
      padding?: number;
      nodeSpacing?: number;
      rankSpacing?: number;
    } = {}
  ): MermaidInitConfig {
    // Default style config if none provided
    const defaultConfig: MermaidStyleConfig = {
      theme: 'default',
      nodeShape: 'rect',
      primaryColor: '#3b82f6',
      secondaryColor: '#10b981',
      accentColor: '#f59e0b',
      backgroundColor: '#ffffff',
      arrowStyle: 'solid',
      fontSize: '16px',
      fontFamily: 'Arial, sans-serif',
      domain: 'default',
    };

    const config = styleConfig || defaultConfig;
    const { isLLD = false, padding, nodeSpacing, rankSpacing } = options;

    // Calculate spacing based on diagram type
    const baseFontSize = isLLD ? '18px' : config.fontSize || '16px';
    const diagramPadding = padding ?? (isLLD ? 30 : 20);
    const diagramNodeSpacing = nodeSpacing ?? (isLLD ? 60 : 50);
    const diagramRankSpacing = rankSpacing ?? (isLLD ? 80 : 60);

    // Determine arrow style for Mermaid
    const curve = config.arrowStyle === 'dotted' ? 'linear' : 
                  config.arrowStyle === 'thick' ? 'basis' : 'basis';

    // Generate primary border color (darker shade of primary)
    const primaryBorderColor = this.darkenColor(config.primaryColor, 0.2);

    return {
      startOnLoad: false,
      theme: config.theme || 'default',
      themeVariables: {
        fontSize: baseFontSize,
        fontFamily: config.fontFamily || 'Arial, sans-serif',
        primaryColor: config.primaryColor,
        primaryTextColor: '#fff',
        primaryBorderColor: primaryBorderColor,
        lineColor: this.getLineColor(config.arrowStyle, config.primaryColor),
        secondaryColor: config.secondaryColor,
        tertiaryColor: config.accentColor,
        background: config.backgroundColor,
      },
      flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: curve,
        padding: diagramPadding,
        nodeSpacing: diagramNodeSpacing,
        rankSpacing: diagramRankSpacing,
      },
    };
  }

  /**
   * Get line color based on arrow style
   */
  private static getLineColor(arrowStyle: string, primaryColor: string): string {
    if (arrowStyle === 'dotted') {
      return this.lightenColor(primaryColor, 0.3);
    }
    if (arrowStyle === 'thick') {
      return primaryColor;
    }
    // Default solid
    return '#64748b';
  }

  /**
   * Darken a hex color by a percentage
   */
  private static darkenColor(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent * 100);
    const R = Math.max(0, Math.min(255, (num >> 16) - amt));
    const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) - amt));
    const B = Math.max(0, Math.min(255, (num & 0x0000FF) - amt));
    return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
  }

  /**
   * Lighten a hex color by a percentage
   */
  private static lightenColor(hex: string, percent: number): string {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent * 100);
    const R = Math.max(0, Math.min(255, (num >> 16) + amt));
    const G = Math.max(0, Math.min(255, ((num >> 8) & 0x00FF) + amt));
    const B = Math.max(0, Math.min(255, (num & 0x0000FF) + amt));
    return '#' + (0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1);
  }

  /**
   * Apply node shape styling to Mermaid diagram
   * Note: Mermaid node shapes are defined in the diagram syntax itself
   * This is a helper to suggest appropriate shapes
   */
  static getNodeShapeSyntax(shape: string): string {
    const shapeMap: Record<string, string> = {
      round: '()',
      rect: '[]',
      stadium: '([])',
      circle: '(())',
      diamond: '{}',
      hexagon: '{{}}',
      parallelogram: '[\\/]',
    };
    return shapeMap[shape] || '[]';
  }
}

