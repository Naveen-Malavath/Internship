import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatMenuModule } from '@angular/material/menu';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { CdkDragDrop, DragDropModule, moveItemInArray } from '@angular/cdk/drag-drop';
import { NavigationService } from '../../services/navigation.service';
import { ProjectStateService, ProjectData } from '../../services/project-state.service';
import { 
  ProjectSettings, 
  CustomField, 
  CustomFieldType,
  FIELD_TYPE_CONFIG,
  createCustomField,
  getDefaultSettings
} from '../../models/settings.model';

@Component({
  selector: 'app-project-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatSliderModule,
    MatTooltipModule,
    MatSelectModule,
    MatInputModule,
    MatFormFieldModule,
    MatMenuModule,
    MatDialogModule,
    DragDropModule
  ],
  templateUrl: './project-settings.component.html',
  styleUrls: ['./project-settings.component.scss']
})
export class ProjectSettingsComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private navService = inject(NavigationService);
  private projectStateService = inject(ProjectStateService);
  
  // Project data
  project = signal<ProjectData | null>(null);
  projectId = signal<string>('');
  
  // Settings
  settings = signal<ProjectSettings>(getDefaultSettings());
  
  // UI State
  activeTab = signal<'workflow' | 'features' | 'stories'>('workflow');
  editingField = signal<CustomField | null>(null);
  showAddFieldForm = signal<'features' | 'stories' | null>(null);
  
  // New field form
  newFieldName = '';
  newFieldType: CustomFieldType = 'text';
  newFieldDescription = '';
  newFieldRequired = false;
  newFieldOptions: string[] = [];
  
  // Field type options
  fieldTypeConfig = FIELD_TYPE_CONFIG;
  
  // Computed values
  enabledFeatureFields = computed(() => 
    this.settings().features.fields.filter(f => f.enabled).length
  );
  enabledStoryFields = computed(() => 
    this.settings().stories.fields.filter(f => f.enabled).length
  );
  
  ngOnInit(): void {
    // Get project ID from route
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.projectId.set(id);
    }
    
    // Get project data from state service
    const projectData = this.projectStateService.getCurrentProject();
    if (projectData) {
      this.project.set(projectData);
      
      // Load project settings or use defaults
      if (projectData.settings) {
        this.settings.set(JSON.parse(JSON.stringify(projectData.settings)));
      }
    }
    
    console.log('[ProjectSettings] Initialized with project:', this.project()?.projectName);
  }
  
  // Tab navigation
  setActiveTab(tab: 'workflow' | 'features' | 'stories'): void {
    this.activeTab.set(tab);
    this.cancelAddField();
  }
  
  // Workflow settings
  onStoriesEnabledChange(enabled: boolean): void {
    this.settings.update(s => ({
      ...s,
      workflow: { ...s.workflow, enableStories: enabled }
    }));
  }
  
  onWireframesEnabledChange(enabled: boolean): void {
    this.settings.update(s => ({
      ...s,
      workflow: { ...s.workflow, enableWireframes: enabled }
    }));
  }
  
  onStoriesPerFeatureChange(value: number): void {
    this.settings.update(s => ({
      ...s,
      stories: { ...s.stories, perFeature: value }
    }));
  }
  
  onFeatureCountChange(value: number): void {
    this.settings.update(s => ({
      ...s,
      features: { ...s.features, defaultCount: value }
    }));
  }
  
  // Field management
  toggleFieldEnabled(fieldType: 'features' | 'stories', fieldId: string): void {
    this.settings.update(s => {
      const fields = [...s[fieldType].fields];
      const index = fields.findIndex(f => f.id === fieldId);
      if (index !== -1) {
        fields[index] = { ...fields[index], enabled: !fields[index].enabled };
      }
      return {
        ...s,
        [fieldType]: { ...s[fieldType], fields }
      };
    });
  }
  
  toggleFieldRequired(fieldType: 'features' | 'stories', fieldId: string): void {
    this.settings.update(s => {
      const fields = [...s[fieldType].fields];
      const index = fields.findIndex(f => f.id === fieldId);
      if (index !== -1) {
        fields[index] = { ...fields[index], required: !fields[index].required };
      }
      return {
        ...s,
        [fieldType]: { ...s[fieldType], fields }
      };
    });
  }
  
  startEditField(field: CustomField): void {
    this.editingField.set(JSON.parse(JSON.stringify(field)));
  }
  
  saveEditField(fieldType: 'features' | 'stories'): void {
    const editing = this.editingField();
    if (!editing) return;
    
    this.settings.update(s => {
      const fields = [...s[fieldType].fields];
      const index = fields.findIndex(f => f.id === editing.id);
      if (index !== -1) {
        fields[index] = editing;
      }
      return {
        ...s,
        [fieldType]: { ...s[fieldType], fields }
      };
    });
    
    this.editingField.set(null);
  }
  
  cancelEditField(): void {
    this.editingField.set(null);
  }
  
  deleteField(fieldType: 'features' | 'stories', fieldId: string): void {
    if (!confirm('Are you sure you want to delete this custom field?')) return;
    
    this.settings.update(s => {
      const fields = s[fieldType].fields.filter(f => f.id !== fieldId);
      return {
        ...s,
        [fieldType]: { ...s[fieldType], fields }
      };
    });
  }
  
  // Add new field
  showAddField(fieldType: 'features' | 'stories'): void {
    this.showAddFieldForm.set(fieldType);
    this.resetNewFieldForm();
  }
  
  cancelAddField(): void {
    this.showAddFieldForm.set(null);
    this.resetNewFieldForm();
  }
  
  resetNewFieldForm(): void {
    this.newFieldName = '';
    this.newFieldType = 'text';
    this.newFieldDescription = '';
    this.newFieldRequired = false;
    this.newFieldOptions = [];
  }
  
  addNewField(): void {
    const fieldType = this.showAddFieldForm();
    if (!fieldType || !this.newFieldName.trim()) return;
    
    const prefix = fieldType === 'features' ? 'feature' : 'story';
    const currentFields = this.settings()[fieldType].fields;
    const maxOrder = Math.max(...currentFields.map(f => f.order), 0);
    
    const newField = createCustomField(
      this.newFieldName.trim(),
      this.newFieldType,
      prefix,
      maxOrder + 1
    );
    
    newField.description = this.newFieldDescription;
    newField.required = this.newFieldRequired;
    
    if ((this.newFieldType === 'select' || this.newFieldType === 'multiselect') && this.newFieldOptions.length > 0) {
      newField.options = this.newFieldOptions.filter(o => o.trim());
    }
    
    this.settings.update(s => ({
      ...s,
      [fieldType]: {
        ...s[fieldType],
        fields: [...s[fieldType].fields, newField]
      }
    }));
    
    this.cancelAddField();
  }
  
  addOption(): void {
    this.newFieldOptions.push('');
  }
  
  removeOption(index: number): void {
    this.newFieldOptions.splice(index, 1);
  }
  
  trackByIndex(index: number): number {
    return index;
  }
  
  // Drag and drop reordering
  dropField(event: CdkDragDrop<CustomField[]>, fieldType: 'features' | 'stories'): void {
    this.settings.update(s => {
      const fields = [...s[fieldType].fields];
      moveItemInArray(fields, event.previousIndex, event.currentIndex);
      // Update order values
      fields.forEach((f, i) => f.order = i + 1);
      return {
        ...s,
        [fieldType]: { ...s[fieldType], fields }
      };
    });
  }
  
  // Save and navigate
  saveSettings(): void {
    const project = this.project();
    if (!project) return;
    
    const updatedSettings = {
      ...this.settings(),
      isConfigured: true
    };
    
    // Update project with settings
    this.projectStateService.updateProjectSettings(updatedSettings);
    
    console.log('[ProjectSettings] Settings saved:', updatedSettings);
  }
  
  saveAndContinue(): void {
    this.saveSettings();
    
    // Navigate to workspace
    console.log('[ProjectSettings] Navigating to workspace...');
    this.navService.navigate('/workspace');
  }
  
  goBack(): void {
    this.navService.navigate('/projects');
  }
  
  // Get field type label
  getFieldTypeLabel(type: CustomFieldType): string {
    return this.fieldTypeConfig.find(t => t.type === type)?.label || type;
  }
  
  getFieldTypeIcon(type: CustomFieldType): string {
    return this.fieldTypeConfig.find(t => t.type === type)?.icon || 'text_fields';
  }
}
