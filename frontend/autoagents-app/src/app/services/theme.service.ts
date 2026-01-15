import { Injectable, signal, effect } from '@angular/core';

export interface ThemeColors {
  // Primary colors
  primaryBg: string;
  secondaryBg: string;
  tertiaryBg: string;
  
  // Text colors
  textPrimary: string;
  textSecondary: string;
  textMuted: string;
  
  // Accent colors
  accentPrimary: string;
  accentSecondary: string;
  accentSuccess: string;
  accentWarning: string;
  accentDanger: string;
  
  // Border and overlay
  borderColor: string;
  overlayColor: string;
}

export interface ThemePreset {
  name: string;
  description: string;
  colors: ThemeColors;
}

@Injectable({
  providedIn: 'root'
})
export class ThemeService {
  private readonly STORAGE_KEY = 'autoagents-theme';

  // Default theme with improved colors
  private defaultColors: ThemeColors = {
    // Modern gradient backgrounds
    primaryBg: '#0f1419',
    secondaryBg: '#1a1f2e',
    tertiaryBg: '#252d3d',
    
    // Clear, readable text
    textPrimary: '#e6edf3',
    textSecondary: '#8b949e',
    textMuted: '#6e7681',
    
    // Vibrant accent colors
    accentPrimary: '#2d9ff5',
    accentSecondary: '#8e4ec6',
    accentSuccess: '#3fb950',
    accentWarning: '#d29922',
    accentDanger: '#f85149',
    
    // Subtle borders and overlays
    borderColor: 'rgba(240, 246, 252, 0.1)',
    overlayColor: 'rgba(1, 4, 9, 0.8)'
  };

  // Theme presets
  readonly themePresets: ThemePreset[] = [
    {
      name: 'Ocean Blue (Default)',
      description: 'Clean and modern with blue accents',
      colors: this.defaultColors
    },
    {
      name: 'Purple Dream',
      description: 'Rich purple and pink tones',
      colors: {
        primaryBg: '#1a0f2e',
        secondaryBg: '#2d1b4e',
        tertiaryBg: '#3d2a5f',
        textPrimary: '#f0e6ff',
        textSecondary: '#b8a9d9',
        textMuted: '#8b7ba8',
        accentPrimary: '#a855f7',
        accentSecondary: '#ec4899',
        accentSuccess: '#4ade80',
        accentWarning: '#fbbf24',
        accentDanger: '#f87171',
        borderColor: 'rgba(168, 85, 247, 0.2)',
        overlayColor: 'rgba(26, 15, 46, 0.85)'
      }
    },
    {
      name: 'Emerald Forest',
      description: 'Nature-inspired green theme',
      colors: {
        primaryBg: '#0a1f1a',
        secondaryBg: '#152e27',
        tertiaryBg: '#1f4037',
        textPrimary: '#e6fff9',
        textSecondary: '#94d2bd',
        textMuted: '#6b9080',
        accentPrimary: '#10b981',
        accentSecondary: '#059669',
        accentSuccess: '#34d399',
        accentWarning: '#fbbf24',
        accentDanger: '#f87171',
        borderColor: 'rgba(16, 185, 129, 0.2)',
        overlayColor: 'rgba(10, 31, 26, 0.85)'
      }
    },
    {
      name: 'Sunset Orange',
      description: 'Warm orange and red palette',
      colors: {
        primaryBg: '#1f1108',
        secondaryBg: '#2e1b0f',
        tertiaryBg: '#3d2817',
        textPrimary: '#fff5e6',
        textSecondary: '#ffb380',
        textMuted: '#cc8866',
        accentPrimary: '#f97316',
        accentSecondary: '#ea580c',
        accentSuccess: '#84cc16',
        accentWarning: '#eab308',
        accentDanger: '#dc2626',
        borderColor: 'rgba(249, 115, 22, 0.2)',
        overlayColor: 'rgba(31, 17, 8, 0.85)'
      }
    },
    {
      name: 'Cyber Teal',
      description: 'Futuristic cyan and teal',
      colors: {
        primaryBg: '#0a1a1f',
        secondaryBg: '#0f2830',
        tertiaryBg: '#163a47',
        textPrimary: '#e6ffff',
        textSecondary: '#7dd3c0',
        textMuted: '#5a9a8a',
        accentPrimary: '#06b6d4',
        accentSecondary: '#14b8a6',
        accentSuccess: '#22d3ee',
        accentWarning: '#fbbf24',
        accentDanger: '#f87171',
        borderColor: 'rgba(6, 182, 212, 0.2)',
        overlayColor: 'rgba(10, 26, 31, 0.85)'
      }
    }
  ];

  // Current theme signal
  private _currentTheme = signal<ThemeColors>(this.loadTheme());
  
  // Public readonly signal
  readonly currentTheme = this._currentTheme.asReadonly();

  constructor() {
    // Apply theme on initialization and whenever it changes
    effect(() => {
      this.applyTheme(this._currentTheme());
    });
  }

  /**
   * Load theme from localStorage or use default
   */
  private loadTheme(): ThemeColors {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Validate that all required properties exist
        if (this.isValidThemeColors(parsed)) {
          return parsed;
        }
      }
    } catch (error) {
      console.error('Failed to load theme:', error);
    }
    return this.defaultColors;
  }

  /**
   * Validate theme colors object
   */
  private isValidThemeColors(colors: any): colors is ThemeColors {
    const requiredKeys: (keyof ThemeColors)[] = [
      'primaryBg', 'secondaryBg', 'tertiaryBg',
      'textPrimary', 'textSecondary', 'textMuted',
      'accentPrimary', 'accentSecondary',
      'borderColor', 'overlayColor'
    ];
    return requiredKeys.every(key => typeof colors[key] === 'string');
  }

  /**
   * Save theme to localStorage
   */
  private saveTheme(colors: ThemeColors): void {
    try {
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(colors));
    } catch (error) {
      console.error('Failed to save theme:', error);
    }
  }

  /**
   * Apply theme colors to CSS variables
   */
  private applyTheme(colors: ThemeColors): void {
    const root = document.documentElement;
    
    // Apply all color variables
    root.style.setProperty('--color-primary-bg', colors.primaryBg);
    root.style.setProperty('--color-secondary-bg', colors.secondaryBg);
    root.style.setProperty('--color-tertiary-bg', colors.tertiaryBg);
    
    root.style.setProperty('--color-text-primary', colors.textPrimary);
    root.style.setProperty('--color-text-secondary', colors.textSecondary);
    root.style.setProperty('--color-text-muted', colors.textMuted);
    
    root.style.setProperty('--color-accent-primary', colors.accentPrimary);
    root.style.setProperty('--color-accent-secondary', colors.accentSecondary);
    root.style.setProperty('--color-accent-success', colors.accentSuccess);
    root.style.setProperty('--color-accent-warning', colors.accentWarning);
    root.style.setProperty('--color-accent-danger', colors.accentDanger);
    
    root.style.setProperty('--color-border', colors.borderColor);
    root.style.setProperty('--color-overlay', colors.overlayColor);
  }

  /**
   * Update theme colors
   */
  setTheme(colors: Partial<ThemeColors>): void {
    const updated = { ...this._currentTheme(), ...colors };
    this._currentTheme.set(updated);
    this.saveTheme(updated);
  }

  /**
   * Apply a preset theme
   */
  applyPreset(preset: ThemePreset): void {
    this._currentTheme.set(preset.colors);
    this.saveTheme(preset.colors);
  }

  /**
   * Reset to default theme
   */
  resetToDefault(): void {
    this._currentTheme.set(this.defaultColors);
    this.saveTheme(this.defaultColors);
  }

  /**
   * Update a single color property
   */
  updateColor(property: keyof ThemeColors, value: string): void {
    const updated = { ...this._currentTheme(), [property]: value };
    this._currentTheme.set(updated);
    this.saveTheme(updated);
  }

  /**
   * Get current theme as object
   */
  getCurrentTheme(): ThemeColors {
    return this._currentTheme();
  }
}
