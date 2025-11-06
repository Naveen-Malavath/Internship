import { Injectable, signal } from '@angular/core';
import { Router } from '@angular/router';

export interface User {
  email: string;
  name: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private currentUserSignal = signal<User | null>(null);
  currentUser = this.currentUserSignal.asReadonly();

  constructor(private router: Router) {
    // Check if user is logged in from localStorage
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
      this.currentUserSignal.set(JSON.parse(savedUser));
    }
  }

  login(email: string, password: string): boolean {
    // Simple validation - in production, this would call a backend API
    if (email && password.length >= 6) {
      const user: User = {
        email: email,
        name: email.split('@')[0]
      };
      
      this.currentUserSignal.set(user);
      localStorage.setItem('currentUser', JSON.stringify(user));
      this.router.navigate(['/chat']);
      return true;
    }
    return false;
  }

  logout(): void {
    this.currentUserSignal.set(null);
    localStorage.removeItem('currentUser');
    this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    return this.currentUserSignal() !== null;
  }
}



