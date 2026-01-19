import { Injectable, signal, computed } from '@angular/core';
import { 
  ProjectSettings, 
  DEFAULT_SETTINGS, 
  getDefaultSettings,
  WorkflowSettings,
  StorySettings,
  FeatureSettings,
  CustomField
} from '../models/settings.model';

const STORAGE_KEY = 'autoagents_default_settings';

/**
 * SettingsService manages global default settings for new projects.
 * Settings are stored in localStorage and used as templates when creating new projects.
 */
@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  // Signal for reactive settings
  private _defaultSettings = signal<ProjectSettings>(this.loadFromStorage());

  // Computed signals for easy access to specific settings
  readonly defaultSettings = computed(() => this._defaultSettings());
  readonly workflowSettings = computed(() => this._defaultSettings().workflow);
  readonly storySettings = computed(() => this._defaultSettings().stories);
  readonly featureSettings = computed(() => this._defaultSettings().features);

  constructor() {
    console.log('[SettingsService] Initialized with settings:', this._defaultSettings());
  }

  /**
   * Load settings from localStorage, or return defaults if not found
   */
  private loadFromStorage(): ProjectSettings {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Merge with defaults to ensure all properties exist
        return this.mergeWithDefaults(parsed);
      }
    } catch (error) {
      console.error('[SettingsService] Error loading settings from storage:', error);
    }
    return getDefaultSettings();
  }

  /**
   * Merge stored settings with defaults to handle new properties
   */
  private mergeWithDefaults(stored: Partial<ProjectSettings>): ProjectSettings {
    const defaults = getDefaultSettings();
    
    return {
      workflow: { ...defaults.workflow, ...stored.workflow },
      stories: { 
        ...defaults.stories, 
        ...stored.stories,
        fields: stored.stories?.fields && Array.isArray(stored.stories.fields) 
          ? stored.stories.fields 
          : defaults.stories.fields
      },
      features: { 
        ...defaults.features, 
        ...stored.features,
        fields: stored.features?.fields && Array.isArray(stored.features.fields) 
          ? stored.features.fields 
          : defaults.features.fields
      },
      isConfigured: stored.isConfigured ?? false
    };
  }

  /**
   * Save settings to localStorage
   */
  private saveToStorage(settings: ProjectSettings): void {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
      console.log('[SettingsService] Settings saved to storage');
    } catch (error) {
      console.error('[SettingsService] Error saving settings to storage:', error);
    }
  }

  /**
   * Get a copy of current default settings for a new project
   */
  getSettingsForNewProject(): ProjectSettings {
    return JSON.parse(JSON.stringify(this._defaultSettings()));
  }

  /**
   * Update all default settings
   */
  updateSettings(settings: ProjectSettings): void {
    this._defaultSettings.set(settings);
    this.saveToStorage(settings);
    console.log('[SettingsService] Settings updated:', settings);
  }

  /**
   * Update workflow settings only
   */
  updateWorkflowSettings(workflow: WorkflowSettings): void {
    const current = this._defaultSettings();
    const updated = { ...current, workflow };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Update story settings only
   */
  updateStorySettings(stories: StorySettings): void {
    const current = this._defaultSettings();
    const updated = { ...current, stories };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Update feature settings only
   */
  updateFeatureSettings(features: FeatureSettings): void {
    const current = this._defaultSettings();
    const updated = { ...current, features };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Toggle a specific story field by key
   */
  toggleStoryField(fieldKey: string, enabled: boolean): void {
    const current = this._defaultSettings();
    const updatedFields = current.stories.fields.map(f => 
      f.key === fieldKey ? { ...f, enabled } : f
    );
    const updated = {
      ...current,
      stories: {
        ...current.stories,
        fields: updatedFields
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Toggle a specific feature field by key
   */
  toggleFeatureField(fieldKey: string, enabled: boolean): void {
    const current = this._defaultSettings();
    const updatedFields = current.features.fields.map(f => 
      f.key === fieldKey ? { ...f, enabled } : f
    );
    const updated = {
      ...current,
      features: {
        ...current.features,
        fields: updatedFields
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Update stories per feature count
   */
  updateStoriesPerFeature(count: number): void {
    const current = this._defaultSettings();
    const clamped = Math.min(Math.max(count, current.stories.minPerFeature), current.stories.maxPerFeature);
    const updated = {
      ...current,
      stories: {
        ...current.stories,
        perFeature: clamped
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Update default feature count
   */
  updateDefaultFeatureCount(count: number): void {
    const current = this._defaultSettings();
    const clamped = Math.min(Math.max(count, current.features.minCount), current.features.maxCount);
    const updated = {
      ...current,
      features: {
        ...current.features,
        defaultCount: clamped
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Toggle stories enabled/disabled
   */
  toggleStoriesEnabled(enabled: boolean): void {
    const current = this._defaultSettings();
    const updated = {
      ...current,
      workflow: {
        ...current.workflow,
        enableStories: enabled
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Toggle wireframes enabled/disabled
   */
  toggleWireframesEnabled(enabled: boolean): void {
    const current = this._defaultSettings();
    const updated = {
      ...current,
      workflow: {
        ...current.workflow,
        enableWireframes: enabled
      }
    };
    this._defaultSettings.set(updated);
    this.saveToStorage(updated);
  }

  /**
   * Reset all settings to defaults
   */
  resetToDefaults(): void {
    const defaults = getDefaultSettings();
    this._defaultSettings.set(defaults);
    this.saveToStorage(defaults);
    console.log('[SettingsService] Settings reset to defaults');
  }

  /**
   * Check if settings differ from defaults
   */
  hasCustomSettings(): boolean {
    return JSON.stringify(this._defaultSettings()) !== JSON.stringify(DEFAULT_SETTINGS);
  }
  
  /**
   * Get enabled story fields
   */
  getEnabledStoryFields(): CustomField[] {
    return this._defaultSettings().stories.fields.filter(f => f.enabled);
  }
  
  /**
   * Get enabled feature fields
   */
  getEnabledFeatureFields(): CustomField[] {
    return this._defaultSettings().features.fields.filter(f => f.enabled);
  }
}
