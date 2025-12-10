import { Component, Input, OnInit, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-placeholder-page',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="placeholder-container">
      <div class="placeholder-content">
        <div class="icon-wrapper">
          <mat-icon>{{ icon }}</mat-icon>
        </div>
        <h1>{{ title }}</h1>
        <p class="description">{{ description }}</p>
        <div class="coming-soon-badge">
          <mat-icon>schedule</mat-icon>
          <span>Coming Soon</span>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .placeholder-container {
      min-height: calc(100vh - 200px);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 2rem;
    }

    .placeholder-content {
      text-align: center;
      max-width: 500px;
    }

    .icon-wrapper {
      width: 120px;
      height: 120px;
      margin: 0 auto 2rem;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(59, 130, 246, 0.1);
      border-radius: 50%;
      border: 2px solid rgba(59, 130, 246, 0.2);

      mat-icon {
        font-size: 56px;
        width: 56px;
        height: 56px;
        color: #3b82f6;
      }
    }

    h1 {
      font-size: 2rem;
      font-weight: 700;
      color: #f1f5f9;
      margin: 0 0 1rem 0;
    }

    .description {
      font-size: 1rem;
      color: #94a3b8;
      margin: 0 0 2rem 0;
      line-height: 1.6;
    }

    .coming-soon-badge {
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem 1.5rem;
      background: rgba(245, 158, 11, 0.15);
      border: 1px solid rgba(245, 158, 11, 0.3);
      border-radius: 30px;
      color: #fbbf24;
      font-size: 0.9375rem;
      font-weight: 600;

      mat-icon {
        font-size: 18px;
        width: 18px;
        height: 18px;
      }
    }

    @media (max-width: 768px) {
      h1 {
        font-size: 1.5rem;
      }

      .icon-wrapper {
        width: 80px;
        height: 80px;

        mat-icon {
          font-size: 40px;
          width: 40px;
          height: 40px;
        }
      }
    }
  `]
})
export class PlaceholderPageComponent implements OnInit {
  private route = inject(ActivatedRoute);
  
  @Input() title = 'Page';
  @Input() description = 'This page is currently under development.';
  @Input() icon = 'construction';

  ngOnInit(): void {
    // Get data from route if available
    const routeData = this.route.snapshot.data;
    
    if (routeData['title']) {
      this.title = routeData['title'];
    }
    if (routeData['description']) {
      this.description = routeData['description'];
    }
    if (routeData['icon']) {
      this.icon = routeData['icon'];
    }
    
    console.log('[PlaceholderPage] Rendering placeholder for:', this.title);
    console.log('[PlaceholderPage] Route data:', routeData);
  }
}
