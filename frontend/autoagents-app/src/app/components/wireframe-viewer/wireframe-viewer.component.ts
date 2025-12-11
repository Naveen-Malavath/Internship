import { 
  Component, 
  Input, 
  Output, 
  EventEmitter, 
  signal, 
  computed,
  ElementRef,
  ViewChild,
  AfterViewInit,
  OnChanges,
  OnInit,
  SimpleChanges,
  SecurityContext,
  OnDestroy
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { DomSanitizer, SafeHtml, SafeResourceUrl } from '@angular/platform-browser';
import { trigger, state, style, animate, transition } from '@angular/animations';

export interface WireframePage {
  id: string;
  name: string;
  type: string;
  html: string;
  description?: string;
  error?: string;
}

export interface WireframeData {
  pages: WireframePage[];
  shared_components: {
    sidebar?: string;
    header?: string;
    page_wrapper?: string;
  };
  plan: {
    pages?: any[];
    navigation?: any;
    theme?: any;
  };
  metadata: {
    total_pages: number;
    generation_time?: number;
  };
}

type ViewportSize = 'mobile' | 'tablet' | 'desktop';

@Component({
  selector: 'app-wireframe-viewer',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatIconModule,
    MatTooltipModule,
    MatButtonModule,
    MatSlideToggleModule,
    MatSelectModule,
    MatFormFieldModule
  ],
  templateUrl: './wireframe-viewer.component.html',
  styleUrls: ['./wireframe-viewer.component.scss'],
  animations: [
    trigger('slideIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateX(-10px)', width: 0 }),
        animate('300ms ease-out', style({ opacity: 1, transform: 'translateX(0)', width: '*' }))
      ]),
      transition(':leave', [
        animate('250ms ease-in', style({ opacity: 0, transform: 'translateX(-10px)', width: 0 }))
      ])
    ])
  ]
})
export class WireframeViewerComponent implements AfterViewInit, OnChanges, OnInit, OnDestroy {
  @ViewChild('previewIframe') previewIframe!: ElementRef<HTMLIFrameElement>;
  @ViewChild('codeEditor') codeEditor!: ElementRef<HTMLTextAreaElement>;
  
  @Input() wireframeData: WireframeData | null = null;
  @Input() isGenerating = false;
  @Input() generationProgress = '';
  
  // Page count settings from parent
  @Input() pageMode: 'auto' | 'manual' = 'auto';
  @Input() pageCount: number = 5;
  @Input() pageCountOptions: number[] = [2, 3, 4, 5, 6, 8, 10, 12];
  
  @Output() regeneratePage = new EventEmitter<WireframePage>();
  @Output() regenerateAll = new EventEmitter<void>();
  @Output() pageModeChange = new EventEmitter<'auto' | 'manual'>();
  @Output() pageCountChange = new EventEmitter<number>();
  
  // Signals for reactive state
  selectedPageId = signal<string>('');
  viewportSize = signal<ViewportSize>('desktop');
  isCodeEditorVisible = signal<boolean>(false);
  isFullscreen = signal<boolean>(false);
  
  // Live progress tracking
  completedPages: string[] = [];
  currentPage: string = '';
  editedHtml = signal<string>('');
  hasUnsavedChanges = signal<boolean>(false);
  
  // Track blob URLs for cleanup
  private currentBlobUrl: string | null = null;
  
  // Signal wrapper for wireframeData to make computed properties reactive
  private wireframeDataSignal = signal<WireframeData | null>(null);
  
  // Computed values - now reactive to wireframeDataSignal
  selectedPage = computed(() => {
    const data = this.wireframeDataSignal();
    if (!data?.pages) return null;
    return data.pages.find(p => p.id === this.selectedPageId()) || data.pages[0];
  });
  
  // Safe iframe source - sanitized for security
  iframeSrc = signal<SafeResourceUrl | null>(null);
  
  viewportWidth = computed(() => {
    switch (this.viewportSize()) {
      case 'mobile': return '375px';
      case 'tablet': return '768px';
      case 'desktop': return '100%';
    }
  });
  
  viewportLabel = computed(() => {
    switch (this.viewportSize()) {
      case 'mobile': return '375px (Mobile)';
      case 'tablet': return '768px (Tablet)';
      case 'desktop': return '100% (Desktop)';
    }
  });
  
  constructor(private sanitizer: DomSanitizer) {}
  
  ngOnDestroy() {
    // Cleanup blob URLs
    if (this.currentBlobUrl) {
      URL.revokeObjectURL(this.currentBlobUrl);
    }
  }
  
  private updateIframeSrc() {
    // Cleanup previous blob URL
    if (this.currentBlobUrl) {
      URL.revokeObjectURL(this.currentBlobUrl);
      this.currentBlobUrl = null;
    }
    
    const html = this.editedHtml() || this.selectedPage()?.html || '';
    console.log('[WireframeViewer] updateIframeSrc - HTML length:', html.length);
    
    if (!html) {
      const placeholder = `<!DOCTYPE html>
<html>
<head><style>
  body { 
    font-family: system-ui, sans-serif; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    height: 100vh; 
    margin: 0; 
    background: #f5f5f5; 
    color: #666; 
  }
</style></head>
<body><div style="text-align:center"><h2>No Preview</h2><p>Select a page to preview</p></div></body>
</html>`;
      const blob = new Blob([placeholder], { type: 'text/html' });
      this.currentBlobUrl = URL.createObjectURL(blob);
      this.iframeSrc.set(this.sanitizer.bypassSecurityTrustResourceUrl(this.currentBlobUrl));
      return;
    }
    
    // Log first 500 chars of HTML for debugging
    console.log('[WireframeViewer] HTML preview:', html.substring(0, 500));
    
    const blob = new Blob([html], { type: 'text/html' });
    this.currentBlobUrl = URL.createObjectURL(blob);
    console.log('[WireframeViewer] Created blob URL:', this.currentBlobUrl);
    this.iframeSrc.set(this.sanitizer.bypassSecurityTrustResourceUrl(this.currentBlobUrl));
  }
  
  ngOnInit() {
    console.log('[WireframeViewer] ngOnInit called, wireframeData:', this.wireframeData);
    // Handle initial data that may be passed before ngOnChanges
    if (this.wireframeData?.pages?.length) {
      this.wireframeDataSignal.set(this.wireframeData);
      this.selectedPageId.set(this.wireframeData.pages[0].id);
      this.editedHtml.set(this.wireframeData.pages[0].html);
      this.updateIframeSrc();
    }
  }
  
  ngAfterViewInit() {
    // Update iframe after view is ready
    this.updateIframeSrc();
  }
  
  ngOnChanges(changes: SimpleChanges) {
    console.log('[WireframeViewer] ngOnChanges triggered', changes);
    
    // Debug isGenerating changes
    if (changes['isGenerating']) {
      console.log('[WireframeViewer] isGenerating changed to:', this.isGenerating);
    }
    
    if (changes['generationProgress']) {
      console.log('[WireframeViewer] generationProgress changed to:', this.generationProgress);
    }
    
    if (changes['wireframeData']) {
      const newData = changes['wireframeData'].currentValue;
      console.log('[WireframeViewer] wireframeData changed:', newData);
      
      // Update the signal to trigger computed properties
      this.wireframeDataSignal.set(newData);
      
      if (newData?.pages?.length) {
        // Select first page if none selected
        if (!this.selectedPageId() || !newData.pages.find((p: WireframePage) => p.id === this.selectedPageId())) {
          console.log('[WireframeViewer] Selecting first page:', newData.pages[0].id);
          this.selectedPageId.set(newData.pages[0].id);
        }
        
        // Set the HTML content for the selected page
        const page = newData.pages.find((p: WireframePage) => p.id === this.selectedPageId()) || newData.pages[0];
        console.log('[WireframeViewer] Setting HTML for page:', page?.name, 'HTML length:', page?.html?.length);
        this.editedHtml.set(page?.html || '');
        this.hasUnsavedChanges.set(false);
        
        // Update the iframe source
        this.updateIframeSrc();
      }
    }
  }
  
  selectPage(pageId: string) {
    if (this.hasUnsavedChanges()) {
      // Optionally prompt user about unsaved changes
    }
    this.selectedPageId.set(pageId);
    // Get the page from the signal
    const data = this.wireframeDataSignal();
    const page = data?.pages?.find(p => p.id === pageId);
    this.editedHtml.set(page?.html || '');
    this.hasUnsavedChanges.set(false);
    this.updateIframeSrc();
  }
  
  setViewport(size: ViewportSize) {
    this.viewportSize.set(size);
  }
  
  toggleCodeEditor() {
    this.isCodeEditorVisible.set(!this.isCodeEditorVisible());
  }
  
  toggleFullscreen() {
    this.isFullscreen.set(!this.isFullscreen());
    if (this.isFullscreen()) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
  }
  
  onCodeChange(event: Event) {
    const target = event.target as HTMLTextAreaElement;
    this.editedHtml.set(target.value);
    this.hasUnsavedChanges.set(target.value !== this.selectedPage()?.html);
    this.updateIframeSrc();
  }
  
  updatePreview() {
    console.log('[WireframeViewer] updatePreview called');
    const html = this.editedHtml() || this.selectedPage()?.html || '';
    console.log('[WireframeViewer] HTML content length:', html.length);
    
    if (html && !this.editedHtml()) {
      this.editedHtml.set(html);
    }
    this.updateIframeSrc();
  }
  
  saveChanges() {
    const page = this.selectedPage();
    if (page) {
      page.html = this.editedHtml();
      this.hasUnsavedChanges.set(false);
    }
  }
  
  revertChanges() {
    this.editedHtml.set(this.selectedPage()?.html || '');
    this.hasUnsavedChanges.set(false);
    this.updateIframeSrc();
  }
  
  copyHtml() {
    const html = this.editedHtml() || this.selectedPage()?.html || '';
    navigator.clipboard.writeText(html);
  }
  
  downloadHtml() {
    const page = this.selectedPage();
    if (!page) return;
    
    const html = this.editedHtml() || page.html;
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${page.id}-wireframe.html`;
    a.click();
    URL.revokeObjectURL(url);
  }
  
  downloadAllPages() {
    if (!this.wireframeData?.pages) return;
    
    // Create a zip-like structure as separate downloads
    this.wireframeData.pages.forEach((page, index) => {
      setTimeout(() => {
        const blob = new Blob([page.html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${page.id}-wireframe.html`;
        a.click();
        URL.revokeObjectURL(url);
      }, index * 500);
    });
  }
  
  openInNewTab() {
    const html = this.editedHtml() || this.selectedPage()?.html || '';
    const blob = new Blob([html], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    window.open(url, '_blank');
  }
  
  onRegeneratePage() {
    const page = this.selectedPage();
    if (page) {
      this.regeneratePage.emit(page);
    }
  }
  
  onRegenerateAll() {
    this.regenerateAll.emit();
  }
  
  onPageModeChange(mode: 'auto' | 'manual') {
    console.log('[WireframeViewer] Page mode changed to:', mode);
    this.pageModeChange.emit(mode);
  }
  
  onPageCountChange(count: number) {
    console.log('[WireframeViewer] Page count changed to:', count);
    this.pageCountChange.emit(count);
  }
  
  getPageIcon(type: string): string {
    const icons: Record<string, string> = {
      'dashboard': 'dashboard',
      'list': 'view_list',
      'detail': 'article',
      'form': 'edit_note',
      'settings': 'settings',
      'auth': 'lock',
      'generic': 'web'
    };
    return icons[type] || 'web';
  }
  
  getPageTypeColor(type: string): string {
    const colors: Record<string, string> = {
      'dashboard': '#3b82f6',
      'list': '#10b981',
      'detail': '#8b5cf6',
      'form': '#f59e0b',
      'settings': '#6b7280',
      'auth': '#ef4444',
      'generic': '#64748b'
    };
    return colors[type] || '#64748b';
  }
  
  // Clean progress text - remove attempt counters
  getCleanProgress(): string {
    if (!this.generationProgress) {
      return 'Creating professional UI designs for your project...';
    }
    // Remove attempt counter text
    return this.generationProgress
      .replace(/\s*\(Attempt \d+\/\d+\)/g, '')
      .replace(/\s*Attempt \d+\/\d+/g, '')
      .trim() || 'Creating professional UI designs for your project...';
  }
  
  // Update page progress - called from parent component
  updatePageProgress(completed: string[], current: string) {
    this.completedPages = completed;
    this.currentPage = current;
  }
  
  // Reset progress when generation starts
  resetProgress() {
    this.completedPages = [];
    this.currentPage = '';
  }
  
  getLineNumbers(): number[] {
    const html = this.editedHtml() || '';
    const lines = html.split('\n').length;
    return Array.from({ length: lines }, (_, i) => i + 1);
  }
}
