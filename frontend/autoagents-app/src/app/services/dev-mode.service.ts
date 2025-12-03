import { Injectable, signal } from '@angular/core';

/**
 * Dev Mode Service
 * 
 * Manages development mode state for bypassing API calls during development.
 * State is persisted in localStorage to survive page refreshes.
 * 
 * DELETE THIS SERVICE BEFORE PRODUCTION DEPLOYMENT
 */
@Injectable({
  providedIn: 'root'
})
export class DevModeService {
  private readonly STORAGE_KEY = 'autoagent_dev_mode';
  
  // Signal for reactive state
  isDevMode = signal(this.loadDevModeState());
  
  constructor() {
    console.log('[DEV MODE] Service initialized. Dev mode:', this.isDevMode() ? 'ON' : 'OFF');
  }
  
  private loadDevModeState(): boolean {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored === 'true';
    } catch {
      return false;
    }
  }
  
  toggleDevMode(): void {
    const newState = !this.isDevMode();
    this.isDevMode.set(newState);
    localStorage.setItem(this.STORAGE_KEY, String(newState));
    console.log('[DEV MODE] Toggled to:', newState ? 'ON' : 'OFF');
  }
  
  enableDevMode(): void {
    this.isDevMode.set(true);
    localStorage.setItem(this.STORAGE_KEY, 'true');
    console.log('[DEV MODE] Enabled');
  }
  
  disableDevMode(): void {
    this.isDevMode.set(false);
    localStorage.setItem(this.STORAGE_KEY, 'false');
    console.log('[DEV MODE] Disabled');
  }
}
