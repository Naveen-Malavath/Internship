/**
 * DEV MODE - Mock Data for Development
 * 
 * This file contains sample data to bypass feature/story generation
 * during development. Delete this file before production deployment.
 * 
 * Toggle dev mode via the UI switch or localStorage key: 'autoagent_dev_mode'
 */

import { Feature, Story } from './api.service';

// Sample Project Context
export const MOCK_PROJECT_CONTEXT = {
  projectName: 'E-Commerce Platform',
  industry: 'Retail & E-Commerce',
  methodology: 'Agile',
  promptSummary: `Build a modern e-commerce platform with the following capabilities:
- User registration and authentication
- Product catalog with search and filtering
- Shopping cart and checkout process
- Payment processing integration
- Order management and tracking
- Admin dashboard for inventory management
- Customer reviews and ratings
- Recommendation engine based on user behavior`,
  focusAreas: 'Scalability, Security, User Experience'
};

// Pre-generated Features (what would come from AI)
export const MOCK_FEATURES: Feature[] = [
  {
    title: 'User Authentication & Profile Management',
    reason: 'Enable secure user access and personalized experience',
    acceptanceCriteria: 'Users can register, login, logout, reset password, and manage profile settings',
    problemStatement: 'Users need secure access to their accounts and personalized shopping experience',
    businessObjective: 'Increase user retention and enable personalized marketing',
    userPersona: 'Online shoppers who value security and convenience',
    detailedDescription: 'Implement OAuth2-based authentication with support for social logins (Google, Facebook). Include 2FA option, session management, and profile customization features.',
    successMetrics: '95% login success rate, <2s authentication time, 80% profile completion rate',
    dependencies: 'Identity provider integration, Email service for verification',
    approved: true
  },
  {
    title: 'Product Catalog & Search',
    reason: 'Allow users to discover and browse products efficiently',
    acceptanceCriteria: 'Users can search, filter, sort, and view detailed product information',
    problemStatement: 'Users need to find products quickly among thousands of items',
    businessObjective: 'Reduce time-to-purchase and increase conversion rates',
    userPersona: 'Shoppers looking for specific products or browsing categories',
    detailedDescription: 'Full-text search with Elasticsearch, faceted filtering by category/price/brand/rating, product detail pages with images, specifications, and related items.',
    successMetrics: '<500ms search response, 70% search-to-click rate, 40% cross-sell engagement',
    dependencies: 'Product data ingestion pipeline, CDN for images',
    approved: true
  },
  {
    title: 'Shopping Cart & Checkout',
    reason: 'Enable seamless purchase flow from cart to order confirmation',
    acceptanceCriteria: 'Users can add/remove items, apply coupons, select shipping, and complete payment',
    problemStatement: 'Cart abandonment is high due to complex checkout processes',
    businessObjective: 'Reduce cart abandonment rate and increase average order value',
    userPersona: 'Ready-to-buy customers who expect a smooth checkout experience',
    detailedDescription: 'Persistent cart across sessions, guest checkout option, multiple payment methods (cards, PayPal, Apple Pay), address validation, shipping calculator, and order summary.',
    successMetrics: '<5% cart abandonment rate, 3-step checkout completion, 98% payment success rate',
    dependencies: 'Payment gateway integration, Shipping API integration',
    approved: true
  },
  {
    title: 'Order Management & Tracking',
    reason: 'Keep customers informed about their order status',
    acceptanceCriteria: 'Users can view order history, track shipments, and manage returns',
    problemStatement: 'Customers frequently contact support for order status updates',
    businessObjective: 'Reduce support tickets and increase customer satisfaction',
    userPersona: 'Post-purchase customers wanting visibility into their orders',
    detailedDescription: 'Real-time order status updates, integration with shipping carriers for tracking, email/SMS notifications, self-service return initiation, and refund tracking.',
    successMetrics: '50% reduction in order status inquiries, 90% tracking accuracy, <24h return processing',
    dependencies: 'Carrier API integrations, Notification service',
    approved: true
  },
  {
    title: 'Admin Dashboard & Inventory',
    reason: 'Enable business operations and inventory management',
    acceptanceCriteria: 'Admins can manage products, inventory, orders, and view analytics',
    problemStatement: 'Manual inventory management leads to overselling and stockouts',
    businessObjective: 'Optimize inventory levels and streamline operations',
    userPersona: 'Store managers and operations team members',
    detailedDescription: 'Role-based admin access, bulk product import/export, inventory alerts, sales analytics dashboard, customer management, and reporting tools.',
    successMetrics: 'Zero oversells, 95% inventory accuracy, real-time analytics updates',
    dependencies: 'Analytics platform, Bulk processing infrastructure',
    approved: true
  },
  {
    title: 'Reviews, Ratings & Recommendations',
    reason: 'Build trust and increase engagement through social proof',
    acceptanceCriteria: 'Users can write reviews, rate products, and receive personalized recommendations',
    problemStatement: 'New customers lack trust signals and personalized discovery',
    businessObjective: 'Increase conversion through social proof and cross-selling',
    userPersona: 'Customers seeking validation and discovering new products',
    detailedDescription: 'Verified purchase reviews, photo/video reviews, helpful vote system, ML-based recommendation engine using collaborative filtering and browsing history.',
    successMetrics: '25% of customers leave reviews, 15% recommendation click-through, 4+ average rating display',
    dependencies: 'ML recommendation service, Content moderation',
    approved: true
  }
];

// Pre-generated Stories (what would come from AI)
export const MOCK_STORIES: Story[] = [
  // Authentication Stories
  { title: 'User Registration', description: 'As a new user, I want to create an account with email and password so that I can access personalized features', featureRef: 'User Authentication & Profile Management', approved: true },
  { title: 'Social Login', description: 'As a user, I want to sign in with Google or Facebook so that I can quickly access my account without remembering another password', featureRef: 'User Authentication & Profile Management', approved: true },
  { title: 'Password Reset', description: 'As a user, I want to reset my forgotten password via email so that I can regain access to my account', featureRef: 'User Authentication & Profile Management', approved: true },
  { title: 'Two-Factor Authentication', description: 'As a security-conscious user, I want to enable 2FA so that my account is protected from unauthorized access', featureRef: 'User Authentication & Profile Management', approved: true },
  { title: 'Profile Management', description: 'As a user, I want to update my profile information and preferences so that my experience is personalized', featureRef: 'User Authentication & Profile Management', approved: true },

  // Product Catalog Stories
  { title: 'Product Search', description: 'As a shopper, I want to search for products by keyword so that I can quickly find what I need', featureRef: 'Product Catalog & Search', approved: true },
  { title: 'Category Browsing', description: 'As a shopper, I want to browse products by category so that I can discover items in specific departments', featureRef: 'Product Catalog & Search', approved: true },
  { title: 'Product Filtering', description: 'As a shopper, I want to filter products by price, brand, and rating so that I can narrow down my options', featureRef: 'Product Catalog & Search', approved: true },
  { title: 'Product Details', description: 'As a shopper, I want to view detailed product information, images, and specs so that I can make informed decisions', featureRef: 'Product Catalog & Search', approved: true },
  { title: 'Product Comparison', description: 'As a shopper, I want to compare multiple products side-by-side so that I can choose the best option', featureRef: 'Product Catalog & Search', approved: true },

  // Shopping Cart Stories
  { title: 'Add to Cart', description: 'As a shopper, I want to add products to my cart so that I can purchase multiple items together', featureRef: 'Shopping Cart & Checkout', approved: true },
  { title: 'Cart Management', description: 'As a shopper, I want to update quantities and remove items from my cart so that I can adjust my order', featureRef: 'Shopping Cart & Checkout', approved: true },
  { title: 'Guest Checkout', description: 'As a guest, I want to checkout without creating an account so that I can complete my purchase quickly', featureRef: 'Shopping Cart & Checkout', approved: true },
  { title: 'Apply Coupon', description: 'As a shopper, I want to apply discount codes so that I can save money on my purchase', featureRef: 'Shopping Cart & Checkout', approved: true },
  { title: 'Payment Processing', description: 'As a shopper, I want to pay with my preferred payment method so that I can complete my order securely', featureRef: 'Shopping Cart & Checkout', approved: true },

  // Order Management Stories
  { title: 'Order Confirmation', description: 'As a customer, I want to receive order confirmation via email so that I have a record of my purchase', featureRef: 'Order Management & Tracking', approved: true },
  { title: 'Order History', description: 'As a customer, I want to view my past orders so that I can track my purchase history', featureRef: 'Order Management & Tracking', approved: true },
  { title: 'Shipment Tracking', description: 'As a customer, I want to track my shipment in real-time so that I know when to expect delivery', featureRef: 'Order Management & Tracking', approved: true },
  { title: 'Return Request', description: 'As a customer, I want to initiate a return online so that I can get a refund without calling support', featureRef: 'Order Management & Tracking', approved: true },
  { title: 'Order Notifications', description: 'As a customer, I want to receive SMS/email updates so that I stay informed about my order status', featureRef: 'Order Management & Tracking', approved: true },

  // Admin Dashboard Stories
  { title: 'Product Management', description: 'As an admin, I want to add and edit products so that the catalog stays up-to-date', featureRef: 'Admin Dashboard & Inventory', approved: true },
  { title: 'Inventory Tracking', description: 'As an admin, I want to view and update inventory levels so that I can prevent stockouts', featureRef: 'Admin Dashboard & Inventory', approved: true },
  { title: 'Order Processing', description: 'As an admin, I want to view and process orders so that customers receive their purchases promptly', featureRef: 'Admin Dashboard & Inventory', approved: true },
  { title: 'Sales Analytics', description: 'As a manager, I want to view sales reports and analytics so that I can make data-driven decisions', featureRef: 'Admin Dashboard & Inventory', approved: true },
  { title: 'Low Stock Alerts', description: 'As an admin, I want to receive alerts for low inventory so that I can reorder in time', featureRef: 'Admin Dashboard & Inventory', approved: true },

  // Reviews & Recommendations Stories
  { title: 'Write Review', description: 'As a customer, I want to write a review for purchased products so that I can share my experience', featureRef: 'Reviews, Ratings & Recommendations', approved: true },
  { title: 'Rate Products', description: 'As a customer, I want to rate products on a 5-star scale so that others can see quality at a glance', featureRef: 'Reviews, Ratings & Recommendations', approved: true },
  { title: 'View Recommendations', description: 'As a shopper, I want to see personalized product recommendations so that I can discover relevant items', featureRef: 'Reviews, Ratings & Recommendations', approved: true },
  { title: 'Helpful Votes', description: 'As a shopper, I want to mark reviews as helpful so that the best reviews are highlighted', featureRef: 'Reviews, Ratings & Recommendations', approved: true },
  { title: 'Photo Reviews', description: 'As a customer, I want to upload photos with my review so that others can see real product images', featureRef: 'Reviews, Ratings & Recommendations', approved: true }
];

// Pre-generated Project Summary (for design chaining)
export const MOCK_PROJECT_SUMMARY = `
# E-Commerce Platform - Project Summary

## Overview
A modern, scalable e-commerce platform designed for retail businesses. The platform supports B2C transactions with a focus on user experience, security, and operational efficiency.

## Core Modules
1. **User Management**: OAuth2 authentication, social logins, 2FA, profile management
2. **Product Catalog**: Elasticsearch-powered search, faceted filtering, category hierarchy
3. **Shopping Cart**: Persistent carts, guest checkout, multi-payment support
4. **Order System**: Real-time tracking, carrier integrations, automated notifications
5. **Admin Portal**: Inventory management, analytics, role-based access
6. **Engagement**: Reviews, ratings, ML-powered recommendations

## Technical Stack
- Frontend: Angular 18+ with Material Design
- Backend: Node.js/Python microservices
- Database: PostgreSQL (primary), Redis (cache), Elasticsearch (search)
- Infrastructure: AWS/GCP with Kubernetes orchestration
- Security: OAuth2, JWT tokens, encryption at rest/transit

## Key Integrations
- Payment: Stripe, PayPal, Apple Pay
- Shipping: FedEx, UPS, USPS APIs
- Analytics: Google Analytics, custom dashboards
- CDN: CloudFront for static assets

## Non-Functional Requirements
- 99.9% uptime SLA
- <500ms API response times
- WCAG 2.1 AA accessibility
- GDPR/CCPA compliance
- PCI DSS for payment handling
`;

// Mock Design Summaries (for chaining between design types)
export const MOCK_DESIGN_SUMMARIES = {
  hld: `High-Level Architecture: 3-tier architecture with Angular frontend, API Gateway routing to microservices (User, Product, Order, Payment, Notification), PostgreSQL and Redis databases, deployed on Kubernetes with auto-scaling.`,
  
  dbd: `Database Design: PostgreSQL with tables for users, products, categories, orders, order_items, carts, reviews, inventory. Redis for session/cache. Elasticsearch for product search indexing.`,
  
  api: `API Design: RESTful APIs with versioning (/api/v1/). Key endpoints: /auth (login, register, refresh), /products (CRUD, search), /cart (manage items), /orders (create, track), /admin (inventory, reports). JWT authentication, rate limiting.`,
  
  lld: `Low-Level Design: Service layer patterns with Repository abstraction. Cart service handles session persistence, Order service implements saga pattern for distributed transactions, Product service uses CQRS for search optimization.`,
  
  dfd: `Data Flow: User requests → API Gateway → Load Balancer → Service Mesh → Microservices → Database/Cache. Event-driven order processing via message queue. Async notification dispatch.`,
  
  component: `Component Architecture: Shared UI library (buttons, forms, modals), Feature modules (ProductModule, CartModule, CheckoutModule), Core services (AuthService, ApiService, StateService), Lazy-loaded admin module.`,
  
  security: `Security Architecture: WAF at edge, OAuth2 + JWT auth, RBAC for admin, encryption (AES-256 at rest, TLS 1.3 in transit), input validation, SQL injection prevention, XSS protection, rate limiting, audit logging.`,
  
  infrastructure: `Infrastructure: Multi-AZ deployment on AWS. EKS for containers, RDS for PostgreSQL, ElastiCache for Redis, CloudFront CDN, S3 for assets, ALB for load balancing, Route53 for DNS. Terraform IaC.`,
  
  state: `State Management: NgRx store for global state (user, cart, products). Effects for async operations. Selectors for derived data. Local component state for UI. Optimistic updates for cart operations.`,
  
  wireframe: `Wireframe Design: Homepage with hero, categories, featured products. PLP with filters sidebar, grid view. PDP with image gallery, specs, reviews. Cart drawer with summary. 3-step checkout flow. Admin dashboard with sidebar navigation.`
};

// Mock Wireframe Pages Data - Feature-based pages for testing
export const MOCK_WIREFRAME_DATA = {
  pages: [
    {
      id: 'dashboard',
      name: 'Admin Dashboard',
      type: 'dashboard',
      description: 'Main admin dashboard with KPIs, analytics, and order overview',
      related_features: ['Admin Dashboard & Inventory', 'Order Management & Tracking'],
      related_stories: ['Sales Analytics', 'Order Processing'],
      functionality: ['View key metrics', 'Monitor sales', 'Track orders', 'View inventory status'],
      ui_elements: ['KPI cards', 'Revenue chart', 'Orders chart', 'Recent orders table'],
      data_displayed: ['Total revenue', 'Orders count', 'Customers count', 'Conversion rate'],
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-200">
    <div class="flex min-h-screen">
        <!-- Sidebar -->
        <aside class="w-64 bg-slate-800 border-r border-slate-700">
            <div class="p-4 border-b border-slate-700">
                <h1 class="text-xl font-bold text-white flex items-center gap-2">
                    <span class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">E</span>
                    E-Commerce
                </h1>
            </div>
            <nav class="p-3 space-y-1">
                <a href="#" class="flex items-center gap-3 px-4 py-3 bg-blue-500/20 text-blue-400 rounded-lg">
                    <span>📊</span> Dashboard
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>📦</span> Products
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>🛒</span> Orders
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>👥</span> Customers
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>⚙️</span> Settings
                </a>
            </nav>
        </aside>
        
        <!-- Main Content -->
        <div class="flex-1 flex flex-col">
            <!-- Header -->
            <header class="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6">
                <div class="flex items-center gap-4">
                    <input type="text" placeholder="Search..." class="w-64 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-200">
                </div>
                <div class="flex items-center gap-4">
                    <button class="p-2 text-slate-400 hover:bg-slate-700 rounded-lg">🔔</button>
                    <div class="w-8 h-8 bg-blue-500 rounded-full"></div>
                </div>
            </header>
            
            <!-- Dashboard Content -->
            <main class="flex-1 p-6 overflow-auto">
                <h2 class="text-2xl font-bold text-white mb-6">Dashboard Overview</h2>
                
                <!-- KPI Cards -->
                <div class="grid grid-cols-4 gap-6 mb-8">
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-slate-400">Total Revenue</span>
                            <span class="text-green-400 text-sm">+12.5%</span>
                        </div>
                        <div class="text-3xl font-bold text-white">$124,563</div>
                        <div class="text-sm text-slate-500 mt-2">vs last month</div>
                    </div>
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-slate-400">Orders</span>
                            <span class="text-green-400 text-sm">+8.2%</span>
                        </div>
                        <div class="text-3xl font-bold text-white">1,247</div>
                        <div class="text-sm text-slate-500 mt-2">this month</div>
                    </div>
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-slate-400">Customers</span>
                            <span class="text-green-400 text-sm">+15.3%</span>
                        </div>
                        <div class="text-3xl font-bold text-white">8,421</div>
                        <div class="text-sm text-slate-500 mt-2">total active</div>
                    </div>
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <div class="flex items-center justify-between mb-4">
                            <span class="text-slate-400">Conversion</span>
                            <span class="text-red-400 text-sm">-2.1%</span>
                        </div>
                        <div class="text-3xl font-bold text-white">3.24%</div>
                        <div class="text-sm text-slate-500 mt-2">avg rate</div>
                    </div>
                </div>
                
                <!-- Charts Section -->
                <div class="grid grid-cols-2 gap-6 mb-8">
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <h3 class="text-lg font-semibold text-white mb-4">Revenue Trend</h3>
                        <div class="h-64 bg-slate-700/50 rounded-lg flex items-center justify-center">
                            <span class="text-slate-500">📈 Line Chart Placeholder</span>
                        </div>
                    </div>
                    <div class="bg-slate-800 rounded-xl p-6 border border-slate-700">
                        <h3 class="text-lg font-semibold text-white mb-4">Sales by Category</h3>
                        <div class="h-64 bg-slate-700/50 rounded-lg flex items-center justify-center">
                            <span class="text-slate-500">🥧 Pie Chart Placeholder</span>
                        </div>
                    </div>
                </div>
                
                <!-- Recent Orders -->
                <div class="bg-slate-800 rounded-xl border border-slate-700">
                    <div class="p-6 border-b border-slate-700">
                        <h3 class="text-lg font-semibold text-white">Recent Orders</h3>
                    </div>
                    <table class="w-full">
                        <thead>
                            <tr class="text-left text-slate-400 text-sm border-b border-slate-700">
                                <th class="px-6 py-4">Order ID</th>
                                <th class="px-6 py-4">Customer</th>
                                <th class="px-6 py-4">Product</th>
                                <th class="px-6 py-4">Amount</th>
                                <th class="px-6 py-4">Status</th>
                                <th class="px-6 py-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-700">
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4 text-white">#ORD-001</td>
                                <td class="px-6 py-4">John Smith</td>
                                <td class="px-6 py-4">MacBook Pro 16"</td>
                                <td class="px-6 py-4 text-white">$2,499</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">Completed</span></td>
                                <td class="px-6 py-4"><button class="text-blue-400 hover:underline">View</button></td>
                            </tr>
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4 text-white">#ORD-002</td>
                                <td class="px-6 py-4">Sarah Johnson</td>
                                <td class="px-6 py-4">iPhone 15 Pro</td>
                                <td class="px-6 py-4 text-white">$1,199</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">Processing</span></td>
                                <td class="px-6 py-4"><button class="text-blue-400 hover:underline">View</button></td>
                            </tr>
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4 text-white">#ORD-003</td>
                                <td class="px-6 py-4">Mike Wilson</td>
                                <td class="px-6 py-4">AirPods Max</td>
                                <td class="px-6 py-4 text-white">$549</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-sm">Shipped</span></td>
                                <td class="px-6 py-4"><button class="text-blue-400 hover:underline">View</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </main>
        </div>
    </div>
</body>
</html>`,
      component_ts: `import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, Sort } from '@angular/material/sort';

interface KpiCard {
  title: string;
  value: string;
  change: number;
  changeType: 'positive' | 'negative';
}

interface RecentOrder {
  id: string;
  customer: string;
  product: string;
  amount: number;
  status: 'completed' | 'processing' | 'shipped';
}

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatSortModule
  ],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // KPI Cards
  kpiCards = signal<KpiCard[]>([
    { title: 'Total Revenue', value: '$124,563', change: 12.5, changeType: 'positive' },
    { title: 'Orders', value: '1,247', change: 8.2, changeType: 'positive' },
    { title: 'Customers', value: '8,421', change: 15.3, changeType: 'positive' },
    { title: 'Conversion', value: '3.24%', change: -2.1, changeType: 'negative' }
  ]);

  // Recent Orders Table
  displayedColumns = ['id', 'customer', 'product', 'amount', 'status', 'actions'];
  ordersDataSource = new MatTableDataSource<RecentOrder>();

  isLoading = signal(false);

  ngOnInit(): void {
    this.loadDashboardData();
  }

  async loadDashboardData(): Promise<void> {
    this.isLoading.set(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500));
      
      this.ordersDataSource.data = [
        { id: '#ORD-001', customer: 'John Smith', product: 'MacBook Pro 16"', amount: 2499, status: 'completed' },
        { id: '#ORD-002', customer: 'Sarah Johnson', product: 'iPhone 15 Pro', amount: 1199, status: 'processing' },
        { id: '#ORD-003', customer: 'Mike Wilson', product: 'AirPods Max', amount: 549, status: 'shipped' }
      ];
    } finally {
      this.isLoading.set(false);
    }
  }

  getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      'completed': 'status-completed',
      'processing': 'status-processing',
      'shipped': 'status-shipped'
    };
    return classes[status] || '';
  }

  viewOrder(order: RecentOrder): void {
    console.log('View order:', order.id);
  }

  refreshData(): void {
    this.loadDashboardData();
  }
}`,
      component_html: `<div class="dashboard-container">
  <!-- Page Header -->
  <header class="page-header">
    <h1>Dashboard Overview</h1>
    <button mat-stroked-button (click)="refreshData()">
      <mat-icon>refresh</mat-icon>
      Refresh
    </button>
  </header>

  <!-- KPI Cards -->
  <div class="kpi-grid">
    @for (card of kpiCards(); track card.title) {
      <mat-card class="kpi-card">
        <mat-card-header>
          <mat-card-title>{{ card.title }}</mat-card-title>
          <span class="change-indicator" [class]="card.changeType">
            {{ card.change > 0 ? '+' : '' }}{{ card.change }}%
          </span>
        </mat-card-header>
        <mat-card-content>
          <div class="kpi-value">{{ card.value }}</div>
          <div class="kpi-subtitle">vs last month</div>
        </mat-card-content>
      </mat-card>
    }
  </div>

  <!-- Charts Section -->
  <div class="charts-grid">
    <mat-card class="chart-card">
      <mat-card-header>
        <mat-card-title>Revenue Trend</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <div class="chart-placeholder">
          <mat-icon>show_chart</mat-icon>
          <span>Line Chart Placeholder</span>
        </div>
      </mat-card-content>
    </mat-card>
    
    <mat-card class="chart-card">
      <mat-card-header>
        <mat-card-title>Sales by Category</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <div class="chart-placeholder">
          <mat-icon>pie_chart</mat-icon>
          <span>Pie Chart Placeholder</span>
        </div>
      </mat-card-content>
    </mat-card>
  </div>

  <!-- Recent Orders Table -->
  <mat-card class="orders-card">
    <mat-card-header>
      <mat-card-title>Recent Orders</mat-card-title>
    </mat-card-header>
    <mat-card-content>
      <table mat-table [dataSource]="ordersDataSource" matSort>
        <ng-container matColumnDef="id">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Order ID</th>
          <td mat-cell *matCellDef="let order">{{ order.id }}</td>
        </ng-container>

        <ng-container matColumnDef="customer">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Customer</th>
          <td mat-cell *matCellDef="let order">{{ order.customer }}</td>
        </ng-container>

        <ng-container matColumnDef="product">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Product</th>
          <td mat-cell *matCellDef="let order">{{ order.product }}</td>
        </ng-container>

        <ng-container matColumnDef="amount">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Amount</th>
          <td mat-cell *matCellDef="let order">\${{ order.amount | number }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Status</th>
          <td mat-cell *matCellDef="let order">
            <span class="status-badge" [class]="getStatusClass(order.status)">
              {{ order.status }}
            </span>
          </td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>Actions</th>
          <td mat-cell *matCellDef="let order">
            <button mat-button color="primary" (click)="viewOrder(order)">View</button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>
    </mat-card-content>
  </mat-card>
</div>`,
      component_scss: `.dashboard-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

// KPI Cards Grid
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.kpi-card {
  .change-indicator {
    font-size: 14px;
    font-weight: 600;
    
    &.positive { color: #10b981; }
    &.negative { color: #ef4444; }
  }

  .kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #1e293b;
    margin: 16px 0 4px;
  }

  .kpi-subtitle {
    font-size: 14px;
    color: #64748b;
  }
}

// Charts Grid
.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.chart-card {
  .chart-placeholder {
    height: 280px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: #f8fafc;
    border-radius: 8px;
    color: #94a3b8;
    gap: 12px;

    mat-icon {
      font-size: 48px;
      width: 48px;
      height: 48px;
    }
  }
}

// Orders Table
.orders-card {
  table {
    width: 100%;
  }

  .status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;

    &.status-completed {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
    }

    &.status-processing {
      background: rgba(245, 158, 11, 0.1);
      color: #f59e0b;
    }

    &.status-shipped {
      background: rgba(59, 130, 246, 0.1);
      color: #3b82f6;
    }
  }
}`
    },
    {
      id: 'products-list',
      name: 'Product Catalog',
      type: 'list',
      description: 'Product catalog with search, filters, and inventory management',
      related_features: ['Product Catalog & Search', 'Admin Dashboard & Inventory'],
      related_stories: ['Product Search', 'Product Filtering', 'Product Management', 'Inventory Tracking'],
      functionality: ['Search products', 'Filter by category/status', 'Add new products', 'Edit products', 'Delete products', 'View inventory'],
      ui_elements: ['Search bar', 'Category filter', 'Status filter', 'Product table', 'Pagination'],
      data_displayed: ['Product name', 'SKU', 'Category', 'Price', 'Stock level', 'Status'],
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Products</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-200">
    <div class="flex min-h-screen">
        <!-- Sidebar -->
        <aside class="w-64 bg-slate-800 border-r border-slate-700">
            <div class="p-4 border-b border-slate-700">
                <h1 class="text-xl font-bold text-white flex items-center gap-2">
                    <span class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">E</span>
                    E-Commerce
                </h1>
            </div>
            <nav class="p-3 space-y-1">
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>📊</span> Dashboard
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 bg-blue-500/20 text-blue-400 rounded-lg">
                    <span>📦</span> Products
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>🛒</span> Orders
                </a>
                <a href="#" class="flex items-center gap-3 px-4 py-3 text-slate-400 hover:bg-slate-700 rounded-lg">
                    <span>👥</span> Customers
                </a>
            </nav>
        </aside>
        
        <!-- Main Content -->
        <div class="flex-1 flex flex-col">
            <header class="h-16 bg-slate-800 border-b border-slate-700 flex items-center justify-between px-6">
                <input type="text" placeholder="Search products..." class="w-64 px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg">
                <div class="flex items-center gap-4">
                    <button class="p-2 text-slate-400 hover:bg-slate-700 rounded-lg">🔔</button>
                    <div class="w-8 h-8 bg-blue-500 rounded-full"></div>
                </div>
            </header>
            
            <main class="flex-1 p-6 overflow-auto">
                <div class="flex items-center justify-between mb-6">
                    <h2 class="text-2xl font-bold text-white">Products</h2>
                    <button class="px-4 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg flex items-center gap-2">
                        <span>+</span> Add Product
                    </button>
                </div>
                
                <!-- Filters -->
                <div class="flex gap-4 mb-6">
                    <select class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg">
                        <option>All Categories</option>
                        <option>Electronics</option>
                        <option>Clothing</option>
                        <option>Home</option>
                    </select>
                    <select class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg">
                        <option>All Status</option>
                        <option>In Stock</option>
                        <option>Low Stock</option>
                        <option>Out of Stock</option>
                    </select>
                    <select class="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg">
                        <option>Sort by: Newest</option>
                        <option>Price: Low to High</option>
                        <option>Price: High to Low</option>
                    </select>
                </div>
                
                <!-- Products Table -->
                <div class="bg-slate-800 rounded-xl border border-slate-700">
                    <table class="w-full">
                        <thead>
                            <tr class="text-left text-slate-400 text-sm border-b border-slate-700">
                                <th class="px-6 py-4"><input type="checkbox" class="rounded"></th>
                                <th class="px-6 py-4">Product</th>
                                <th class="px-6 py-4">SKU</th>
                                <th class="px-6 py-4">Category</th>
                                <th class="px-6 py-4">Price</th>
                                <th class="px-6 py-4">Stock</th>
                                <th class="px-6 py-4">Status</th>
                                <th class="px-6 py-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-700">
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4"><input type="checkbox" class="rounded"></td>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-12 h-12 bg-slate-600 rounded-lg"></div>
                                        <span class="text-white">MacBook Pro 16"</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4">SKU-001</td>
                                <td class="px-6 py-4">Electronics</td>
                                <td class="px-6 py-4 text-white">$2,499</td>
                                <td class="px-6 py-4">45</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm">In Stock</span></td>
                                <td class="px-6 py-4">
                                    <button class="text-blue-400 hover:underline mr-3">Edit</button>
                                    <button class="text-red-400 hover:underline">Delete</button>
                                </td>
                            </tr>
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4"><input type="checkbox" class="rounded"></td>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-12 h-12 bg-slate-600 rounded-lg"></div>
                                        <span class="text-white">iPhone 15 Pro</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4">SKU-002</td>
                                <td class="px-6 py-4">Electronics</td>
                                <td class="px-6 py-4 text-white">$1,199</td>
                                <td class="px-6 py-4">8</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-sm">Low Stock</span></td>
                                <td class="px-6 py-4">
                                    <button class="text-blue-400 hover:underline mr-3">Edit</button>
                                    <button class="text-red-400 hover:underline">Delete</button>
                                </td>
                            </tr>
                            <tr class="hover:bg-slate-700/50">
                                <td class="px-6 py-4"><input type="checkbox" class="rounded"></td>
                                <td class="px-6 py-4">
                                    <div class="flex items-center gap-3">
                                        <div class="w-12 h-12 bg-slate-600 rounded-lg"></div>
                                        <span class="text-white">AirPods Max</span>
                                    </div>
                                </td>
                                <td class="px-6 py-4">SKU-003</td>
                                <td class="px-6 py-4">Electronics</td>
                                <td class="px-6 py-4 text-white">$549</td>
                                <td class="px-6 py-4">0</td>
                                <td class="px-6 py-4"><span class="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm">Out of Stock</span></td>
                                <td class="px-6 py-4">
                                    <button class="text-blue-400 hover:underline mr-3">Edit</button>
                                    <button class="text-red-400 hover:underline">Delete</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <!-- Pagination -->
                    <div class="flex items-center justify-between px-6 py-4 border-t border-slate-700">
                        <span class="text-slate-400 text-sm">Showing 1-10 of 156 products</span>
                        <div class="flex gap-2">
                            <button class="px-3 py-1 bg-slate-700 rounded hover:bg-slate-600">Previous</button>
                            <button class="px-3 py-1 bg-blue-500 rounded text-white">1</button>
                            <button class="px-3 py-1 bg-slate-700 rounded hover:bg-slate-600">2</button>
                            <button class="px-3 py-1 bg-slate-700 rounded hover:bg-slate-600">3</button>
                            <button class="px-3 py-1 bg-slate-700 rounded hover:bg-slate-600">Next</button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    </div>
</body>
</html>`,
      component_ts: `import { Component, OnInit, signal, computed, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatSortModule, MatSort, Sort } from '@angular/material/sort';
import { MatPaginatorModule, MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatCheckboxModule } from '@angular/material/checkbox';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { SelectionModel } from '@angular/cdk/collections';

interface Product {
  id: string;
  name: string;
  sku: string;
  category: string;
  price: number;
  stock: number;
  status: 'in-stock' | 'low-stock' | 'out-of-stock';
  image?: string;
}

@Component({
  selector: 'app-products-list',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatTableModule,
    MatSortModule,
    MatPaginatorModule,
    MatCheckboxModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule
  ],
  templateUrl: './products-list.component.html',
  styleUrls: ['./products-list.component.scss']
})
export class ProductsListComponent implements OnInit {
  @ViewChild(MatSort) sort!: MatSort;
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  displayedColumns = ['select', 'product', 'sku', 'category', 'price', 'stock', 'status', 'actions'];
  dataSource = new MatTableDataSource<Product>();
  selection = new SelectionModel<Product>(true, []);

  // Filters
  searchQuery = signal('');
  selectedCategory = signal('all');
  selectedStatus = signal('all');
  
  categories = ['all', 'Electronics', 'Clothing', 'Home'];
  statuses = ['all', 'in-stock', 'low-stock', 'out-of-stock'];

  isLoading = signal(false);
  totalProducts = signal(156);

  ngOnInit(): void {
    this.loadProducts();
  }

  ngAfterViewInit(): void {
    this.dataSource.sort = this.sort;
    this.dataSource.paginator = this.paginator;
  }

  async loadProducts(): Promise<void> {
    this.isLoading.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      
      this.dataSource.data = [
        { id: '1', name: 'MacBook Pro 16"', sku: 'SKU-001', category: 'Electronics', price: 2499, stock: 45, status: 'in-stock' },
        { id: '2', name: 'iPhone 15 Pro', sku: 'SKU-002', category: 'Electronics', price: 1199, stock: 8, status: 'low-stock' },
        { id: '3', name: 'AirPods Max', sku: 'SKU-003', category: 'Electronics', price: 549, stock: 0, status: 'out-of-stock' }
      ];
    } finally {
      this.isLoading.set(false);
    }
  }

  applyFilter(): void {
    this.dataSource.filter = this.searchQuery().trim().toLowerCase();
  }

  isAllSelected(): boolean {
    const numSelected = this.selection.selected.length;
    const numRows = this.dataSource.data.length;
    return numSelected === numRows;
  }

  toggleAllRows(): void {
    if (this.isAllSelected()) {
      this.selection.clear();
      return;
    }
    this.selection.select(...this.dataSource.data);
  }

  getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      'in-stock': 'status-in-stock',
      'low-stock': 'status-low-stock',
      'out-of-stock': 'status-out-of-stock'
    };
    return classes[status] || '';
  }

  editProduct(product: Product): void {
    console.log('Edit product:', product.id);
  }

  deleteProduct(product: Product): void {
    console.log('Delete product:', product.id);
  }

  addProduct(): void {
    console.log('Add new product');
  }
}`,
      component_html: `<div class="products-container">
  <!-- Page Header -->
  <header class="page-header">
    <h1>Products</h1>
    <button mat-raised-button color="primary" (click)="addProduct()">
      <mat-icon>add</mat-icon>
      Add Product
    </button>
  </header>

  <!-- Filters Card -->
  <mat-card class="filters-card">
    <mat-card-content>
      <div class="filters-row">
        <mat-form-field appearance="outline" class="search-field">
          <mat-label>Search products</mat-label>
          <input matInput [ngModel]="searchQuery()" (ngModelChange)="searchQuery.set($event); applyFilter()">
          <mat-icon matPrefix>search</mat-icon>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Category</mat-label>
          <mat-select [value]="selectedCategory()" (selectionChange)="selectedCategory.set($event.value)">
            @for (cat of categories; track cat) {
              <mat-option [value]="cat">{{ cat === 'all' ? 'All Categories' : cat }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>Status</mat-label>
          <mat-select [value]="selectedStatus()" (selectionChange)="selectedStatus.set($event.value)">
            @for (status of statuses; track status) {
              <mat-option [value]="status">{{ status === 'all' ? 'All Status' : status }}</mat-option>
            }
          </mat-select>
        </mat-form-field>
      </div>
    </mat-card-content>
  </mat-card>

  <!-- Products Table -->
  <mat-card class="table-card">
    <mat-card-content>
      <table mat-table [dataSource]="dataSource" matSort>
        <!-- Checkbox Column -->
        <ng-container matColumnDef="select">
          <th mat-header-cell *matHeaderCellDef>
            <mat-checkbox (change)="toggleAllRows()"
                          [checked]="selection.hasValue() && isAllSelected()"
                          [indeterminate]="selection.hasValue() && !isAllSelected()">
            </mat-checkbox>
          </th>
          <td mat-cell *matCellDef="let row">
            <mat-checkbox (click)="$event.stopPropagation()"
                          (change)="selection.toggle(row)"
                          [checked]="selection.isSelected(row)">
            </mat-checkbox>
          </td>
        </ng-container>

        <!-- Product Column -->
        <ng-container matColumnDef="product">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Product</th>
          <td mat-cell *matCellDef="let product">
            <div class="product-cell">
              <div class="product-image"></div>
              <span class="product-name">{{ product.name }}</span>
            </div>
          </td>
        </ng-container>

        <!-- SKU Column -->
        <ng-container matColumnDef="sku">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>SKU</th>
          <td mat-cell *matCellDef="let product">{{ product.sku }}</td>
        </ng-container>

        <!-- Category Column -->
        <ng-container matColumnDef="category">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Category</th>
          <td mat-cell *matCellDef="let product">{{ product.category }}</td>
        </ng-container>

        <!-- Price Column -->
        <ng-container matColumnDef="price">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Price</th>
          <td mat-cell *matCellDef="let product">\${{ product.price | number }}</td>
        </ng-container>

        <!-- Stock Column -->
        <ng-container matColumnDef="stock">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Stock</th>
          <td mat-cell *matCellDef="let product">{{ product.stock }}</td>
        </ng-container>

        <!-- Status Column -->
        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef mat-sort-header>Status</th>
          <td mat-cell *matCellDef="let product">
            <span class="status-badge" [class]="getStatusClass(product.status)">
              {{ product.status }}
            </span>
          </td>
        </ng-container>

        <!-- Actions Column -->
        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>Actions</th>
          <td mat-cell *matCellDef="let product">
            <button mat-button color="primary" (click)="editProduct(product)">Edit</button>
            <button mat-button color="warn" (click)="deleteProduct(product)">Delete</button>
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <mat-paginator [length]="totalProducts()"
                     [pageSize]="10"
                     [pageSizeOptions]="[5, 10, 25, 50]"
                     showFirstLastButtons>
      </mat-paginator>
    </mat-card-content>
  </mat-card>
</div>`,
      component_scss: `.products-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;

  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

// Filters
.filters-card {
  margin-bottom: 24px;

  .filters-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;

    .search-field {
      flex: 1;
      min-width: 250px;
    }

    mat-form-field {
      min-width: 150px;
    }
  }
}

// Table
.table-card {
  table {
    width: 100%;
  }

  .product-cell {
    display: flex;
    align-items: center;
    gap: 12px;

    .product-image {
      width: 48px;
      height: 48px;
      background: #e2e8f0;
      border-radius: 8px;
    }

    .product-name {
      font-weight: 500;
      color: #1e293b;
    }
  }

  .status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;

    &.status-in-stock {
      background: rgba(16, 185, 129, 0.1);
      color: #10b981;
    }

    &.status-low-stock {
      background: rgba(245, 158, 11, 0.1);
      color: #f59e0b;
    }

    &.status-out-of-stock {
      background: rgba(239, 68, 68, 0.1);
      color: #ef4444;
    }
  }
}

mat-paginator {
  border-top: 1px solid #e2e8f0;
}`
    },
    {
      id: 'order-history',
      name: 'Order History',
      type: 'list',
      description: 'Customer order history with tracking and return management',
      related_features: ['Order Management & Tracking'],
      related_stories: ['Order History', 'Shipment Tracking', 'Return Request', 'Order Notifications'],
      functionality: ['View order history', 'Track shipments', 'Request returns', 'Download invoices'],
      ui_elements: ['Orders table', 'Status filters', 'Date range picker', 'Track button', 'Return button'],
      data_displayed: ['Order ID', 'Date', 'Items', 'Total', 'Status', 'Tracking number'],
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Order History</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; color: #333; line-height: 1.5; }
        .wireframe-container { display: flex; min-height: 100vh; }
        .wireframe-sidebar { width: 220px; min-width: 220px; background: #fff; border-right: 2px solid #ddd; padding: 20px; }
        .wireframe-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
        .wireframe-header { background: #fff; border-bottom: 2px solid #ddd; padding: 15px 20px; }
        .wireframe-content { flex: 1; padding: 20px; background: #f5f5f5; overflow-x: auto; }
        .wf-card { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 15px; margin-bottom: 15px; }
        .wf-btn { display: inline-block; padding: 8px 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 4px; color: #333; cursor: pointer; }
        .wf-btn-primary { background: #666; color: #fff; border-color: #555; }
        .wf-heading { color: #333; margin-bottom: 10px; }
        .flex { display: flex; flex-wrap: wrap; }
        .gap-10 { gap: 10px; }
        .table-wrapper { width: 100%; overflow-x: auto; }
        table { width: 100%; min-width: 600px; border-collapse: collapse; background: #fff; }
        th { text-align: left; padding: 10px; background: #f5f5f5; border: 1px solid #ddd; font-size: 11px; text-transform: uppercase; color: #666; }
        td { padding: 10px; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <div class="wireframe-container">
        <aside class="wireframe-sidebar">
            <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">
                <div style="font-weight: bold; font-size: 18px;">E-Commerce</div>
            </div>
            <nav>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Dashboard</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Products</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; background: #e8e8e8; color: #333; font-weight: 500;">Order History</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Cart</div>
            </nav>
        </aside>
        <div class="wireframe-main">
            <header class="wireframe-header">
                <div class="flex" style="justify-content: space-between; align-items: center;">
                    <h2 class="wf-heading" style="margin: 0;">My Orders</h2>
                    <div style="width: 40px; height: 40px; background: #ddd; border-radius: 50%;"></div>
                </div>
            </header>
            <div class="wireframe-content">
                <div class="wf-card">
                    <div class="flex gap-10" style="flex-wrap: wrap; margin-bottom: 15px;">
                        <select style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                            <option>All Status</option>
                            <option>Processing</option>
                            <option>Shipped</option>
                            <option>Delivered</option>
                        </select>
                        <input type="date" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                        <input type="date" style="padding: 8px; border: 1px solid #ccc; border-radius: 4px;">
                    </div>
                </div>
                <div class="table-wrapper">
                    <table>
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Date</th>
                                <th>Items</th>
                                <th>Total</th>
                                <th>Status</th>
                                <th>Tracking</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td>#ORD-1234</td>
                                <td>Dec 5, 2024</td>
                                <td>3 items</td>
                                <td>$249.99</td>
                                <td><span style="background:#e8f5e9;color:#2e7d32;padding:3px 8px;border-radius:12px;font-size:12px;">Delivered</span></td>
                                <td>TRACK123456</td>
                                <td><a href="#" style="color:#1976d2;">Details</a> | <a href="#" style="color:#1976d2;">Return</a></td>
                            </tr>
                            <tr>
                                <td>#ORD-1233</td>
                                <td>Dec 3, 2024</td>
                                <td>1 item</td>
                                <td>$89.99</td>
                                <td><span style="background:#e3f2fd;color:#1565c0;padding:3px 8px;border-radius:12px;font-size:12px;">Shipped</span></td>
                                <td>TRACK123457</td>
                                <td><a href="#" style="color:#1976d2;">Track</a> | <a href="#" style="color:#1976d2;">Details</a></td>
                            </tr>
                            <tr>
                                <td>#ORD-1232</td>
                                <td>Dec 1, 2024</td>
                                <td>2 items</td>
                                <td>$159.99</td>
                                <td><span style="background:#fff3e0;color:#ef6c00;padding:3px 8px;border-radius:12px;font-size:12px;">Processing</span></td>
                                <td>--</td>
                                <td><a href="#" style="color:#1976d2;">Details</a></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: #666; font-size: 14px;">Showing 1-10 of 25 orders</span>
                    <div>
                        <button class="wf-btn">Previous</button>
                        <button class="wf-btn wf-btn-primary" style="margin: 0 5px;">1</button>
                        <button class="wf-btn">2</button>
                        <button class="wf-btn">3</button>
                        <button class="wf-btn">Next</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>`,
      component_ts: `import { Component, OnInit, signal, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTableModule, MatTableDataSource } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator } from '@angular/material/paginator';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';

interface Order {
  id: string;
  date: Date;
  itemCount: number;
  total: number;
  status: 'processing' | 'shipped' | 'delivered' | 'returned';
  trackingNumber?: string;
}

@Component({
  selector: 'app-order-history',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatTableModule, MatPaginatorModule, MatSelectModule, MatFormFieldModule,
    MatDatepickerModule, MatNativeDateModule
  ],
  templateUrl: './order-history.component.html',
  styleUrls: ['./order-history.component.scss']
})
export class OrderHistoryComponent implements OnInit {
  @ViewChild(MatPaginator) paginator!: MatPaginator;

  displayedColumns = ['id', 'date', 'items', 'total', 'status', 'tracking', 'actions'];
  dataSource = new MatTableDataSource<Order>();

  // Filters
  selectedStatus = signal('all');
  startDate = signal<Date | null>(null);
  endDate = signal<Date | null>(null);
  
  statuses = ['all', 'processing', 'shipped', 'delivered', 'returned'];
  isLoading = signal(false);
  totalOrders = signal(25);

  ngOnInit(): void {
    this.loadOrders();
  }

  ngAfterViewInit(): void {
    this.dataSource.paginator = this.paginator;
  }

  async loadOrders(): Promise<void> {
    this.isLoading.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      this.dataSource.data = [
        { id: '#ORD-1234', date: new Date('2024-12-05'), itemCount: 3, total: 249.99, status: 'delivered', trackingNumber: 'TRACK123456' },
        { id: '#ORD-1233', date: new Date('2024-12-03'), itemCount: 1, total: 89.99, status: 'shipped', trackingNumber: 'TRACK123457' },
        { id: '#ORD-1232', date: new Date('2024-12-01'), itemCount: 2, total: 159.99, status: 'processing' }
      ];
    } finally {
      this.isLoading.set(false);
    }
  }

  trackOrder(order: Order): void {
    console.log('Track order:', order.id);
    window.open(\`https://tracking.example.com/\${order.trackingNumber}\`, '_blank');
  }

  viewOrderDetails(order: Order): void {
    console.log('View order details:', order.id);
  }

  requestReturn(order: Order): void {
    console.log('Request return for:', order.id);
  }

  downloadInvoice(order: Order): void {
    console.log('Download invoice for:', order.id);
  }

  getStatusClass(status: string): string {
    const classes: Record<string, string> = {
      'processing': 'status-processing',
      'shipped': 'status-shipped',
      'delivered': 'status-delivered',
      'returned': 'status-returned'
    };
    return classes[status] || '';
  }
}`,
      component_html: `<div class="order-history-container">
  <header class="page-header">
    <h1>My Orders</h1>
  </header>

  <!-- Filters -->
  <mat-card class="filters-card">
    <mat-card-content>
      <div class="filters-row">
        <mat-form-field appearance="outline">
          <mat-label>Status</mat-label>
          <mat-select [value]="selectedStatus()" (selectionChange)="selectedStatus.set($event.value)">
            @for (status of statuses; track status) {
              <mat-option [value]="status">{{ status === 'all' ? 'All Status' : status }}</mat-option>
            }
          </mat-select>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>From Date</mat-label>
          <input matInput [matDatepicker]="startPicker" [ngModel]="startDate()" (ngModelChange)="startDate.set($event)">
          <mat-datepicker-toggle matSuffix [for]="startPicker"></mat-datepicker-toggle>
          <mat-datepicker #startPicker></mat-datepicker>
        </mat-form-field>

        <mat-form-field appearance="outline">
          <mat-label>To Date</mat-label>
          <input matInput [matDatepicker]="endPicker" [ngModel]="endDate()" (ngModelChange)="endDate.set($event)">
          <mat-datepicker-toggle matSuffix [for]="endPicker"></mat-datepicker-toggle>
          <mat-datepicker #endPicker></mat-datepicker>
        </mat-form-field>
      </div>
    </mat-card-content>
  </mat-card>

  <!-- Orders Table -->
  <mat-card class="table-card">
    <mat-card-content>
      <table mat-table [dataSource]="dataSource">
        <ng-container matColumnDef="id">
          <th mat-header-cell *matHeaderCellDef>Order ID</th>
          <td mat-cell *matCellDef="let order">{{ order.id }}</td>
        </ng-container>

        <ng-container matColumnDef="date">
          <th mat-header-cell *matHeaderCellDef>Date</th>
          <td mat-cell *matCellDef="let order">{{ order.date | date:'mediumDate' }}</td>
        </ng-container>

        <ng-container matColumnDef="items">
          <th mat-header-cell *matHeaderCellDef>Items</th>
          <td mat-cell *matCellDef="let order">{{ order.itemCount }} items</td>
        </ng-container>

        <ng-container matColumnDef="total">
          <th mat-header-cell *matHeaderCellDef>Total</th>
          <td mat-cell *matCellDef="let order">\${{ order.total | number:'1.2-2' }}</td>
        </ng-container>

        <ng-container matColumnDef="status">
          <th mat-header-cell *matHeaderCellDef>Status</th>
          <td mat-cell *matCellDef="let order">
            <span class="status-badge" [class]="getStatusClass(order.status)">{{ order.status }}</span>
          </td>
        </ng-container>

        <ng-container matColumnDef="tracking">
          <th mat-header-cell *matHeaderCellDef>Tracking</th>
          <td mat-cell *matCellDef="let order">{{ order.trackingNumber || '--' }}</td>
        </ng-container>

        <ng-container matColumnDef="actions">
          <th mat-header-cell *matHeaderCellDef>Actions</th>
          <td mat-cell *matCellDef="let order">
            <button mat-button color="primary" (click)="viewOrderDetails(order)">Details</button>
            @if (order.status === 'shipped') {
              <button mat-button color="accent" (click)="trackOrder(order)">Track</button>
            }
            @if (order.status === 'delivered') {
              <button mat-button color="warn" (click)="requestReturn(order)">Return</button>
            }
          </td>
        </ng-container>

        <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
        <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
      </table>

      <mat-paginator [length]="totalOrders()" [pageSize]="10" [pageSizeOptions]="[5, 10, 25]" showFirstLastButtons>
      </mat-paginator>
    </mat-card-content>
  </mat-card>
</div>`,
      component_scss: `.order-history-container {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;
  h1 {
    font-size: 28px;
    font-weight: 600;
    color: #1e293b;
    margin: 0;
  }
}

.filters-card {
  margin-bottom: 24px;
  .filters-row {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    mat-form-field { min-width: 150px; }
  }
}

.table-card {
  table { width: 100%; }
  
  .status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    text-transform: capitalize;

    &.status-processing { background: rgba(245, 158, 11, 0.1); color: #f59e0b; }
    &.status-shipped { background: rgba(59, 130, 246, 0.1); color: #3b82f6; }
    &.status-delivered { background: rgba(16, 185, 129, 0.1); color: #10b981; }
    &.status-returned { background: rgba(239, 68, 68, 0.1); color: #ef4444; }
  }
}`
    },
    {
      id: 'shopping-cart',
      name: 'Shopping Cart',
      type: 'form',
      description: 'Shopping cart with item management and checkout initiation',
      related_features: ['Shopping Cart & Checkout'],
      related_stories: ['Add to Cart', 'Cart Management', 'Apply Coupon'],
      functionality: ['View cart items', 'Update quantities', 'Remove items', 'Apply coupon codes', 'Proceed to checkout'],
      ui_elements: ['Cart items list', 'Quantity controls', 'Remove button', 'Coupon input', 'Order summary', 'Checkout button'],
      data_displayed: ['Product image', 'Product name', 'Unit price', 'Quantity', 'Subtotal'],
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopping Cart</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; color: #333; line-height: 1.5; }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
        .wf-card { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 15px; }
        .wf-btn { display: inline-block; padding: 8px 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; }
        .wf-btn-primary { background: #666; color: #fff; border-color: #555; }
        .wf-input { padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; }
        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div style="background: #fff; padding: 15px 20px; border-bottom: 2px solid #ddd;">
        <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center;">
            <h1 style="font-size: 20px;">Shopping Cart (3 items)</h1>
            <a href="#" style="color: #555;">Continue Shopping</a>
        </div>
    </div>
    <div class="container">
        <div>
            <div class="wf-card" style="margin-bottom: 15px;">
                <div style="display: flex; gap: 15px; padding-bottom: 15px; border-bottom: 1px solid #eee;">
                    <div style="width: 80px; height: 80px; background: #e5e5e5; border-radius: 4px;"></div>
                    <div style="flex: 1;">
                        <h3 style="font-size: 16px; margin-bottom: 5px;">MacBook Pro 16"</h3>
                        <p style="color: #666; font-size: 14px;">Color: Space Gray</p>
                        <p style="font-weight: bold; margin-top: 10px;">$2,499.00</p>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <button class="wf-btn" style="padding: 5px 10px;">-</button>
                            <input type="number" value="1" style="width: 50px; text-align: center; padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
                            <button class="wf-btn" style="padding: 5px 10px;">+</button>
                        </div>
                        <button style="color: #d32f2f; background: none; border: none; cursor: pointer;">Remove</button>
                    </div>
                </div>
            </div>
            <div class="wf-card" style="margin-bottom: 15px;">
                <div style="display: flex; gap: 15px;">
                    <div style="width: 80px; height: 80px; background: #e5e5e5; border-radius: 4px;"></div>
                    <div style="flex: 1;">
                        <h3 style="font-size: 16px; margin-bottom: 5px;">iPhone 15 Pro</h3>
                        <p style="color: #666; font-size: 14px;">256GB - Natural Titanium</p>
                        <p style="font-weight: bold; margin-top: 10px;">$1,199.00</p>
                    </div>
                    <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 10px;">
                        <div style="display: flex; align-items: center; gap: 5px;">
                            <button class="wf-btn" style="padding: 5px 10px;">-</button>
                            <input type="number" value="2" style="width: 50px; text-align: center; padding: 5px; border: 1px solid #ccc; border-radius: 4px;">
                            <button class="wf-btn" style="padding: 5px 10px;">+</button>
                        </div>
                        <button style="color: #d32f2f; background: none; border: none; cursor: pointer;">Remove</button>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <div class="wf-card">
                <h3 style="margin-bottom: 15px; font-size: 18px;">Order Summary</h3>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Subtotal</span><span>$4,897.00</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span>Shipping</span><span>FREE</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 15px;">
                    <span>Tax</span><span>$392.00</span>
                </div>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                    <input type="text" placeholder="Coupon code" class="wf-input" style="flex: 1;">
                    <button class="wf-btn">Apply</button>
                </div>
                <div style="border-top: 1px solid #ddd; padding-top: 15px; display: flex; justify-content: space-between; font-weight: bold; font-size: 18px;">
                    <span>Total</span><span>$5,289.00</span>
                </div>
                <button class="wf-btn wf-btn-primary" style="width: 100%; margin-top: 15px; padding: 12px;">Proceed to Checkout</button>
            </div>
        </div>
    </div>
</body>
</html>`,
      component_ts: `import { Component, OnInit, signal, computed } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatDividerModule } from '@angular/material/divider';

interface CartItem {
  id: string;
  name: string;
  variant: string;
  price: number;
  quantity: number;
  image?: string;
}

@Component({
  selector: 'app-shopping-cart',
  standalone: true,
  imports: [
    CommonModule, FormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatDividerModule
  ],
  templateUrl: './shopping-cart.component.html',
  styleUrls: ['./shopping-cart.component.scss']
})
export class ShoppingCartComponent implements OnInit {
  cartItems = signal<CartItem[]>([]);
  couponCode = signal('');
  appliedCoupon = signal<string | null>(null);
  discount = signal(0);
  isLoading = signal(false);

  subtotal = computed(() => 
    this.cartItems().reduce((sum, item) => sum + (item.price * item.quantity), 0)
  );

  tax = computed(() => this.subtotal() * 0.08);
  
  total = computed(() => this.subtotal() + this.tax() - this.discount());

  totalItems = computed(() => 
    this.cartItems().reduce((sum, item) => sum + item.quantity, 0)
  );

  ngOnInit(): void {
    this.loadCart();
  }

  async loadCart(): Promise<void> {
    this.isLoading.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 300));
      this.cartItems.set([
        { id: '1', name: 'MacBook Pro 16"', variant: 'Space Gray', price: 2499, quantity: 1 },
        { id: '2', name: 'iPhone 15 Pro', variant: '256GB - Natural Titanium', price: 1199, quantity: 2 }
      ]);
    } finally {
      this.isLoading.set(false);
    }
  }

  updateQuantity(item: CartItem, delta: number): void {
    const newQuantity = Math.max(1, item.quantity + delta);
    this.cartItems.update(items => 
      items.map(i => i.id === item.id ? { ...i, quantity: newQuantity } : i)
    );
  }

  removeItem(item: CartItem): void {
    this.cartItems.update(items => items.filter(i => i.id !== item.id));
  }

  applyCoupon(): void {
    const code = this.couponCode().trim().toUpperCase();
    if (code === 'SAVE10') {
      this.appliedCoupon.set(code);
      this.discount.set(this.subtotal() * 0.1);
    } else {
      alert('Invalid coupon code');
    }
  }

  removeCoupon(): void {
    this.appliedCoupon.set(null);
    this.discount.set(0);
    this.couponCode.set('');
  }

  proceedToCheckout(): void {
    console.log('Proceeding to checkout with', this.cartItems());
  }
}`,
      component_html: `<div class="cart-container">
  <header class="cart-header">
    <h1>Shopping Cart ({{ totalItems() }} items)</h1>
    <a mat-button routerLink="/products">Continue Shopping</a>
  </header>

  <div class="cart-content">
    <!-- Cart Items -->
    <div class="cart-items">
      @for (item of cartItems(); track item.id) {
        <mat-card class="cart-item-card">
          <div class="cart-item">
            <div class="item-image"></div>
            <div class="item-details">
              <h3>{{ item.name }}</h3>
              <p class="variant">{{ item.variant }}</p>
              <p class="price">\${{ item.price | number:'1.2-2' }}</p>
            </div>
            <div class="item-actions">
              <div class="quantity-controls">
                <button mat-icon-button (click)="updateQuantity(item, -1)" [disabled]="item.quantity <= 1">
                  <mat-icon>remove</mat-icon>
                </button>
                <span class="quantity">{{ item.quantity }}</span>
                <button mat-icon-button (click)="updateQuantity(item, 1)">
                  <mat-icon>add</mat-icon>
                </button>
              </div>
              <button mat-button color="warn" (click)="removeItem(item)">Remove</button>
            </div>
          </div>
        </mat-card>
      }
    </div>

    <!-- Order Summary -->
    <mat-card class="order-summary">
      <mat-card-header>
        <mat-card-title>Order Summary</mat-card-title>
      </mat-card-header>
      <mat-card-content>
        <div class="summary-row">
          <span>Subtotal</span>
          <span>\${{ subtotal() | number:'1.2-2' }}</span>
        </div>
        <div class="summary-row">
          <span>Shipping</span>
          <span class="free">FREE</span>
        </div>
        <div class="summary-row">
          <span>Tax</span>
          <span>\${{ tax() | number:'1.2-2' }}</span>
        </div>
        @if (discount() > 0) {
          <div class="summary-row discount">
            <span>Discount ({{ appliedCoupon() }})</span>
            <span>-\${{ discount() | number:'1.2-2' }}</span>
          </div>
        }

        <mat-divider></mat-divider>

        @if (!appliedCoupon()) {
          <div class="coupon-section">
            <mat-form-field appearance="outline">
              <mat-label>Coupon code</mat-label>
              <input matInput [ngModel]="couponCode()" (ngModelChange)="couponCode.set($event)">
            </mat-form-field>
            <button mat-stroked-button (click)="applyCoupon()">Apply</button>
          </div>
        } @else {
          <div class="applied-coupon">
            <span>{{ appliedCoupon() }} applied</span>
            <button mat-icon-button (click)="removeCoupon()"><mat-icon>close</mat-icon></button>
          </div>
        }

        <div class="summary-row total">
          <span>Total</span>
          <span>\${{ total() | number:'1.2-2' }}</span>
        </div>

        <button mat-raised-button color="primary" class="checkout-btn" (click)="proceedToCheckout()">
          Proceed to Checkout
        </button>
      </mat-card-content>
    </mat-card>
  </div>
</div>`,
      component_scss: `.cart-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  h1 { font-size: 28px; font-weight: 600; margin: 0; }
}

.cart-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.cart-item-card {
  margin-bottom: 16px;
  
  .cart-item {
    display: flex;
    gap: 16px;
    align-items: center;
    
    .item-image {
      width: 80px;
      height: 80px;
      background: #e2e8f0;
      border-radius: 8px;
    }
    
    .item-details {
      flex: 1;
      h3 { font-size: 16px; margin: 0 0 4px; }
      .variant { color: #64748b; font-size: 14px; margin: 0; }
      .price { font-weight: 600; margin: 8px 0 0; }
    }
    
    .item-actions {
      display: flex;
      flex-direction: column;
      align-items: flex-end;
      gap: 8px;
      
      .quantity-controls {
        display: flex;
        align-items: center;
        gap: 8px;
        .quantity { font-weight: 500; min-width: 30px; text-align: center; }
      }
    }
  }
}

.order-summary {
  height: fit-content;
  position: sticky;
  top: 24px;
  
  .summary-row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    &.discount { color: #10b981; }
    &.total { font-size: 18px; font-weight: 600; padding-top: 16px; }
    .free { color: #10b981; font-weight: 500; }
  }
  
  .coupon-section {
    display: flex;
    gap: 8px;
    margin: 16px 0;
    mat-form-field { flex: 1; }
  }
  
  .applied-coupon {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: #f0fdf4;
    padding: 8px 12px;
    border-radius: 8px;
    margin: 16px 0;
    color: #10b981;
  }
  
  .checkout-btn {
    width: 100%;
    margin-top: 16px;
    padding: 12px;
  }
}`
    },
    {
      id: 'user-profile',
      name: 'User Profile',
      type: 'settings',
      description: 'User profile and account settings management',
      related_features: ['User Authentication & Profile Management'],
      related_stories: ['Profile Management', 'Two-Factor Authentication', 'Password Reset'],
      functionality: ['Update profile info', 'Change password', 'Manage 2FA', 'Update preferences', 'Delete account'],
      ui_elements: ['Profile form', 'Avatar upload', 'Password fields', '2FA toggle', 'Save button'],
      data_displayed: ['Full name', 'Email', 'Phone', 'Address', 'Notification preferences'],
      html: `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Profile Settings</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; color: #333; line-height: 1.5; }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; display: grid; grid-template-columns: 200px 1fr; gap: 20px; }
        .wf-card { background: #fff; border: 1px solid #ddd; border-radius: 4px; padding: 20px; }
        .wf-btn { padding: 8px 16px; background: #e0e0e0; border: 1px solid #ccc; border-radius: 4px; cursor: pointer; }
        .wf-btn-primary { background: #666; color: #fff; }
        .wf-input { width: 100%; padding: 8px 12px; border: 1px solid #ccc; border-radius: 4px; margin-top: 5px; }
        .wf-label { font-weight: bold; color: #555; font-size: 14px; display: block; margin-bottom: 5px; }
        @media (max-width: 768px) { .container { grid-template-columns: 1fr; } }
    </style>
</head>
<body>
    <div style="background: #fff; padding: 15px 20px; border-bottom: 2px solid #ddd;">
        <h1 style="font-size: 20px; max-width: 900px; margin: 0 auto;">Account Settings</h1>
    </div>
    <div class="container">
        <div class="wf-card" style="height: fit-content;">
            <nav>
                <div style="padding: 10px; background: #e8e8e8; border-radius: 4px; margin-bottom: 5px; font-weight: 500;">Profile</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Security</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Notifications</div>
                <div style="padding: 10px; border-radius: 4px; margin-bottom: 5px; color: #555;">Privacy</div>
            </nav>
        </div>
        <div>
            <div class="wf-card" style="margin-bottom: 20px;">
                <h2 style="margin-bottom: 20px; font-size: 18px;">Profile Information</h2>
                <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 20px;">
                    <div style="width: 80px; height: 80px; background: #ddd; border-radius: 50%;"></div>
                    <div>
                        <button class="wf-btn">Upload Photo</button>
                        <p style="font-size: 12px; color: #666; margin-top: 5px;">JPG or PNG, max 2MB</p>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                    <div>
                        <label class="wf-label">First Name</label>
                        <input type="text" value="John" class="wf-input">
                    </div>
                    <div>
                        <label class="wf-label">Last Name</label>
                        <input type="text" value="Smith" class="wf-input">
                    </div>
                    <div style="grid-column: span 2;">
                        <label class="wf-label">Email</label>
                        <input type="email" value="john.smith@example.com" class="wf-input">
                    </div>
                    <div style="grid-column: span 2;">
                        <label class="wf-label">Phone</label>
                        <input type="tel" value="+1 (555) 123-4567" class="wf-input">
                    </div>
                </div>
            </div>
            <div class="wf-card" style="margin-bottom: 20px;">
                <h2 style="margin-bottom: 15px; font-size: 18px;">Security</h2>
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee;">
                    <div>
                        <strong>Two-Factor Authentication</strong>
                        <p style="font-size: 12px; color: #666;">Add an extra layer of security</p>
                    </div>
                    <div style="width: 50px; height: 28px; background: #4caf50; border-radius: 14px; position: relative;">
                        <div style="width: 24px; height: 24px; background: #fff; border-radius: 50%; position: absolute; right: 2px; top: 2px;"></div>
                    </div>
                </div>
                <div style="padding: 10px 0;">
                    <button class="wf-btn">Change Password</button>
                </div>
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 10px;">
                <button class="wf-btn">Cancel</button>
                <button class="wf-btn wf-btn-primary">Save Changes</button>
            </div>
        </div>
    </div>
</body>
</html>`,
      component_ts: `import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';

interface UserProfile {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  twoFactorEnabled: boolean;
}

@Component({
  selector: 'app-user-profile',
  standalone: true,
  imports: [
    CommonModule, ReactiveFormsModule, MatCardModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatSlideToggleModule, MatSnackBarModule, MatTabsModule
  ],
  templateUrl: './user-profile.component.html',
  styleUrls: ['./user-profile.component.scss']
})
export class UserProfileComponent implements OnInit {
  profileForm!: FormGroup;
  passwordForm!: FormGroup;
  
  isLoading = signal(false);
  isSaving = signal(false);
  twoFactorEnabled = signal(true);
  selectedTab = signal(0);

  constructor(private fb: FormBuilder, private snackBar: MatSnackBar) {}

  ngOnInit(): void {
    this.initForms();
    this.loadProfile();
  }

  initForms(): void {
    this.profileForm = this.fb.group({
      firstName: ['', Validators.required],
      lastName: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: ['']
    });

    this.passwordForm = this.fb.group({
      currentPassword: ['', Validators.required],
      newPassword: ['', [Validators.required, Validators.minLength(8)]],
      confirmPassword: ['', Validators.required]
    });
  }

  async loadProfile(): Promise<void> {
    this.isLoading.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 500));
      this.profileForm.patchValue({
        firstName: 'John',
        lastName: 'Smith',
        email: 'john.smith@example.com',
        phone: '+1 (555) 123-4567'
      });
    } finally {
      this.isLoading.set(false);
    }
  }

  async saveProfile(): Promise<void> {
    if (this.profileForm.invalid) return;
    
    this.isSaving.set(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      this.snackBar.open('Profile updated successfully', 'Close', { duration: 3000 });
    } finally {
      this.isSaving.set(false);
    }
  }

  toggle2FA(): void {
    this.twoFactorEnabled.update(v => !v);
    const status = this.twoFactorEnabled() ? 'enabled' : 'disabled';
    this.snackBar.open(\`Two-factor authentication \${status}\`, 'Close', { duration: 3000 });
  }

  uploadAvatar(event: Event): void {
    const input = event.target as HTMLInputElement;
    if (input.files?.length) {
      console.log('Uploading avatar:', input.files[0].name);
    }
  }

  changePassword(): void {
    if (this.passwordForm.invalid) return;
    console.log('Changing password');
  }
}`,
      component_html: `<div class="profile-container">
  <header class="page-header">
    <h1>Account Settings</h1>
  </header>

  <div class="profile-content">
    <!-- Settings Navigation -->
    <mat-card class="settings-nav">
      <nav>
        <button mat-button [class.active]="selectedTab() === 0" (click)="selectedTab.set(0)">
          <mat-icon>person</mat-icon> Profile
        </button>
        <button mat-button [class.active]="selectedTab() === 1" (click)="selectedTab.set(1)">
          <mat-icon>security</mat-icon> Security
        </button>
        <button mat-button [class.active]="selectedTab() === 2" (click)="selectedTab.set(2)">
          <mat-icon>notifications</mat-icon> Notifications
        </button>
      </nav>
    </mat-card>

    <!-- Settings Content -->
    <div class="settings-content">
      @if (selectedTab() === 0) {
        <mat-card>
          <mat-card-header>
            <mat-card-title>Profile Information</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="avatar-section">
              <div class="avatar"></div>
              <div>
                <input type="file" #fileInput hidden accept="image/*" (change)="uploadAvatar($event)">
                <button mat-stroked-button (click)="fileInput.click()">Upload Photo</button>
                <p class="hint">JPG or PNG, max 2MB</p>
              </div>
            </div>

            <form [formGroup]="profileForm" class="profile-form">
              <div class="form-row">
                <mat-form-field appearance="outline">
                  <mat-label>First Name</mat-label>
                  <input matInput formControlName="firstName">
                </mat-form-field>
                <mat-form-field appearance="outline">
                  <mat-label>Last Name</mat-label>
                  <input matInput formControlName="lastName">
                </mat-form-field>
              </div>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Email</mat-label>
                <input matInput formControlName="email" type="email">
              </mat-form-field>
              <mat-form-field appearance="outline" class="full-width">
                <mat-label>Phone</mat-label>
                <input matInput formControlName="phone" type="tel">
              </mat-form-field>
            </form>
          </mat-card-content>
        </mat-card>
      }

      @if (selectedTab() === 1) {
        <mat-card>
          <mat-card-header>
            <mat-card-title>Security Settings</mat-card-title>
          </mat-card-header>
          <mat-card-content>
            <div class="security-option">
              <div>
                <strong>Two-Factor Authentication</strong>
                <p>Add an extra layer of security to your account</p>
              </div>
              <mat-slide-toggle [checked]="twoFactorEnabled()" (change)="toggle2FA()"></mat-slide-toggle>
            </div>
            <mat-divider></mat-divider>
            <div class="security-option">
              <div>
                <strong>Change Password</strong>
                <p>Update your password regularly for security</p>
              </div>
              <button mat-stroked-button>Change</button>
            </div>
          </mat-card-content>
        </mat-card>
      }

      <!-- Action Buttons -->
      <div class="actions">
        <button mat-button>Cancel</button>
        <button mat-raised-button color="primary" (click)="saveProfile()" [disabled]="isSaving()">
          @if (isSaving()) { Saving... } @else { Save Changes }
        </button>
      </div>
    </div>
  </div>
</div>`,
      component_scss: `.profile-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
  h1 { font-size: 28px; font-weight: 600; margin: 0; }
}

.profile-content {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 24px;
  @media (max-width: 768px) { grid-template-columns: 1fr; }
}

.settings-nav {
  height: fit-content;
  nav {
    display: flex;
    flex-direction: column;
    button {
      justify-content: flex-start;
      padding: 12px 16px;
      mat-icon { margin-right: 12px; }
      &.active { background: #e3f2fd; color: #1976d2; }
    }
  }
}

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 20px;

  .avatar-section {
    display: flex;
    align-items: center;
    gap: 20px;
    margin-bottom: 24px;
    
    .avatar {
      width: 80px;
      height: 80px;
      background: #e2e8f0;
      border-radius: 50%;
    }
    .hint { font-size: 12px; color: #64748b; margin-top: 4px; }
  }

  .profile-form {
    .form-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 16px;
    }
    .full-width { width: 100%; }
  }

  .security-option {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 0;
    p { font-size: 14px; color: #64748b; margin: 4px 0 0; }
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}`
    }
  ],
  shared_components: {
    sidebar: '<aside>Sidebar Component</aside>',
    header: '<header>Header Component</header>'
  },
  plan: {
    pages: [
      { id: 'dashboard', name: 'Admin Dashboard', type: 'dashboard', related_features: ['Admin Dashboard & Inventory', 'Order Management & Tracking'], functionality: ['View key metrics', 'Monitor sales'] },
      { id: 'products-list', name: 'Product Catalog', type: 'list', related_features: ['Product Catalog & Search', 'Admin Dashboard & Inventory'], functionality: ['Search products', 'Manage inventory'] },
      { id: 'order-history', name: 'Order History', type: 'list', related_features: ['Order Management & Tracking'], functionality: ['View orders', 'Track shipments'] },
      { id: 'shopping-cart', name: 'Shopping Cart', type: 'form', related_features: ['Shopping Cart & Checkout'], functionality: ['Manage cart', 'Apply coupons'] },
      { id: 'user-profile', name: 'User Profile', type: 'settings', related_features: ['User Authentication & Profile Management'], functionality: ['Update profile', 'Manage security'] }
    ],
    navigation: {
      sidebar_items: ['Dashboard', 'Products', 'Orders', 'Cart', 'Profile', 'Settings']
    },
    theme: {
      primary_color: '#3b82f6',
      secondary_color: '#1e293b',
      background: '#f5f5f5',
      text_color: '#333',
      accent_color: '#60a5fa'
    }
  },
  metadata: {
    total_pages: 5,
    generation_time: 12
  }
};
