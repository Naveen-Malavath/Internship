import { Injectable, signal } from '@angular/core';

export interface Activity {
  id: string;
  title: string;
  time: string;
  timestamp: number;
  icon: string;
  type: 'success' | 'info' | 'warning' | 'error';
}

@Injectable({
  providedIn: 'root'
})
export class ActivityService {
  private activities = signal<Activity[]>([]);
  
  // Public readonly signal
  readonly activitiesList = this.activities.asReadonly();
  
  constructor() {
    console.log('[ActivityService] Service initialized');
    this.loadActivitiesFromStorage();
  }
  
  /**
   * Add a new activity to the log
   * Edge cases handled:
   * - Duplicate entries (checked by title + time proximity)
   * - Maximum entries limit (keep last 50)
   * - Invalid data (fallback to defaults)
   */
  logActivity(title: string, icon: string = 'info', type: 'success' | 'info' | 'warning' | 'error' = 'info') {
    try {
      console.log('[ActivityService] Logging activity:', { title, icon, type });
      
      // Edge case: Empty title
      if (!title || title.trim().length === 0) {
        console.warn('[ActivityService] Empty activity title, skipping');
        return;
      }
      
      const now = Date.now();
      const timeAgo = this.getTimeAgo(now);
      
      // Edge case: Check for duplicate activity within last 5 seconds
      const recentActivities = this.activities().filter(a => now - a.timestamp < 5000);
      const isDuplicate = recentActivities.some(a => a.title === title);
      
      if (isDuplicate) {
        console.warn('[ActivityService] Duplicate activity detected, skipping:', title);
        return;
      }
      
      const activity: Activity = {
        id: `activity-${now}-${Math.random().toString(36).substr(2, 9)}`,
        title: title.trim(),
        time: timeAgo,
        timestamp: now,
        icon: icon || 'info',
        type: type || 'info'
      };
      
      // Add to beginning of array (most recent first)
      const updatedActivities = [activity, ...this.activities()];
      
      // Edge case: Limit to 50 activities to prevent memory issues
      const trimmedActivities = updatedActivities.slice(0, 50);
      
      this.activities.set(trimmedActivities);
      
      console.log('[ActivityService] Activity logged successfully. Total activities:', trimmedActivities.length);
      
      // Persist to localStorage
      this.saveActivitiesToStorage();
      
    } catch (error) {
      console.error('[ActivityService] Error logging activity:', error);
    }
  }
  
  /**
   * Get all activities
   */
  getActivities(): Activity[] {
    return this.activities();
  }
  
  /**
   * Get recent activities (last N)
   */
  getRecentActivities(count: number = 5): Activity[] {
    try {
      // Edge case: Invalid count
      const validCount = Math.max(1, Math.min(count, this.activities().length));
      return this.activities().slice(0, validCount);
    } catch (error) {
      console.error('[ActivityService] Error getting recent activities:', error);
      return [];
    }
  }
  
  /**
   * Clear all activities
   */
  clearActivities() {
    console.log('[ActivityService] Clearing all activities');
    this.activities.set([]);
    this.saveActivitiesToStorage();
  }
  
  /**
   * Update time labels (call periodically to refresh "X minutes ago" labels)
   */
  updateTimeLabels() {
    try {
      const now = Date.now();
      const updated = this.activities().map(activity => ({
        ...activity,
        time: this.getTimeAgo(activity.timestamp, now)
      }));
      this.activities.set(updated);
      console.log('[ActivityService] Time labels updated');
    } catch (error) {
      console.error('[ActivityService] Error updating time labels:', error);
    }
  }
  
  /**
   * Convert timestamp to human-readable "time ago" format
   * Edge cases:
   * - Future timestamps (show "Just now")
   * - Very old timestamps (show date)
   * - Invalid timestamps (fallback to "Unknown")
   */
  private getTimeAgo(timestamp: number, currentTime?: number): string {
    try {
      const now = currentTime || Date.now();
      const diff = now - timestamp;
      
      // Edge case: Future timestamp
      if (diff < 0) {
        console.warn('[ActivityService] Future timestamp detected:', timestamp);
        return 'Just now';
      }
      
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      
      if (seconds < 10) return 'Just now';
      if (seconds < 60) return `${seconds} seconds ago`;
      if (minutes === 1) return '1 minute ago';
      if (minutes < 60) return `${minutes} minutes ago`;
      if (hours === 1) return '1 hour ago';
      if (hours < 24) return `${hours} hours ago`;
      if (days === 1) return 'Yesterday';
      if (days < 7) return `${days} days ago`;
      
      // Edge case: Very old activity, show date
      const date = new Date(timestamp);
      return date.toLocaleDateString();
      
    } catch (error) {
      console.error('[ActivityService] Error calculating time ago:', error);
      return 'Unknown';
    }
  }
  
  /**
   * Save activities to localStorage for persistence across page navigation
   * (still resets on browser refresh, but survives SPA navigation)
   */
  private saveActivitiesToStorage() {
    try {
      const data = JSON.stringify(this.activities());
      localStorage.setItem('autoagents_activities', data);
      console.log('[ActivityService] Activities saved to localStorage');
    } catch (error) {
      console.error('[ActivityService] Error saving to localStorage:', error);
    }
  }
  
  /**
   * Load activities from localStorage on service init
   */
  private loadActivitiesFromStorage() {
    try {
      const data = localStorage.getItem('autoagents_activities');
      if (data) {
        const parsed = JSON.parse(data);
        
        // Edge case: Validate data structure
        if (Array.isArray(parsed)) {
          // Filter out invalid entries
          const validActivities = parsed.filter(a => 
            a && 
            typeof a.id === 'string' && 
            typeof a.title === 'string' && 
            typeof a.timestamp === 'number'
          );
          
          this.activities.set(validActivities);
          console.log('[ActivityService] Loaded', validActivities.length, 'activities from localStorage');
          
          // Update time labels after loading
          this.updateTimeLabels();
        } else {
          console.warn('[ActivityService] Invalid data structure in localStorage');
        }
      } else {
        console.log('[ActivityService] No saved activities found');
      }
    } catch (error) {
      console.error('[ActivityService] Error loading from localStorage:', error);
    }
  }
  
  /**
   * Helper methods for specific activity types
   */
  logProjectCreated(projectName: string) {
    this.logActivity(`Project "${projectName}" created`, 'folder', 'success');
  }
  
  logFeaturesGenerated(count: number) {
    this.logActivity(`AI Agent generated ${count} feature${count !== 1 ? 's' : ''}`, 'smart_toy', 'info');
  }
  
  logStoriesGenerated(count: number) {
    this.logActivity(`AI Agent generated ${count} user stor${count !== 1 ? 'ies' : 'y'}`, 'smart_toy', 'info');
  }
  
  logDesignGenerated(designType: string) {
    const labels: Record<string, string> = {
      'hld': 'High Level Design',
      'dbd': 'Database Design',
      'api': 'API Design',
      'lld': 'Low Level Design',
      'dfd': 'Data Flow Diagram',
      'component': 'Component Diagram',
      'security': 'Security Architecture',
      'infrastructure': 'Infrastructure Design',
      'state': 'State Diagram',
      'journey': 'User Journey',
      'sequence': 'Sequence Diagram',
      'mindmap': 'Feature Mindmap',
      'gantt': 'Project Timeline',
      'gitflow': 'Git Workflow'
    };
    
    const label = labels[designType] || designType;
    this.logActivity(`${label} completed`, 'check_circle', 'success');
  }
  
  logWireframesGenerated(pageCount: number) {
    this.logActivity(`${pageCount} wireframe page${pageCount !== 1 ? 's' : ''} generated`, 'web', 'success');
  }
  
  logFeatureApproved(featureTitle: string) {
    this.logActivity(`Feature "${featureTitle}" approved`, 'check_circle', 'success');
  }
  
  logStoryApproved(storyTitle: string) {
    this.logActivity(`Story "${storyTitle}" approved`, 'check_circle', 'success');
  }
  
  logError(message: string) {
    this.logActivity(message, 'error', 'error');
  }
}
