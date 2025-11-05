import { Component, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  email = signal('');
  password = signal('');
  error = signal('');
  showPassword = signal(false);

  constructor(private authService: AuthService) {}

  onSubmit(): void {
    this.error.set('');
    
    if (!this.email() || !this.password()) {
      this.error.set('Please fill in all fields');
      return;
    }

    if (!this.isValidEmail(this.email())) {
      this.error.set('Please enter a valid email address');
      return;
    }

    if (this.password().length < 6) {
      this.error.set('Password must be at least 6 characters');
      return;
    }

    const success = this.authService.login(this.email(), this.password());
    
    if (!success) {
      this.error.set('Login failed. Please try again.');
    }
  }

  private isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  togglePasswordVisibility(): void {
    this.showPassword.set(!this.showPassword());
  }
}

