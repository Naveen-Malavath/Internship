import { Component, signal, ChangeDetectorRef, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatDialog, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ApiService } from '../../services/api.service';
import { LoadingDialogComponent } from '../loading-dialog/loading-dialog.component';
import { PromptReviewDialogComponent } from '../prompt-review-dialog/prompt-review-dialog.component';
import { FeatureDetailModalComponent } from '../feature-detail-modal/feature-detail-modal.component';
import { Feature, Story } from '../../services/api.service';
import { DevModeService } from '../../services/dev-mode.service';
import { MOCK_FEATURES, MOCK_STORIES, MOCK_PROJECT_CONTEXT } from '../../services/dev-data';

interface Template {
  title: string;
  industry: string;
  methodology: string;
  description: string;
  features: string[];
  personas: string;
  additionalTag?: string;
}

interface Workflow {
  title: string;
  type: string;
  description: string;
  issueTypes: string[];
  cadence: string;
}

interface ProjectData {
  projectName: string;
  projectKey: string;
  industry: string;
  methodology: string;
  timezone: string;
  teamSize: string;
  kickoffDate: string;
  targetLaunch: string;
  promptSummary: string;
  selectedWorkflow?: Workflow;
  attachments: File[];
  executiveSummary: string;
  acceptanceCriteria: string;
  generatedEpics: string;
  generatedRisks: string;
  agentGuidance: string;
  epicIdeas: string[];
  riskHighlights: string[];
  finalPrompt: string;
}

@Component({
  selector: 'app-create-project-modal',
  standalone: true,
  imports: [
    CommonModule, 
    FormsModule,
    MatDialogModule, 
    MatButtonModule, 
    MatIconModule,
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatTooltipModule
  ],
  templateUrl: './create-project-modal.component.html',
  styleUrls: ['./create-project-modal.component.scss']
})
export class CreateProjectModalComponent {
  currentStep = signal(1);
  selectedTemplate = signal<Template | null>(null);
  
  // Loading states for generate buttons
  loadingSummary = signal(false);
  loadingEpics = signal(false);
  loadingAcceptance = signal(false);
  loadingRisks = signal(false);
  loadingFeatures = signal(false);
  loadingStories = signal(false);
  
  // Features
  generatedFeatures = signal<Feature[]>([]);
  manualFeatures = signal<string[]>([]);
  allFeaturesApproved = signal<boolean>(false);
  
  // Stories
  generatedStories = signal<Story[]>([]);
  manualStories = signal<string[]>([]);
  allStoriesApproved = signal<boolean>(false);
  
  // Dev mode service
  devModeService = inject(DevModeService);
  
  constructor(
    private apiService: ApiService,
    private dialog: MatDialog,
    private dialogRef: MatDialogRef<CreateProjectModalComponent>,
    private cdr: ChangeDetectorRef
  ) {}
  
  projectData: ProjectData = {
    projectName: '',
    projectKey: '',
    industry: '',
    methodology: '',
    timezone: 'UTC',
    teamSize: 'Not sure yet',
    kickoffDate: '',
    targetLaunch: '',
    promptSummary: '',
    attachments: [],
    executiveSummary: '',
    acceptanceCriteria: '',
    generatedEpics: '',
    generatedRisks: '',
    agentGuidance: '',
    epicIdeas: [],
    riskHighlights: [],
    finalPrompt: ''
  };
  
  steps = [
    { number: 1, label: 'TEMPLATE' },
    { number: 2, label: 'PROJECT DETAILS' },
    { number: 3, label: 'AI ASSIST' },
    { number: 4, label: 'FEATURES' },
    { number: 5, label: 'STORIES' }
  ];

  templates: Template[] = [
    {
      title: 'Digital Banking Suite',
      industry: 'FINANCIAL SERVICES',
      methodology: 'SCRUM',
      description: 'Deliver a secure, personalised banking experience with account management, payments, and analytics.',
      features: [
        'security',
        'compliance',
        'mobile-first experience'
      ],
      personas: 'Compliance Lead, Branch Manager, Mobile UX Specialist'
    },
    {
      title: 'Composable Commerce',
      industry: 'RETAIL & ECOMMERCE',
      methodology: 'HYBRID',
      description: 'Create a modular e-commerce platform with headless storefronts, inventory orchestration, and loyalty.',
      features: [
        'performance',
        'catalog scalability',
        'personalisation'
      ],
      personas: 'Merchandising Lead, Growth Marketer, Fulfilment Analyst'
    },
    {
      title: 'AI-powered Support Desk',
      industry: 'SAAS / CUSTOMER SUCCESS',
      methodology: 'KANBAN',
      description: 'Roll out an AI-assisted support desk with conversational automation and proactive insights.',
      features: [
        'self-service automation',
        'agent productivity',
        'analytics'
      ],
      personas: 'Support Operations, CX Lead'
    }
  ];

  workflows: Workflow[] = [
    {
      title: 'Scrum Iterations',
      type: 'SCRUM',
      description: 'Two-week sprints with backlog grooming, sprint review, and retro checkpoints.',
      issueTypes: ['Epic', 'Story', 'Task', 'Bug'],
      cadence: '14-day cadence recommended'
    },
    {
      title: 'Kanban Delivery',
      type: 'KANBAN',
      description: 'Continuous flow board with WIP limits to unblock teams quickly.',
      issueTypes: ['Epic', 'Task', 'Bug'],
      cadence: ''
    },
    {
      title: 'Dual-Track Discovery',
      type: 'MIXED',
      description: 'Blends discovery and delivery tracks with weekly checkpoints and outcome tracking.',
      issueTypes: ['Epic', 'Story', 'Task', 'Research', 'Experiment'],
      cadence: '7-day cadence recommended'
    }
  ];

  timezones = ['UTC', 'EST', 'PST', 'CST', 'GMT', 'IST', 'CET'];
  teamSizes = ['Not sure yet', '1-5', '6-10', '11-20', '21-50', '50+'];

  selectTemplate(template: Template) {
    this.selectedTemplate.set(template);
    this.projectData.projectName = template.title;
    this.projectData.projectKey = this.generateProjectKey(template.title);
    this.projectData.industry = template.industry;
    this.projectData.methodology = template.methodology;
    this.projectData.promptSummary = template.description;
    this.nextStep();
  }

  selectWorkflow(workflow: Workflow) {
    this.projectData.selectedWorkflow = workflow;
  }

  generateProjectKey(name: string): string {
    return name
      .split(' ')
      .map(word => word.charAt(0).toUpperCase())
      .join('')
      .substring(0, 3);
  }

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files) {
      const newFiles = Array.from(input.files);
      const remainingSlots = 7 - this.projectData.attachments.length;
      const filesToAdd = newFiles.slice(0, remainingSlots);
      this.projectData.attachments = [...this.projectData.attachments, ...filesToAdd];
      input.value = ''; // Reset input
    }
  }

  removeAttachment(index: number) {
    this.projectData.attachments = this.projectData.attachments.filter((_, i) => i !== index);
  }

  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  }

  generateAIContent(type: 'summary' | 'epics' | 'acceptance' | 'risks') {
    // Set loading state for the specific button
    this.setLoadingState(type, true);

    // Prepare request
    const request = {
      type,
      projectName: this.projectData.projectName,
      industry: this.projectData.industry,
      methodology: this.projectData.methodology,
      promptSummary: this.projectData.promptSummary,
      focusAreas: this.selectedTemplate()?.features.join(', ') || ''
    };

    console.log('Sending request:', request);

    // Call API
    this.apiService.generateContent(request).subscribe({
      next: (response) => {
        console.log('Received response:', response);
        
        if (type === 'summary') {
          this.projectData.executiveSummary = response.content;
          console.log('Set executiveSummary:', this.projectData.executiveSummary);
        } else if (type === 'epics') {
          this.projectData.generatedEpics = response.content;
          console.log('Set generatedEpics:', this.projectData.generatedEpics);
        } else if (type === 'acceptance') {
          this.projectData.acceptanceCriteria = response.content;
          console.log('Set acceptanceCriteria:', this.projectData.acceptanceCriteria);
        } else if (type === 'risks') {
          this.projectData.generatedRisks = response.content;
          console.log('Set generatedRisks:', this.projectData.generatedRisks);
        }
        
        // Trigger change detection after updating data
        this.cdr.detectChanges();
        
        // Clear loading state
        this.setLoadingState(type, false);
      },
      error: (error) => {
        console.error('API Error:', error);
        this.setLoadingState(type, false);
        alert(`Failed to generate content. Error: ${error.message || 'Unknown error'}\n\nPlease check:\n1. Backend is running on http://localhost:8000\n2. Check browser console for details`);
      }
    });
  }

  private setLoadingState(type: string, loading: boolean) {
    switch(type) {
      case 'summary':
        this.loadingSummary.set(loading);
        break;
      case 'epics':
        this.loadingEpics.set(loading);
        break;
      case 'acceptance':
        this.loadingAcceptance.set(loading);
        break;
      case 'risks':
        this.loadingRisks.set(loading);
        break;
    }
  }

  addEpic() {
    if (this.projectData.epicIdeas.length < 2) {
      this.projectData.epicIdeas.push('');
    }
  }

  onEpicKeyPress(event: KeyboardEvent, index: number) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const currentValue = this.projectData.epicIdeas[index]?.trim();
      if (currentValue && this.projectData.epicIdeas.length < 2) {
        this.addEpic();
        // Focus the new input after a short delay
        setTimeout(() => {
          const inputs = document.querySelectorAll('.epic-section .list-item-input');
          const lastInput = inputs[inputs.length - 1] as HTMLInputElement;
          lastInput?.focus();
        }, 0);
      }
    }
  }

  getWordCount(text: string): number {
    return text?.trim().split(/\s+/).filter(word => word.length > 0).length || 0;
  }

  removeEpic(index: number) {
    this.projectData.epicIdeas = this.projectData.epicIdeas.filter((_, i) => i !== index);
  }

  addRisk() {
    if (this.projectData.riskHighlights.length < 2) {
      this.projectData.riskHighlights.push('');
    }
  }

  onRiskKeyPress(event: KeyboardEvent, index: number) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const currentValue = this.projectData.riskHighlights[index]?.trim();
      if (currentValue && this.projectData.riskHighlights.length < 2) {
        this.addRisk();
        // Focus the new input after a short delay
        setTimeout(() => {
          const inputs = document.querySelectorAll('.risk-section .list-item-input');
          const lastInput = inputs[inputs.length - 1] as HTMLInputElement;
          lastInput?.focus();
        }, 0);
      }
    }
  }

  removeRisk(index: number) {
    this.projectData.riskHighlights = this.projectData.riskHighlights.filter((_, i) => i !== index);
  }

  generateFinalPrompt(): string {
    let prompt = '';

    // Project Basic Information
    prompt += `PROJECT INFORMATION\n`;
    prompt += `===================\n\n`;
    prompt += `Project Name: ${this.projectData.projectName}\n`;
    prompt += `Project Key: ${this.projectData.projectKey}\n`;
    prompt += `Industry: ${this.projectData.industry}\n`;
    prompt += `Methodology: ${this.projectData.methodology}\n`;
    prompt += `Team Size: ${this.projectData.teamSize}\n`;
    prompt += `Timezone: ${this.projectData.timezone}\n`;
    if (this.projectData.kickoffDate) {
      prompt += `Kick-off Date: ${this.projectData.kickoffDate}\n`;
    }
    if (this.projectData.targetLaunch) {
      prompt += `Target Launch: ${this.projectData.targetLaunch}\n`;
    }
    prompt += `\n`;

    // Workflow
    if (this.projectData.selectedWorkflow) {
      prompt += `WORKFLOW\n`;
      prompt += `========\n\n`;
      prompt += `Type: ${this.projectData.selectedWorkflow.title}\n`;
      prompt += `Description: ${this.projectData.selectedWorkflow.description}\n`;
      prompt += `Issue Types: ${this.projectData.selectedWorkflow.issueTypes.join(', ')}\n`;
      if (this.projectData.selectedWorkflow.cadence) {
        prompt += `Cadence: ${this.projectData.selectedWorkflow.cadence}\n`;
      }
      prompt += `\n`;
    }

    // Executive Summary
    if (this.projectData.executiveSummary) {
      prompt += `EXECUTIVE SUMMARY\n`;
      prompt += `=================\n\n`;
      prompt += `${this.projectData.executiveSummary}\n\n`;
    }

    // Epic-level Roadmap Ideas (AI Generated)
    if (this.projectData.generatedEpics) {
      prompt += `EPIC-LEVEL ROADMAP IDEAS (AI Generated)\n`;
      prompt += `========================================\n\n`;
      prompt += `${this.projectData.generatedEpics}\n\n`;
    }

    // Manual Epic Ideas
    if (this.projectData.epicIdeas.length > 0) {
      const filteredEpics = this.projectData.epicIdeas.filter(epic => epic.trim());
      if (filteredEpics.length > 0) {
        prompt += `ADDITIONAL EPIC IDEAS (Manual)\n`;
        prompt += `==============================\n\n`;
        filteredEpics.forEach((epic, index) => {
          prompt += `Epic ${index + 1}: ${epic}\n\n`;
        });
      }
    }

    // Acceptance Criteria
    if (this.projectData.acceptanceCriteria) {
      prompt += `ACCEPTANCE CRITERIA\n`;
      prompt += `===================\n\n`;
      prompt += `${this.projectData.acceptanceCriteria}\n\n`;
    }

    // Delivery Risk Register (AI Generated)
    if (this.projectData.generatedRisks) {
      prompt += `DELIVERY RISK REGISTER (AI Generated)\n`;
      prompt += `======================================\n\n`;
      prompt += `${this.projectData.generatedRisks}\n\n`;
    }

    // Manual Risk Highlights
    if (this.projectData.riskHighlights.length > 0) {
      const filteredRisks = this.projectData.riskHighlights.filter(risk => risk.trim());
      if (filteredRisks.length > 0) {
        prompt += `ADDITIONAL RISK HIGHLIGHTS (Manual)\n`;
        prompt += `===================================\n\n`;
        filteredRisks.forEach((risk, index) => {
          prompt += `Risk ${index + 1}: ${risk}\n\n`;
        });
      }
    }

    // Attachments
    if (this.projectData.attachments.length > 0) {
      prompt += `ATTACHMENTS\n`;
      prompt += `===========\n\n`;
      this.projectData.attachments.forEach((file, index) => {
        prompt += `${index + 1}. ${file.name} (${this.formatFileSize(file.size)})\n`;
      });
      prompt += `\n`;
    }

    return prompt;
  }

  showPromptReviewDialog() {
    // Generate the prompt
    this.projectData.finalPrompt = this.generateFinalPrompt();
    
    // Open the dialog
    const dialogRef = this.dialog.open(PromptReviewDialogComponent, {
      data: { prompt: this.projectData.finalPrompt },
      disableClose: true,
      width: '800px',
      maxWidth: '90vw',
      panelClass: 'prompt-review-dialog'
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result && result.proceed) {
        // Update the prompt with any edits
        this.projectData.finalPrompt = result.prompt;
        console.log('Proceeding with prompt:', this.projectData.finalPrompt);
        
        // Now move to step 4 (Features) and generate features
        this.currentStep.set(4);
        this.scrollToTop();
        
        // Generate features automatically
        this.generateFeatures();
      }
      // If cancelled, stay on step 3
    });
  }

  generateFeatures() {
    this.loadingFeatures.set(true);
    this.generatedFeatures.set([]);

    // PROD MODE (Dev Mode OFF): Use mock data to bypass API calls
    if (!this.devModeService.isDevMode()) {
      console.log('[PROD MODE] Using mock features - bypassing API call');
      setTimeout(() => {
        this.generatedFeatures.set([...MOCK_FEATURES]);
        this.loadingFeatures.set(false);
        this.cdr.detectChanges();
      }, 500); // Small delay to simulate loading
      return;
    }

    // Generate first batch of 6 features
    this.apiService.generateFeatures({ prompt: this.projectData.finalPrompt }).subscribe({
      next: (response1) => {
        console.log('First batch of features generated:', response1);
        
        // Generate second batch with context from first batch
        const previousFeaturesSummary = response1.features.map((f, idx) => 
          `${idx + 1}. ${f.title}\n   - ${f.reason}\n   - Focus: ${this.extractFocusAreas(f)}`
        ).join('\n\n');
        
        this.apiService.generateFeatures({ 
          prompt: this.projectData.finalPrompt,
          previousFeatures: previousFeaturesSummary 
        }).subscribe({
          next: (response2) => {
            console.log('Second batch of features generated:', response2);
            const allFeatures = [...response1.features, ...response2.features];
            this.generatedFeatures.set(allFeatures);
            this.loadingFeatures.set(false);
            this.cdr.detectChanges();
          },
          error: (error) => {
            console.error('Features generation error (batch 2):', error);
            // Still show first batch
            this.generatedFeatures.set(response1.features);
            this.loadingFeatures.set(false);
            alert(`Failed to generate all features. Showing first 6 features. Error: ${error.message || 'Unknown error'}`);
          }
        });
      },
      error: (error) => {
        console.error('Features generation error:', error);
        this.loadingFeatures.set(false);
        alert(`Failed to generate features. Error: ${error.message || 'Unknown error'}\n\nPlease check:\n1. Backend is running on http://localhost:8000\n2. Check browser console for details`);
      }
    });
  }

  extractFocusAreas(feature: Feature): string {
    // Extract key focus areas from the feature for the artifact
    const keywords = [];
    if (feature.title.toLowerCase().includes('security') || feature.reason.toLowerCase().includes('security')) {
      keywords.push('Security');
    }
    if (feature.title.toLowerCase().includes('dashboard') || feature.title.toLowerCase().includes('analytics')) {
      keywords.push('Analytics');
    }
    if (feature.title.toLowerCase().includes('user') || feature.title.toLowerCase().includes('customer')) {
      keywords.push('User Experience');
    }
    if (feature.title.toLowerCase().includes('payment') || feature.title.toLowerCase().includes('transaction')) {
      keywords.push('Payments');
    }
    if (feature.title.toLowerCase().includes('compliance') || feature.title.toLowerCase().includes('kyc')) {
      keywords.push('Compliance');
    }
    return keywords.length > 0 ? keywords.join(', ') : 'Core Functionality';
  }

  regenerateFeatures() {
    this.generateFeatures();
  }

  addManualFeature() {
    const newFeatures = this.manualFeatures();
    newFeatures.push('');
    this.manualFeatures.set([...newFeatures]);
  }

  removeManualFeature(index: number) {
    const newFeatures = this.manualFeatures().filter((_, i) => i !== index);
    this.manualFeatures.set(newFeatures);
  }

  onManualFeatureKeyPress(event: KeyboardEvent, index: number) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const currentValue = this.manualFeatures()[index]?.trim();
      if (currentValue) {
        this.addManualFeature();
        // Focus the new input after a short delay
        setTimeout(() => {
          const inputs = document.querySelectorAll('.manual-feature-input');
          const lastInput = inputs[inputs.length - 1] as HTMLInputElement;
          lastInput?.focus();
        }, 0);
      }
    }
  }

  approveFeature(index: number) {
    const features = this.generatedFeatures();
    features[index].approved = true;
    this.generatedFeatures.set([...features]);
    this.checkAllApproved();
  }

  toggleApproveFeature(index: number) {
    const features = this.generatedFeatures();
    features[index].approved = !features[index].approved;
    this.generatedFeatures.set([...features]);
    this.checkAllApproved();
  }

  onApproveClick(event: Event, index: number) {
    event.stopPropagation();
    event.preventDefault();
    this.toggleApproveFeature(index);
  }

  approveAllFeatures() {
    const features = this.generatedFeatures().map(f => ({ ...f, approved: true }));
    this.generatedFeatures.set(features);
    this.allFeaturesApproved.set(true);
  }

  checkAllApproved() {
    const allApproved = this.generatedFeatures().every(f => f.approved);
    this.allFeaturesApproved.set(allApproved);
  }

  generateStories() {
    // Collect ONLY APPROVED features (AI generated + manual)
    const approvedAIFeatures = this.generatedFeatures()
      .filter(f => f.approved)
      .map(f => f.title);
    
    const manualFeaturesFiltered = this.manualFeatures().filter(f => f.trim());
    
    const allApprovedFeatures = [
      ...approvedAIFeatures,
      ...manualFeaturesFiltered
    ];

    if (allApprovedFeatures.length === 0) {
      alert('Please approve at least one feature before creating stories.');
      return;
    }

    // PROD MODE (Dev Mode OFF): Use mock data to bypass API calls
    if (!this.devModeService.isDevMode()) {
      console.log('[PROD MODE] Using mock stories - bypassing API call');
      this.loadingStories.set(true);
      this.generatedStories.set([]);
      setTimeout(() => {
        this.generatedStories.set([...MOCK_STORIES]);
        this.loadingStories.set(false);
        this.cdr.detectChanges();
      }, 500); // Small delay to simulate loading
      return;
    }

    // Build project context from form data
    const projectContext = `Project: ${this.projectData.projectName}
Industry: ${this.projectData.industry}
Methodology: ${this.projectData.methodology}
Description: ${this.projectData.promptSummary}
Focus Areas: ${this.projectData.executiveSummary || 'N/A'}`;

    this.loadingStories.set(true);
    this.generatedStories.set([]);

    // Split features into batches of 6
    const batch1 = allApprovedFeatures.slice(0, 6);
    const batch2 = allApprovedFeatures.slice(6, 12);

    // Generate stories for first batch
    this.apiService.generateStories({ features: batch1, projectContext }).subscribe({
      next: (response1) => {
        // If there's a second batch, generate for it too
        if (batch2.length > 0) {
          // Create detailed summary of first batch stories to prevent duplicates
          const previousStoriesSummary = response1.stories.map((s, idx) => 
            `${idx + 1}. [${s.featureRef}] ${s.title}\n   Description: ${s.description.substring(0, 150)}...`
          ).join('\n\n');
          
          this.apiService.generateStories({ 
            features: batch2, 
            projectContext,
            previousStories: previousStoriesSummary 
          }).subscribe({
            next: (response2) => {
              const allStories = [...response1.stories, ...response2.stories];
              this.generatedStories.set(allStories);
              this.loadingStories.set(false);
              this.cdr.detectChanges();
            },
            error: (error) => {
              console.error('Stories generation error (batch 2):', error);
              // Still show first batch
              this.generatedStories.set(response1.stories);
              this.loadingStories.set(false);
              alert(`Failed to generate all stories. Error: ${error.message || 'Unknown error'}`);
            }
          });
        } else {
          this.generatedStories.set(response1.stories);
          this.loadingStories.set(false);
          this.cdr.detectChanges();
        }
      },
      error: (error) => {
        console.error('Stories generation error:', error);
        this.loadingStories.set(false);
        alert(`Failed to generate stories. Error: ${error.message || 'Unknown error'}\n\nPlease check:\n1. Backend is running on http://localhost:8000\n2. Check browser console for details`);
      }
    });
  }

  regenerateStories() {
    this.generateStories();
  }

  addManualStory() {
    const newStories = this.manualStories();
    newStories.push('');
    this.manualStories.set([...newStories]);
  }

  removeManualStory(index: number) {
    const newStories = this.manualStories().filter((_, i) => i !== index);
    this.manualStories.set(newStories);
  }

  onManualStoryKeyPress(event: KeyboardEvent, index: number) {
    if (event.key === 'Enter') {
      event.preventDefault();
      const currentValue = this.manualStories()[index]?.trim();
      if (currentValue) {
        this.addManualStory();
        setTimeout(() => {
          const inputs = document.querySelectorAll('.manual-story-input');
          const lastInput = inputs[inputs.length - 1] as HTMLInputElement;
          lastInput?.focus();
        }, 0);
      }
    }
  }

  approveStory(index: number) {
    const stories = this.generatedStories();
    stories[index].approved = !stories[index].approved;
    this.generatedStories.set([...stories]);
    this.checkAllStoriesApproved();
  }

  approveAllStories() {
    const stories = this.generatedStories().map(story => ({
      ...story,
      approved: true
    }));
    this.generatedStories.set(stories);
    this.checkAllStoriesApproved();
  }

  checkAllStoriesApproved() {
    const allApproved = this.generatedStories().every(s => s.approved);
    this.allStoriesApproved.set(allApproved);
  }

  openFeatureDetail(feature: Feature, index: number) {
    const dialogRef = this.dialog.open(FeatureDetailModalComponent, {
      data: feature,
      width: '900px',
      maxWidth: '95vw',
      maxHeight: '90vh',
      panelClass: 'feature-detail-dialog'
    });

    dialogRef.afterClosed().subscribe((updatedFeature: Feature | undefined) => {
      if (updatedFeature) {
        // Update the feature in the array
        const features = this.generatedFeatures();
        features[index] = updatedFeature;
        this.generatedFeatures.set([...features]);
      }
    });
  }

  nextStep() {
    if (this.currentStep() < 5) {
      // Show prompt review dialog when moving from step 3
      if (this.currentStep() === 3) {
        this.showPromptReviewDialog();
        return;
      }
      
      // Validate at least one feature is approved when moving from step 4 to 5
      if (this.currentStep() === 4) {
        const approvedFeatures = this.generatedFeatures().filter(f => f.approved);
        const hasManualFeatures = this.manualFeatures().length > 0;
        
        if (approvedFeatures.length === 0 && !hasManualFeatures) {
          alert('Please approve at least one feature or add a manual feature before proceeding.');
          return;
        }
        
        this.currentStep.set(5);
        this.scrollToTop();
        // Only generate if we don't have stories yet
        if (this.generatedStories().length === 0 && this.manualStories().length === 0) {
          this.generateStories();
        }
        return;
      }
      
      this.currentStep.set(this.currentStep() + 1);
      this.scrollToTop();
    }
  }

  finishProject() {
    // Validate at least one story is approved
    const approvedStories = this.generatedStories().filter(s => s.approved);
    const hasManualStories = this.manualStories().filter(s => s.trim()).length > 0;
    
    if (approvedStories.length === 0 && !hasManualStories) {
      alert('Please approve at least one story or add a manual story before creating the project.');
      return;
    }
    
    // Generate final prompt for review
    this.projectData.finalPrompt = this.generateFinalPrompt();
    
    // Create the result object to pass back
    const projectResult = {
      projectName: this.projectData.projectName,
      projectKey: this.projectData.projectKey,
      industry: this.projectData.industry,
      methodology: this.projectData.methodology,
      teamSize: this.projectData.teamSize,
      executiveSummary: this.projectData.executiveSummary,
      promptSummary: this.projectData.promptSummary,
      finalPrompt: this.projectData.finalPrompt,
      features: this.generatedFeatures().filter(f => f.approved),
      stories: approvedStories,
      epicIdeas: this.projectData.epicIdeas.filter(e => e.trim()),
      riskHighlights: this.projectData.riskHighlights.filter(r => r.trim()),
      generatedRisks: this.projectData.generatedRisks
    };
    
    console.log('Creating project with data:', projectResult);
    
    // Close dialog and return the project data
    this.dialogRef.close(projectResult);
  }

  previousStep() {
    if (this.currentStep() > 1) {
      this.currentStep.set(this.currentStep() - 1);
      this.scrollToTop();
    }
  }

  private scrollToTop() {
    setTimeout(() => {
      const modalContent = document.querySelector('.modal-content');
      if (modalContent) {
        modalContent.scrollTop = 0;
      }
    }, 0);
  }
}
