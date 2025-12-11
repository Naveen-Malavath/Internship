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

// Mock Wireframe Pages Data - 2 pages for testing
export const MOCK_WIREFRAME_DATA = {
  pages: [
    {
      id: 'dashboard',
      name: 'Dashboard',
      type: 'dashboard',
      description: 'Main admin dashboard with KPIs and analytics',
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
</html>`
    },
    {
      id: 'products-list',
      name: 'Products',
      type: 'list',
      description: 'Product catalog with search and filters',
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
</html>`
    }
  ],
  shared_components: {
    sidebar: '<aside>Sidebar Component</aside>',
    header: '<header>Header Component</header>'
  },
  plan: {
    pages: [
      { id: 'dashboard', name: 'Dashboard', type: 'dashboard' },
      { id: 'products-list', name: 'Products', type: 'list' }
    ],
    navigation: {
      sidebar_items: ['Dashboard', 'Products', 'Orders', 'Customers', 'Settings']
    }
  },
  metadata: {
    total_pages: 2,
    generation_time: 8
  }
};
