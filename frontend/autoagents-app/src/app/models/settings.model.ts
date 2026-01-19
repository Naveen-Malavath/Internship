/**
 * Settings Model - Per-Project Settings for AutoAgents
 */

// Custom field types that can be added
export type CustomFieldType = 'text' | 'textarea' | 'number' | 'select' | 'multiselect' | 'date' | 'checkbox' | 'url';

// Custom field definition
export interface CustomField {
  id: string;
  name: string;
  key: string;           // Unique key for the field (generated from name)
  type: CustomFieldType;
  description?: string;
  required: boolean;
  enabled: boolean;
  options?: string[];    // For select/multiselect types
  defaultValue?: any;
  placeholder?: string;
  order: number;         // Display order
  isBuiltIn: boolean;    // True for system fields, false for custom
}

// Workflow settings - control which steps are enabled
export interface WorkflowSettings {
  enableStories: boolean;      // Enable/disable story generation step
  enableWireframes: boolean;   // Enable/disable wireframes step
}

// Story configuration
export interface StorySettings {
  perFeature: number;          // Number of stories to generate per feature
  minPerFeature: number;       // Minimum stories allowed
  maxPerFeature: number;       // Maximum stories allowed
  fields: CustomField[];       // Both built-in and custom fields
}

// Feature configuration
export interface FeatureSettings {
  defaultCount: number;        // Default number of features to generate
  minCount: number;            // Minimum features
  maxCount: number;            // Maximum features
  fields: CustomField[];       // Both built-in and custom fields
}

// Complete project settings
export interface ProjectSettings {
  workflow: WorkflowSettings;
  stories: StorySettings;
  features: FeatureSettings;
  isConfigured: boolean;       // Whether the project has been configured
}

// Built-in story fields
export const BUILT_IN_STORY_FIELDS: CustomField[] = [
  { 
    id: 'story-title', 
    name: 'Title', 
    key: 'title', 
    type: 'text', 
    description: 'Story title', 
    required: true, 
    enabled: true, 
    order: 1, 
    isBuiltIn: true,
    placeholder: 'Enter story title'
  },
  { 
    id: 'story-description', 
    name: 'Description', 
    key: 'description', 
    type: 'textarea', 
    description: 'Detailed story description', 
    required: true, 
    enabled: true, 
    order: 2, 
    isBuiltIn: true,
    placeholder: 'Describe the user story'
  },
  { 
    id: 'story-acceptance', 
    name: 'Acceptance Criteria', 
    key: 'acceptanceCriteria', 
    type: 'textarea', 
    description: 'Conditions for story completion', 
    required: false, 
    enabled: true, 
    order: 3, 
    isBuiltIn: true,
    placeholder: 'List the acceptance criteria'
  },
  { 
    id: 'story-priority', 
    name: 'Priority', 
    key: 'priority', 
    type: 'select', 
    description: 'Story priority level', 
    required: false, 
    enabled: false, 
    options: ['Critical', 'High', 'Medium', 'Low'],
    order: 4, 
    isBuiltIn: true
  },
  { 
    id: 'story-points', 
    name: 'Story Points', 
    key: 'storyPoints', 
    type: 'select', 
    description: 'Effort estimation in points', 
    required: false, 
    enabled: false, 
    options: ['1', '2', '3', '5', '8', '13', '21'],
    order: 5, 
    isBuiltIn: true
  },
  { 
    id: 'story-assignee', 
    name: 'Assignee', 
    key: 'assignee', 
    type: 'text', 
    description: 'Person responsible for this story', 
    required: false, 
    enabled: false, 
    order: 6, 
    isBuiltIn: true,
    placeholder: 'Enter assignee name'
  },
  { 
    id: 'story-sprint', 
    name: 'Sprint', 
    key: 'sprint', 
    type: 'text', 
    description: 'Sprint assignment', 
    required: false, 
    enabled: false, 
    order: 7, 
    isBuiltIn: true,
    placeholder: 'Enter sprint name'
  },
  { 
    id: 'story-dueDate', 
    name: 'Due Date', 
    key: 'dueDate', 
    type: 'date', 
    description: 'Target completion date', 
    required: false, 
    enabled: false, 
    order: 8, 
    isBuiltIn: true
  }
];

// Built-in feature fields
export const BUILT_IN_FEATURE_FIELDS: CustomField[] = [
  { 
    id: 'feature-name', 
    name: 'Name', 
    key: 'name', 
    type: 'text', 
    description: 'Feature name', 
    required: true, 
    enabled: true, 
    order: 1, 
    isBuiltIn: true,
    placeholder: 'Enter feature name'
  },
  { 
    id: 'feature-description', 
    name: 'Description', 
    key: 'description', 
    type: 'textarea', 
    description: 'Feature overview and details', 
    required: true, 
    enabled: true, 
    order: 2, 
    isBuiltIn: true,
    placeholder: 'Describe the feature'
  },
  { 
    id: 'feature-category', 
    name: 'Category', 
    key: 'category', 
    type: 'select', 
    description: 'Feature category/type', 
    required: false, 
    enabled: true, 
    options: ['Core', 'Enhancement', 'Integration', 'Analytics', 'Security', 'Performance', 'UX/UI', 'Other'],
    order: 3, 
    isBuiltIn: true
  },
  { 
    id: 'feature-acceptance', 
    name: 'Acceptance Criteria', 
    key: 'acceptanceCriteria', 
    type: 'textarea', 
    description: 'Feature completion criteria', 
    required: false, 
    enabled: true, 
    order: 4, 
    isBuiltIn: true,
    placeholder: 'List the acceptance criteria'
  },
  { 
    id: 'feature-problem', 
    name: 'Problem Statement', 
    key: 'problemStatement', 
    type: 'textarea', 
    description: 'Problem being solved', 
    required: false, 
    enabled: true, 
    order: 5, 
    isBuiltIn: true,
    placeholder: 'What problem does this feature solve?'
  },
  { 
    id: 'feature-objective', 
    name: 'Business Objective', 
    key: 'businessObjective', 
    type: 'textarea', 
    description: 'Business goal alignment', 
    required: false, 
    enabled: true, 
    order: 6, 
    isBuiltIn: true,
    placeholder: 'How does this align with business goals?'
  },
  { 
    id: 'feature-persona', 
    name: 'User Persona', 
    key: 'userPersona', 
    type: 'textarea', 
    description: 'Target user description', 
    required: false, 
    enabled: true, 
    order: 7, 
    isBuiltIn: true,
    placeholder: 'Who is the target user?'
  },
  { 
    id: 'feature-metrics', 
    name: 'Success Metrics', 
    key: 'successMetrics', 
    type: 'textarea', 
    description: 'KPIs and measurements', 
    required: false, 
    enabled: true, 
    order: 8, 
    isBuiltIn: true,
    placeholder: 'How will success be measured?'
  },
  { 
    id: 'feature-dependencies', 
    name: 'Dependencies', 
    key: 'dependencies', 
    type: 'textarea', 
    description: 'Related features/systems', 
    required: false, 
    enabled: true, 
    order: 9, 
    isBuiltIn: true,
    placeholder: 'List any dependencies'
  },
  { 
    id: 'feature-priority', 
    name: 'Priority', 
    key: 'priority', 
    type: 'select', 
    description: 'Feature priority level', 
    required: false, 
    enabled: false, 
    options: ['Critical', 'High', 'Medium', 'Low'],
    order: 10, 
    isBuiltIn: true
  },
  { 
    id: 'feature-complexity', 
    name: 'Complexity', 
    key: 'complexity', 
    type: 'select', 
    description: 'Implementation complexity', 
    required: false, 
    enabled: false, 
    options: ['Low', 'Medium', 'High', 'Very High'],
    order: 11, 
    isBuiltIn: true
  },
  { 
    id: 'feature-technical', 
    name: 'Technical Notes', 
    key: 'technicalNotes', 
    type: 'textarea', 
    description: 'Implementation hints and technical details', 
    required: false, 
    enabled: false, 
    order: 12, 
    isBuiltIn: true,
    placeholder: 'Add technical notes'
  },
  { 
    id: 'feature-estimate', 
    name: 'Estimate', 
    key: 'estimate', 
    type: 'text', 
    description: 'Development time estimate', 
    required: false, 
    enabled: false, 
    order: 13, 
    isBuiltIn: true,
    placeholder: 'e.g., 2 weeks'
  },
  { 
    id: 'feature-owner', 
    name: 'Owner', 
    key: 'owner', 
    type: 'text', 
    description: 'Feature owner/lead', 
    required: false, 
    enabled: false, 
    order: 14, 
    isBuiltIn: true,
    placeholder: 'Enter owner name'
  }
];

// Default settings to match current behavior
export const DEFAULT_SETTINGS: ProjectSettings = {
  workflow: {
    enableStories: true,
    enableWireframes: true
  },
  stories: {
    perFeature: 2,
    minPerFeature: 1,
    maxPerFeature: 10,
    fields: JSON.parse(JSON.stringify(BUILT_IN_STORY_FIELDS))
  },
  features: {
    defaultCount: 6,
    minCount: 1,
    maxCount: 20,
    fields: JSON.parse(JSON.stringify(BUILT_IN_FEATURE_FIELDS))
  },
  isConfigured: false
};

// Helper to create a deep copy of default settings
export function getDefaultSettings(): ProjectSettings {
  return JSON.parse(JSON.stringify(DEFAULT_SETTINGS));
}

// Generate a unique key from field name
export function generateFieldKey(name: string): string {
  return name
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '');
}

// Generate a unique field ID
export function generateFieldId(prefix: string): string {
  return `${prefix}-custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

// Create a new custom field
export function createCustomField(
  name: string, 
  type: CustomFieldType, 
  prefix: 'story' | 'feature',
  order: number
): CustomField {
  return {
    id: generateFieldId(prefix),
    name,
    key: generateFieldKey(name),
    type,
    description: '',
    required: false,
    enabled: true,
    options: type === 'select' || type === 'multiselect' ? ['Option 1', 'Option 2'] : undefined,
    order,
    isBuiltIn: false
  };
}

// Field type display configuration
export const FIELD_TYPE_CONFIG: { type: CustomFieldType; label: string; icon: string }[] = [
  { type: 'text', label: 'Text', icon: 'short_text' },
  { type: 'textarea', label: 'Long Text', icon: 'notes' },
  { type: 'number', label: 'Number', icon: 'tag' },
  { type: 'select', label: 'Dropdown', icon: 'arrow_drop_down_circle' },
  { type: 'multiselect', label: 'Multi-Select', icon: 'checklist' },
  { type: 'date', label: 'Date', icon: 'calendar_today' },
  { type: 'checkbox', label: 'Checkbox', icon: 'check_box' },
  { type: 'url', label: 'URL', icon: 'link' }
];

// Legacy field config for backwards compatibility
export interface FieldConfig {
  key: string;
  label: string;
  description: string;
  defaultEnabled: boolean;
}

export const STORY_FIELD_CONFIG: FieldConfig[] = BUILT_IN_STORY_FIELDS.map(f => ({
  key: f.key,
  label: f.name,
  description: f.description || '',
  defaultEnabled: f.enabled
}));

export const FEATURE_FIELD_CONFIG: FieldConfig[] = BUILT_IN_FEATURE_FIELDS.map(f => ({
  key: f.key,
  label: f.name,
  description: f.description || '',
  defaultEnabled: f.enabled
}));
