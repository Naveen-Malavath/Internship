# 📚 Enterprise Libraries - Quick Reference

## 🎯 TL;DR - Best Choices for Each Category

| Category | Library | Installation | Why? |
|----------|---------|--------------|------|
| **UI Components** | Angular Material | `ng add @angular/material` | Most popular, Google-backed |
| **State Management** | NgRx | `npm install @ngrx/store @ngrx/effects` | Industry standard |
| **Authentication** | Auth0 | `npm install @auth0/auth0-angular` | Easy setup, enterprise features |
| **Real-time** | Socket.io | `npm install socket.io-client` | Most popular WebSocket library |
| **Notifications** | NGX Toastr | `npm install ngx-toastr` | Simple, beautiful toasts |
| **Markdown** | NGX Markdown | `npm install ngx-markdown` | Angular-optimized |
| **Logging** | NGX Logger | `npm install ngx-logger` | Production-ready |
| **Error Tracking** | Sentry | `npm install @sentry/angular` | Best error monitoring |
| **Charts** | Chart.js | `npm install chart.js ng2-charts` | Easy to use |
| **Data Tables** | AG Grid | `npm install ag-grid-angular` | Enterprise-grade |
| **i18n** | NGX Translate | `npm install @ngx-translate/core` | Most popular |
| **Testing** | Cypress | `npm install cypress` | Modern E2E testing |

---

## ⚡ Quick Installation Commands

### Minimal Stack (Start Here)
```bash
ng add @angular/material
npm install ngx-toastr @angular/animations ngx-markdown @sentry/angular
```

### Standard Stack (Recommended)
```bash
ng add @angular/material
npm install @ngrx/store @ngrx/effects @ngrx/store-devtools
npm install ngx-toastr @angular/animations
npm install ngx-markdown socket.io-client
npm install @sentry/angular ngx-logger
```

### Full Enterprise Stack
```bash
ng add @angular/material
npm install @ngrx/store @ngrx/effects @ngrx/store-devtools @ngrx/entity
npm install @auth0/auth0-angular
npm install ngx-toastr @angular/animations
npm install ngx-markdown socket.io-client
npm install @ngx-translate/core @ngx-translate/http-loader
npm install @sentry/angular ngx-logger
npm install @ngx-formly/core @ngx-formly/material
npm install --save-dev cypress
```

---

## 📦 All Libraries by Category

### 1️⃣ UI Component Libraries

```bash
# Angular Material (Recommended)
ng add @angular/material

# PrimeNG (80+ components)
npm install primeng primeicons

# Ant Design
npm install ng-zorro-antd

# Bootstrap
npm install @ng-bootstrap/ng-bootstrap
```

### 2️⃣ State Management

```bash
# NgRx (Redux pattern)
npm install @ngrx/store @ngrx/effects @ngrx/store-devtools @ngrx/entity

# Akita (Simpler)
npm install @datorama/akita

# NGXS
npm install @ngxs/store @ngxs/devtools-plugin
```

### 3️⃣ Authentication

```bash
# Auth0
npm install @auth0/auth0-angular

# Firebase
npm install @angular/fire

# Keycloak
npm install keycloak-angular keycloak-js

# AWS Amplify
npm install @aws-amplify/ui-angular aws-amplify
```

### 4️⃣ Real-time Communication

```bash
# Socket.io
npm install socket.io-client @types/socket.io-client

# SignalR (for .NET)
npm install @microsoft/signalr

# RxJS WebSocket (built-in)
# Already included in Angular
```

### 5️⃣ Notifications

```bash
# NGX Toastr
npm install ngx-toastr @angular/animations

# Sweetalert2
npm install sweetalert2

# Angular Material Snackbar
# Included with Angular Material
```

### 6️⃣ Forms

```bash
# NGX Formly
npm install @ngx-formly/core @ngx-formly/material

# RxWeb Validators
npm install @rxweb/reactive-form-validators
```

### 7️⃣ Data Tables

```bash
# AG Grid (Best for enterprise)
npm install ag-grid-angular ag-grid-community

# NGX DataTable
npm install @swimlane/ngx-datatable

# PrimeNG Table
# Included with PrimeNG
```

### 8️⃣ Charts & Visualization

```bash
# Chart.js
npm install chart.js ng2-charts

# NGX Charts
npm install @swimlane/ngx-charts

# Highcharts
npm install highcharts highcharts-angular

# Plotly
npm install plotly.js-dist-min angular-plotly.js
```

### 9️⃣ File Upload

```bash
# NGX File Drop
npm install ngx-file-drop

# NG2 File Upload
npm install ng2-file-upload
```

### 🔟 Date & Time

```bash
# Date-fns
npm install date-fns ngx-date-fns

# Luxon
npm install luxon

# Day.js
npm install dayjs
```

### 1️⃣1️⃣ Internationalization

```bash
# NGX Translate
npm install @ngx-translate/core @ngx-translate/http-loader

# Transloco
npm install @ngneat/transloco
```

### 1️⃣2️⃣ Markdown & Rich Text

```bash
# NGX Markdown
npm install ngx-markdown

# Marked.js
npm install marked @types/marked

# Quill Editor
npm install ngx-quill quill
```

### 1️⃣3️⃣ Syntax Highlighting

```bash
# Highlight.js
npm install highlight.js

# Prism.js
npm install prismjs
```

### 1️⃣4️⃣ Logging

```bash
# NGX Logger
npm install ngx-logger

# Console Pro
npm install console-pro
```

### 1️⃣5️⃣ Error Tracking

```bash
# Sentry
npm install @sentry/angular

# LogRocket
npm install logrocket

# Bugsnag
npm install @bugsnag/js @bugsnag/plugin-angular
```

### 1️⃣6️⃣ Testing

```bash
# Cypress (E2E)
npm install --save-dev cypress

# Playwright
npm install --save-dev @playwright/test

# Jest (Unit)
npm install --save-dev jest @types/jest
```

### 1️⃣7️⃣ Utilities

```bash
# Lodash
npm install lodash @types/lodash

# RxJS Extensions
npm install rxjs-etc

# Utility Types
npm install utility-types
```

### 1️⃣8️⃣ Security

```bash
# DOMPurify
npm install dompurify @types/dompurify

# Crypto-JS
npm install crypto-js @types/crypto-js
```

### 1️⃣9️⃣ HTTP & API

```bash
# Axios
npm install axios

# Apollo Client (GraphQL)
npm install @apollo/client graphql apollo-angular
```

### 2️⃣0️⃣ Performance

```bash
# Angular CDK
ng add @angular/cdk

# NGX Quicklink
npm install ngx-quicklink

# Web Vitals
npm install web-vitals
```

---

## 🎯 Recommended for YOUR Chatbot

### Phase 1 (This Week)
```bash
ng add @angular/material
npm install ngx-toastr @angular/animations
npm install ngx-markdown
```

### Phase 2 (Next Week)
```bash
npm install socket.io-client @types/socket.io-client
npm install @sentry/angular
npm install ngx-logger
```

### Phase 3 (Production)
```bash
npm install @ngrx/store @ngrx/effects @ngrx/store-devtools
npm install @auth0/auth0-angular
npm install @ngx-translate/core @ngx-translate/http-loader
npm install --save-dev cypress
```

---

## 🚀 Automated Installation

### Use the PowerShell Script
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship\Internship
.\install-enterprise-stack.ps1
```

Choose:
- **Option 1**: Minimal (Quick start)
- **Option 2**: Standard (Recommended)
- **Option 3**: Full Enterprise (All features)
- **Option 4**: Custom (Pick what you need)

---

## 📊 Bundle Size Comparison

| Library | Size (gzipped) | Impact |
|---------|---------------|--------|
| Angular Material | ~150 KB | Medium |
| NgRx | ~20 KB | Low |
| Socket.io | ~60 KB | Medium |
| NGX Toastr | ~10 KB | Low |
| Chart.js | ~55 KB | Medium |
| AG Grid | ~200 KB | High |
| Lodash | ~70 KB | Medium (use lodash-es) |

---

## ⚠️ Important Notes

### Version Compatibility
Always check compatibility with Angular 17:
```bash
npm info <package-name> peerDependencies
```

### Tree Shaking
Import only what you need:
```typescript
// ❌ Bad - imports entire library
import _ from 'lodash';

// ✅ Good - imports only what's needed
import debounce from 'lodash-es/debounce';
```

### Lazy Loading
Load heavy modules only when needed:
```typescript
{
  path: 'admin',
  loadChildren: () => import('./admin/admin.module').then(m => m.AdminModule)
}
```

---

## 📖 Documentation Links

- **Angular Material**: https://material.angular.io
- **NgRx**: https://ngrx.io
- **PrimeNG**: https://primeng.org
- **Socket.io**: https://socket.io/docs
- **Auth0 Angular**: https://auth0.com/docs/quickstart/spa/angular
- **Sentry**: https://docs.sentry.io/platforms/javascript/guides/angular/
- **Cypress**: https://www.cypress.io
- **NGX Translate**: https://github.com/ngx-translate/core

---

## 🆘 Need Help?

1. **Check the detailed guide**: `ENTERPRISE_LIBRARIES.md`
2. **Read library docs**: See links above
3. **Search Stack Overflow**: Tag: `angular` + library name
4. **GitHub Issues**: Most libraries have active issue trackers
5. **Angular Discord**: https://discord.gg/angular

---

## 🔍 How to Choose?

### Questions to Ask:
1. **How large is my team?** → Larger teams need NgRx
2. **Do I need real-time?** → Use Socket.io
3. **International app?** → Add NGX Translate
4. **Need beautiful UI?** → Angular Material
5. **Complex data grids?** → AG Grid
6. **Production monitoring?** → Sentry + NGX Logger

### Decision Tree:
```
Start with:
  └─ Angular Material (UI)
     └─ NGX Toastr (Notifications)
        └─ Do you need real-time chat?
           ├─ YES → Socket.io
           └─ NO → Continue
              └─ Do you have complex state?
                 ├─ YES → NgRx
                 └─ NO → Use Signals
                    └─ Need authentication?
                       ├─ YES → Auth0
                       └─ NO → Done!
```

---

**Happy coding! 🚀**

