import { Component, inject, signal, OnInit, OnDestroy, HostListener } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatRippleModule } from '@angular/material/core';
import { NavigationService, NavItem } from '../../services/navigation.service';

@Component({
  selector: 'app-sidebar-nav',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatIconModule,
    MatTooltipModule,
    MatRippleModule
  ],
  templateUrl: './sidebar-nav.component.html',
  styleUrls: ['./sidebar-nav.component.scss']
})
export class SidebarNavComponent implements OnInit, OnDestroy {
  navService = inject(NavigationService);
  
  // Local component state
  hoveredItem = signal<string | null>(null);
  expandedItems = signal<Set<string>>(new Set());
  isMobile = signal<boolean>(false);
  
  // Keyboard navigation
  focusedIndex = signal<number>(-1);
  
  private resizeObserver: ResizeObserver | null = null;

  ngOnInit(): void {
    console.log('[SidebarNav] Component initializing...');
    console.log('[SidebarNav] Nav items:', this.navService.navItems());
    console.log('[SidebarNav] Initial collapsed state:', this.navService.isCollapsed());
    
    this.checkScreenSize();
    this.setupResizeObserver();
  }

  ngOnDestroy(): void {
    console.log('[SidebarNav] Component destroying...');
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }
  }

  @HostListener('window:resize')
  onWindowResize(): void {
    this.checkScreenSize();
  }

  @HostListener('window:keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    // Only handle keyboard navigation when sidebar is focused
    if (!document.querySelector('.sidebar-nav:focus-within')) {
      return;
    }

    const items = this.navService.navItems();
    const currentIndex = this.focusedIndex();

    switch (event.key) {
      case 'ArrowDown':
        event.preventDefault();
        this.focusedIndex.set(Math.min(currentIndex + 1, items.length - 1));
        console.log('[SidebarNav] Arrow down - focused index:', this.focusedIndex());
        break;
      case 'ArrowUp':
        event.preventDefault();
        this.focusedIndex.set(Math.max(currentIndex - 1, 0));
        console.log('[SidebarNav] Arrow up - focused index:', this.focusedIndex());
        break;
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (currentIndex >= 0 && currentIndex < items.length) {
          this.onNavItemClick(items[currentIndex]);
        }
        break;
      case 'Escape':
        if (this.navService.isMobileMenuOpen()) {
          this.navService.closeMobileMenu();
        }
        break;
    }
  }

  private checkScreenSize(): void {
    const wasMobile = this.isMobile();
    const isNowMobile = window.innerWidth < 768;
    
    this.isMobile.set(isNowMobile);
    
    if (wasMobile !== isNowMobile) {
      console.log('[SidebarNav] Screen size changed - mobile:', isNowMobile);
      
      // Auto-collapse on mobile
      if (isNowMobile && !this.navService.isCollapsed()) {
        console.log('[SidebarNav] Auto-collapsing for mobile view');
        this.navService.setCollapsed(true);
      }
    }
  }

  private setupResizeObserver(): void {
    if (typeof ResizeObserver !== 'undefined') {
      this.resizeObserver = new ResizeObserver(() => {
        this.checkScreenSize();
      });
      this.resizeObserver.observe(document.body);
    }
  }

  onNavItemClick(item: NavItem): void {
    console.log('[SidebarNav] Nav item clicked:', item.id, item.route);
    
    // Edge case: Disabled item
    if (item.disabled) {
      console.log('[SidebarNav] Item is disabled, ignoring click');
      return;
    }
    
    // Edge case: Item has children - toggle expansion
    if (item.children && item.children.length > 0) {
      console.log('[SidebarNav] Item has children, toggling expansion');
      this.toggleExpanded(item.id);
      return;
    }
    
    // Navigate
    this.navService.navigate(item.route);
  }

  onNavItemHover(itemId: string | null): void {
    this.hoveredItem.set(itemId);
    if (itemId) {
      console.log('[SidebarNav] Hovering over:', itemId);
    }
  }

  toggleExpanded(itemId: string): void {
    const expanded = new Set(this.expandedItems());
    if (expanded.has(itemId)) {
      expanded.delete(itemId);
      console.log('[SidebarNav] Collapsing item:', itemId);
    } else {
      expanded.add(itemId);
      console.log('[SidebarNav] Expanding item:', itemId);
    }
    this.expandedItems.set(expanded);
  }

  isExpanded(itemId: string): boolean {
    return this.expandedItems().has(itemId);
  }

  onToggleCollapse(): void {
    console.log('[SidebarNav] Toggle collapse button clicked');
    this.navService.toggleCollapse();
  }

  onMobileMenuToggle(): void {
    console.log('[SidebarNav] Mobile menu toggle clicked');
    this.navService.toggleMobileMenu();
  }

  onOverlayClick(): void {
    console.log('[SidebarNav] Overlay clicked, closing mobile menu');
    this.navService.closeMobileMenu();
  }

  getTooltip(item: NavItem): string {
    if (this.navService.isCollapsed()) {
      return item.label;
    }
    return '';
  }

  trackByNavItem(index: number, item: NavItem): string {
    return item.id;
  }
}
