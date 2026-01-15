import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatRippleModule } from '@angular/material/core';
import { ThemeService, ThemeColors, ThemePreset } from '../../services/theme.service';

@Component({
  selector: 'app-settings',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatButtonModule,
    MatTooltipModule,
    MatRippleModule
  ],
  templateUrl: './settings.component.html',
  styleUrls: ['./settings.component.scss']
})
export class SettingsComponent {
  themeService = inject(ThemeService);
  
  // Active tab
  activeTab: 'appearance' | 'general' = 'appearance';
  
  // Color categories for organized display
  colorCategories = [
    {
      name: 'Background Colors',
      colors: [
        { key: 'primaryBg' as keyof ThemeColors, label: 'Primary Background', description: 'Main app background' },
        { key: 'secondaryBg' as keyof ThemeColors, label: 'Secondary Background', description: 'Cards and panels' },
        { key: 'tertiaryBg' as keyof ThemeColors, label: 'Tertiary Background', description: 'Hover and elevated elements' }
      ]
    },
    {
      name: 'Text Colors',
      colors: [
        { key: 'textPrimary' as keyof ThemeColors, label: 'Primary Text', description: 'Main content text' },
        { key: 'textSecondary' as keyof ThemeColors, label: 'Secondary Text', description: 'Supporting text' },
        { key: 'textMuted' as keyof ThemeColors, label: 'Muted Text', description: 'Disabled or subtle text' }
      ]
    },
    {
      name: 'Accent Colors',
      colors: [
        { key: 'accentPrimary' as keyof ThemeColors, label: 'Primary Accent', description: 'Links and primary actions' },
        { key: 'accentSecondary' as keyof ThemeColors, label: 'Secondary Accent', description: 'Secondary actions' },
        { key: 'accentSuccess' as keyof ThemeColors, label: 'Success', description: 'Success states' },
        { key: 'accentWarning' as keyof ThemeColors, label: 'Warning', description: 'Warning states' },
        { key: 'accentDanger' as keyof ThemeColors, label: 'Danger', description: 'Error states' }
      ]
    },
    {
      name: 'UI Elements',
      colors: [
        { key: 'borderColor' as keyof ThemeColors, label: 'Border Color', description: 'Dividers and borders' },
        { key: 'overlayColor' as keyof ThemeColors, label: 'Overlay Color', description: 'Modal backgrounds' }
      ]
    }
  ];

  setActiveTab(tab: 'appearance' | 'general'): void {
    this.activeTab = tab;
  }

  onColorChange(property: keyof ThemeColors, event: Event): void {
    const input = event.target as HTMLInputElement;
    this.themeService.updateColor(property, input.value);
  }

  applyPreset(preset: ThemePreset): void {
    this.themeService.applyPreset(preset);
  }

  resetToDefaults(): void {
    if (confirm('Are you sure you want to reset all colors to default? This action cannot be undone.')) {
      this.themeService.resetToDefault();
    }
  }

  getCurrentColor(property: keyof ThemeColors): string {
    return this.themeService.getCurrentTheme()[property];
  }

  exportTheme(): void {
    const theme = this.themeService.getCurrentTheme();
    const dataStr = JSON.stringify(theme, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'autoagents-theme.json';
    link.click();
    URL.revokeObjectURL(url);
  }

  importTheme(): void {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e: Event) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const theme = JSON.parse(event.target?.result as string);
            this.themeService.setTheme(theme);
            alert('Theme imported successfully!');
          } catch (error) {
            alert('Failed to import theme. Please check the file format.');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  }
}
