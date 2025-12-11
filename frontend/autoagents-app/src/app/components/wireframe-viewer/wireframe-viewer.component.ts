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
  // Angular component code
  component_ts?: string;
  component_html?: string;
  component_scss?: string;
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
type CodeViewMode = 'preview' | 'typescript' | 'html' | 'scss';

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
  
  // Code view mode - which type of code to display
  codeViewMode = signal<CodeViewMode>('preview');
  
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
  
  // The actual render width for the iframe content (always render at desktop size, then scale)
  // The actual render width for the iframe content
  // For desktop: use 100% (original behavior)
  // For mobile/tablet: use fixed 1200px width then scale down
  iframeRenderWidth = computed(() => {
    switch (this.viewportSize()) {
      case 'mobile': return '1200px';
      case 'tablet': return '1200px';
      case 'desktop': return '100%'; // Original desktop behavior - no fixed width
    }
  });
  
  // Calculate scale factor for mobile/tablet to fit content
  // Desktop uses scale 1 with 100% width (no scaling needed)
  viewportScale = computed(() => {
    switch (this.viewportSize()) {
      case 'mobile': return 375 / 1200; // ~0.3125
      case 'tablet': return 768 / 1200; // ~0.64
      case 'desktop': return 1;
    }
  });
  
  // Calculate the height the iframe needs to be to fill the visible area after scaling
  // For desktop: use 100% height (original behavior)
  // For mobile/tablet: calculate inverse height based on scale
  iframeScaledHeight = computed(() => {
    if (this.viewportSize() === 'desktop') {
      return '100%'; // Original desktop behavior
    }
    const scale = this.viewportScale();
    // When scaled down, we need to increase the height inversely
    // For example, at 0.3125 scale, height needs to be 1/0.3125 = 3.2x to fill 500px visible area
    const baseHeight = 500; // matches the wrapper height
    return `${Math.ceil(baseHeight / scale)}px`;
  });
  
  // Calculate fullscreen scaled height
  // For desktop: use 100% height (original behavior)
  // For mobile/tablet: calculate inverse height based on scale
  fullscreenScaledHeight = computed(() => {
    if (this.viewportSize() === 'desktop') {
      return '100%'; // Original desktop behavior
    }
    const scale = this.viewportScale();
    // Fullscreen height is viewport height minus header (140px)
    // We estimate based on a typical height
    const baseHeight = 800; // Approximate fullscreen visible area
    return `${Math.ceil(baseHeight / scale)}px`;
  });
  
  viewportLabel = computed(() => {
    switch (this.viewportSize()) {
      case 'mobile': return '375px (Mobile)';
      case 'tablet': return '768px (Tablet)';
      case 'desktop': return '100% (Desktop)';
    }
  });
  
  // Get current code content based on view mode
  currentCodeContent = computed(() => {
    const page = this.selectedPage();
    if (!page) return '';
    
    switch (this.codeViewMode()) {
      case 'preview': return this.editedHtml() || page.html || '';
      case 'typescript': return page.component_ts || '// No TypeScript code generated yet';
      case 'html': return page.component_html || '<!-- No HTML template generated yet -->';
      case 'scss': return page.component_scss || '/* No SCSS styles generated yet */';
    }
  });
  
  // Get file extension for current code view
  currentFileExtension = computed(() => {
    switch (this.codeViewMode()) {
      case 'preview': return 'html';
      case 'typescript': return 'ts';
      case 'html': return 'html';
      case 'scss': return 'scss';
    }
  });
  
  // Get file name for current code view
  currentFileName = computed(() => {
    const page = this.selectedPage();
    if (!page) return 'code';
    
    const baseName = this.toKebabCase(page.name);
    switch (this.codeViewMode()) {
      case 'preview': return `${page.id}-wireframe.html`;
      case 'typescript': return `${baseName}.component.ts`;
      case 'html': return `${baseName}.component.html`;
      case 'scss': return `${baseName}.component.scss`;
    }
  });
  
  // Check if component code is available
  hasComponentCode = computed(() => {
    const page = this.selectedPage();
    return !!(page?.component_ts || page?.component_html || page?.component_scss);
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
    
    // Inject responsive CSS and viewport meta to make content adapt to viewport size
    const responsiveHtml = this.injectResponsiveStyles(html);
    
    const blob = new Blob([responsiveHtml], { type: 'text/html' });
    this.currentBlobUrl = URL.createObjectURL(blob);
    console.log('[WireframeViewer] Created blob URL:', this.currentBlobUrl);
    this.iframeSrc.set(this.sanitizer.bypassSecurityTrustResourceUrl(this.currentBlobUrl));
  }
  
  /**
   * Injects base CSS into the HTML content to ensure proper rendering.
   * Since we now use CSS transform scaling for mobile/tablet viewports,
   * we render content at full desktop width and scale it down visually.
   */
  private injectResponsiveStyles(html: string): string {
    // Base CSS to inject - ensures proper rendering at full width
    const baseCSS = `
    <style data-wireframe-base="true">
      /* Base styles for consistent rendering */
      *, *::before, *::after {
        box-sizing: border-box;
      }
      
      html, body {
        margin: 0;
        padding: 0;
        min-height: 100%;
        background: white;
      }
      
      /* Ensure body fills the iframe */
      body {
        min-width: 100%;
      }
      
      /* Make images scale properly within their containers */
      img {
        max-width: 100%;
        height: auto;
      }
      
      /* Ensure tables display properly */
      table {
        border-collapse: collapse;
      }
    </style>
    `;
    
    // Viewport meta tag - set to render at desktop width
    const viewportMeta = '<meta name="viewport" content="width=1200, initial-scale=1.0">';
    
    // Check if HTML already has viewport meta
    const hasViewportMeta = /<meta[^>]*name=["']viewport["'][^>]*>/i.test(html);
    
    // Check if HTML has head tag
    const hasHeadTag = /<head[^>]*>/i.test(html);
    const hasHtmlTag = /<html[^>]*>/i.test(html);
    
    let modifiedHtml = html;
    
    if (hasHeadTag) {
      // Inject after opening head tag
      modifiedHtml = modifiedHtml.replace(
        /(<head[^>]*>)/i, 
        `$1\n${!hasViewportMeta ? viewportMeta : ''}\n${baseCSS}`
      );
    } else if (hasHtmlTag) {
      // Create head tag and inject
      modifiedHtml = modifiedHtml.replace(
        /(<html[^>]*>)/i,
        `$1\n<head>\n${viewportMeta}\n${baseCSS}\n</head>`
      );
    } else {
      // No html/head structure, wrap everything
      modifiedHtml = `<!DOCTYPE html>
<html>
<head>
${viewportMeta}
${baseCSS}
</head>
<body>
${html}
</body>
</html>`;
    }
    
    return modifiedHtml;
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
    // Reset to preview mode when opening code editor
    if (this.isCodeEditorVisible()) {
      this.codeViewMode.set('preview');
    }
  }
  
  // Set code view mode
  setCodeViewMode(mode: CodeViewMode) {
    this.codeViewMode.set(mode);
  }
  
  // Helper to convert string to kebab-case
  private toKebabCase(str: string): string {
    return str
      .replace(/([a-z])([A-Z])/g, '$1-$2')
      .replace(/[\s_]+/g, '-')
      .toLowerCase();
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
    const content = this.currentCodeContent();
    navigator.clipboard.writeText(content);
  }
  
  // Copy current code content (alias for copyHtml for clarity)
  copyCurrentCode() {
    this.copyHtml();
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
  
  // Download current code view (respects codeViewMode)
  downloadCurrentCode() {
    const content = this.currentCodeContent();
    const fileName = this.currentFileName();
    const mimeType = this.codeViewMode() === 'scss' ? 'text/x-scss' : 
                     this.codeViewMode() === 'typescript' ? 'text/typescript' : 'text/html';
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = fileName;
    a.click();
    URL.revokeObjectURL(url);
  }
  
  // Download all component files for current page
  downloadComponentFiles() {
    const page = this.selectedPage();
    if (!page) return;
    
    const baseName = this.toKebabCase(page.name);
    const files = [
      { content: page.component_ts || '', name: `${baseName}.component.ts`, type: 'text/typescript' },
      { content: page.component_html || '', name: `${baseName}.component.html`, type: 'text/html' },
      { content: page.component_scss || '', name: `${baseName}.component.scss`, type: 'text/x-scss' }
    ];
    
    files.forEach((file, index) => {
      if (file.content) {
        setTimeout(() => {
          const blob = new Blob([file.content], { type: file.type });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = file.name;
          a.click();
          URL.revokeObjectURL(url);
        }, index * 300);
      }
    });
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
  
  // Download all pages with their component code
  downloadAllWithComponents() {
    if (!this.wireframeData?.pages) return;
    
    let downloadIndex = 0;
    this.wireframeData.pages.forEach((page) => {
      const baseName = this.toKebabCase(page.name);
      
      // Download wireframe HTML
      setTimeout(() => {
        const blob = new Blob([page.html], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${page.id}-wireframe.html`;
        a.click();
        URL.revokeObjectURL(url);
      }, downloadIndex++ * 300);
      
      // Download component files if available
      if (page.component_ts) {
        setTimeout(() => {
          const blob = new Blob([page.component_ts!], { type: 'text/typescript' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${baseName}.component.ts`;
          a.click();
          URL.revokeObjectURL(url);
        }, downloadIndex++ * 300);
      }
      
      if (page.component_html) {
        setTimeout(() => {
          const blob = new Blob([page.component_html!], { type: 'text/html' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${baseName}.component.html`;
          a.click();
          URL.revokeObjectURL(url);
        }, downloadIndex++ * 300);
      }
      
      if (page.component_scss) {
        setTimeout(() => {
          const blob = new Blob([page.component_scss!], { type: 'text/x-scss' });
          const url = URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = `${baseName}.component.scss`;
          a.click();
          URL.revokeObjectURL(url);
        }, downloadIndex++ * 300);
      }
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
    const content = this.currentCodeContent();
    const lines = content.split('\n').length;
    return Array.from({ length: lines }, (_, i) => i + 1);
  }
  
  // Get syntax highlighting language indicator
  getCodeLanguage(): string {
    switch (this.codeViewMode()) {
      case 'preview': return 'HTML';
      case 'typescript': return 'TypeScript';
      case 'html': return 'HTML Template';
      case 'scss': return 'SCSS';
    }
  }
}
