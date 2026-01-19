import { Component, inject, signal, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialogModule, MatDialogRef, MAT_DIALOG_DATA } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSliderModule } from '@angular/material/slider';
import { MatTooltipModule } from '@angular/material/tooltip';
import { 
  ProjectSettings, 
  STORY_FIELD_CONFIG, 
  FEATURE_FIELD_CONFIG,
  getDefaultSettings
} from '../../models/settings.model';

export interface ProjectSettingsDialogData {
  projectName: string;
  projectKey: string;
  settings: ProjectSettings;
}

@Component({
  selector: 'app-project-settings-modal',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatDialogModule,
    MatButtonModule,
    MatIconModule,
    MatSlideToggleModule,
    MatSliderModule,
    MatTooltipModule
  ],
  templateUrl: './project-settings-modal.component.html',
  styleUrls: ['./project-settings-modal.component.scss']
})
export class ProjectSettingsModalComponent {
  dialogRef = inject(MatDialogRef<ProjectSettingsModalComponent>);
  
  projectName: string;
  projectKey: string;
  settings: ProjectSettings;
  
  storyFieldConfig = STORY_FIELD_CONFIG;
  featureFieldConfig = FEATURE_FIELD_CONFIG;
  
  showAdvancedSettings = signal(false);
  
  constructor(@Inject(MAT_DIALOG_DATA) public data: ProjectSettingsDialogData) {
    this.projectName = data.projectName;
    this.projectKey = data.projectKey;
    // Deep clone settings to avoid mutating original
    this.settings = JSON.parse(JSON.stringify(data.settings));
  }
  
  toggleAdvancedSettings(): void {
    this.showAdvancedSettings.update(v => !v);
  }
  
  onStoriesEnabledChange(enabled: boolean): void {
    this.settings.workflow.enableStories = enabled;
  }
  
  onWireframesEnabledChange(enabled: boolean): void {
    this.settings.workflow.enableWireframes = enabled;
  }
  
  onStoriesPerFeatureChange(value: number): void {
    this.settings.stories.perFeature = value;
  }
  
  onFeatureCountChange(value: number): void {
    this.settings.features.defaultCount = value;
  }
  
  onStoryFieldChange(fieldKey: string, enabled: boolean): void {
    (this.settings.stories.fields as any)[fieldKey] = enabled;
  }
  
  onFeatureFieldChange(fieldKey: string, enabled: boolean): void {
    (this.settings.features.fields as any)[fieldKey] = enabled;
  }
  
  isStoryFieldEnabled(fieldKey: string): boolean {
    return (this.settings.stories.fields as any)[fieldKey] ?? false;
  }
  
  isFeatureFieldEnabled(fieldKey: string): boolean {
    return (this.settings.features.fields as any)[fieldKey] ?? false;
  }
  
  resetToDefaults(): void {
    this.settings = JSON.parse(JSON.stringify(getDefaultSettings()));
  }
  
  save(): void {
    this.dialogRef.close(this.settings);
  }
  
  cancel(): void {
    this.dialogRef.close();
  }
}
