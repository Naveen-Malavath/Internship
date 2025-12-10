import { Injectable, signal, computed, inject } from '@angular/core';
import { Router, NavigationEnd, Event } from '@angular/router';
import { filter } from 'rxjs/operators';

export interface NavItem {
  id: string;
  label: string;
  icon: string;
  route: string;
  badge?: number;
  disabled?: boolean;
  children?: NavItem[];
}

export interface BreadcrumbItem {
  label: string;
  route?: string;
}

@Injectable({
  providedIn: 'root'
})
export class NavigationService {
  private router = inject(Router);

  // Navigation state signals
  private _isCollapsed = signal<boolean>(false);
  private _isMobileMenuOpen = signal<boolean>(false);
  private _activeRoute = signal<string>('/');
  private _navigationHistory = signal<string[]>([]);
  private _isNavigating = signal<boolean>(false);

  // Public readonly signals
  readonly isCollapsed = this._isCollapsed.asReadonly();
  readonly isMobileMenuOpen = this._isMobileMenuOpen.asReadonly();
  readonly activeRoute = this._activeRoute.asReadonly();
  readonly navigationHistory = this._navigationHistory.asReadonly();
  readonly isNavigating = this._isNavigating.asReadonly();

  // Navigation items configuration
  readonly navItems = signal<NavItem[]>([
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: 'dashboard',
      route: '/dashboard'
    },
    {
      id: 'projects',
      label: 'Projects',
      icon: 'folder',
      route: '/projects',
      badge: 0
    },
    {
      id: 'agents',
      label: 'AI Agents',
      icon: 'smart_toy',
      route: '/agents'
    }
  ]);

  // Computed breadcrumbs based on current route
  readonly breadcrumbs = computed<BreadcrumbItem[]>(() => {
    const route = this._activeRoute();
    const segments = route.split('/').filter((s: string) => s);
    
    console.log('[NavigationService] Computing breadcrumbs for route:', route);
    console.log('[NavigationService] Route segments:', segments);
    
    const breadcrumbs: BreadcrumbItem[] = [{ label: 'Home', route: '/' }];
    
    let currentPath = '';
    for (const segment of segments) {
      currentPath += `/${segment}`;
      const navItem = this.findNavItemByRoute(currentPath);
      breadcrumbs.push({
        label: navItem?.label || this.formatSegmentLabel(segment),
        route: currentPath
      });
    }
    
    console.log('[NavigationService] Generated breadcrumbs:', breadcrumbs);
    return breadcrumbs;
  });

  // Check if can go back
  readonly canGoBack = computed(() => {
    return this._navigationHistory().length > 1;
  });

  constructor() {
    console.log('[NavigationService] Initializing navigation service...');
    this.initRouterSubscription();
    this.loadPersistedState();
  }

  private initRouterSubscription(): void {
    console.log('[NavigationService] Setting up router subscription...');
    
    this.router.events.pipe(
      filter((event: Event): event is NavigationEnd => event instanceof NavigationEnd)
    ).subscribe((event: NavigationEnd) => {
      console.log('[NavigationService] Navigation ended:', event.urlAfterRedirects);
      
      this._activeRoute.set(event.urlAfterRedirects);
      this._isNavigating.set(false);
      
      // Update navigation history
      const history = this._navigationHistory();
      if (history[history.length - 1] !== event.urlAfterRedirects) {
        this._navigationHistory.set([...history, event.urlAfterRedirects].slice(-10)); // Keep last 10
      }
      
      // Close mobile menu on navigation
      if (this._isMobileMenuOpen()) {
        console.log('[NavigationService] Closing mobile menu after navigation');
        this._isMobileMenuOpen.set(false);
      }
    });
  }

  private loadPersistedState(): void {
    try {
      const savedCollapsed = localStorage.getItem('nav_collapsed');
      if (savedCollapsed !== null) {
        this._isCollapsed.set(savedCollapsed === 'true');
        console.log('[NavigationService] Loaded persisted collapsed state:', savedCollapsed);
      }
    } catch (error) {
      console.warn('[NavigationService] Could not load persisted state:', error);
    }
  }

  private persistState(): void {
    try {
      localStorage.setItem('nav_collapsed', String(this._isCollapsed()));
      console.log('[NavigationService] Persisted collapsed state:', this._isCollapsed());
    } catch (error) {
      console.warn('[NavigationService] Could not persist state:', error);
    }
  }

  private findNavItemByRoute(route: string): NavItem | undefined {
    const items = this.navItems();
    for (const item of items) {
      if (item.route === route) return item;
      if (item.children) {
        const child = item.children.find((c: NavItem) => c.route === route);
        if (child) return child;
      }
    }
    return undefined;
  }

  private formatSegmentLabel(segment: string): string {
    // Convert kebab-case or snake_case to Title Case
    return segment
      .replace(/[-_]/g, ' ')
      .replace(/\b\w/g, l => l.toUpperCase());
  }

  // Public methods
  toggleCollapse(): void {
    console.log('[NavigationService] Toggling collapse state');
    this._isCollapsed.set(!this._isCollapsed());
    this.persistState();
  }

  setCollapsed(collapsed: boolean): void {
    console.log('[NavigationService] Setting collapsed state:', collapsed);
    this._isCollapsed.set(collapsed);
    this.persistState();
  }

  toggleMobileMenu(): void {
    console.log('[NavigationService] Toggling mobile menu');
    this._isMobileMenuOpen.set(!this._isMobileMenuOpen());
  }

  closeMobileMenu(): void {
    console.log('[NavigationService] Closing mobile menu');
    this._isMobileMenuOpen.set(false);
  }

  openMobileMenu(): void {
    console.log('[NavigationService] Opening mobile menu');
    this._isMobileMenuOpen.set(true);
  }

  navigate(route: string): void {
    console.log('[NavigationService] Navigating to:', route);
    
    // Edge case: Check if route is valid
    if (!route || typeof route !== 'string') {
      console.error('[NavigationService] Invalid route provided:', route);
      return;
    }

    // Edge case: Already on this route
    if (this._activeRoute() === route) {
      console.log('[NavigationService] Already on route:', route);
      return;
    }

    // Edge case: Check if nav item is disabled
    const navItem = this.findNavItemByRoute(route);
    if (navItem?.disabled) {
      console.warn('[NavigationService] Navigation blocked - route is disabled:', route);
      return;
    }

    this._isNavigating.set(true);
    
    this.router.navigate([route]).then(
      (success: boolean) => {
        if (success) {
          console.log('[NavigationService] Navigation successful to:', route);
        } else {
          console.warn('[NavigationService] Navigation failed to:', route);
          this._isNavigating.set(false);
        }
      },
      (error: Error) => {
        console.error('[NavigationService] Navigation error:', error);
        this._isNavigating.set(false);
      }
    );
  }

  goBack(): void {
    console.log('[NavigationService] Going back...');
    
    const history = this._navigationHistory();
    if (history.length > 1) {
      // Remove current route and get previous
      const previousRoute = history[history.length - 2];
      this._navigationHistory.set(history.slice(0, -1));
      this.navigate(previousRoute);
    } else {
      console.log('[NavigationService] No history to go back to, navigating to home');
      this.navigate('/');
    }
  }

  isActiveRoute(route: string): boolean {
    const currentRoute = this._activeRoute();
    
    // Exact match
    if (currentRoute === route) return true;
    
    // Check if current route starts with the nav item route (for nested routes)
    if (route !== '/' && currentRoute.startsWith(route + '/')) return true;
    
    return false;
  }

  updateBadge(navItemId: string, count: number): void {
    console.log('[NavigationService] Updating badge for:', navItemId, 'count:', count);
    
    const items = this.navItems();
    const updatedItems = items.map((item: NavItem) => {
      if (item.id === navItemId) {
        return { ...item, badge: count };
      }
      return item;
    });
    this.navItems.set(updatedItems);
  }

  setNavItemDisabled(navItemId: string, disabled: boolean): void {
    console.log('[NavigationService] Setting disabled state for:', navItemId, 'disabled:', disabled);
    
    const items = this.navItems();
    const updatedItems = items.map((item: NavItem) => {
      if (item.id === navItemId) {
        return { ...item, disabled };
      }
      return item;
    });
    this.navItems.set(updatedItems);
  }
}
