import { Routes } from '@angular/router';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { ProjectsComponent } from './pages/projects/projects.component';
import { WorkspacePageComponent } from './pages/workspace/workspace-page.component';
import { PlaceholderPageComponent } from './pages/placeholder/placeholder-page.component';

export const routes: Routes = [
  // Default route - redirect to dashboard
  {
    path: '',
    redirectTo: '/dashboard',
    pathMatch: 'full'
  },
  
  // Dashboard - main landing page
  {
    path: 'dashboard',
    component: DashboardComponent,
    title: 'Dashboard - AutoAgents'
  },
  
  // Projects management
  {
    path: 'projects',
    component: ProjectsComponent,
    title: 'Projects - AutoAgents'
  },
  
  // Workspace - project design and architecture
  {
    path: 'workspace',
    component: WorkspacePageComponent,
    title: 'Workspace - AutoAgents'
  },
  
  // Wildcard route - 404 handling
  {
    path: '**',
    component: PlaceholderPageComponent,
    title: 'Page Not Found - AutoAgents',
    data: {
      title: 'Page Not Found',
      description: 'The page you are looking for does not exist or has been moved.',
      icon: 'error_outline'
    }
  }
];
