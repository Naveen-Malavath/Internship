import { Routes } from '@angular/router';

import { ChatPageComponent } from './pages/chat-page/chat-page.component';

export const routes: Routes = [
  {
    path: '',
    loadComponent: () => import('./app').then((m) => m.App),
  },
  {
    path: 'chat',
    loadComponent: () => import('./pages/chat-page/chat-page.component').then((m) => m.ChatPageComponent),
  },
  {
    path: '**',
    redirectTo: '',
  },
];
