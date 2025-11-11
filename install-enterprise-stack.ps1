# Enterprise Stack Installation Script for Angular Chatbot
# Run this in PowerShell from the Internship directory

Write-Host "🏢 Enterprise Stack Installer for Angular Chatbot" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json not found!" -ForegroundColor Red
    Write-Host "Please run this script from the Internship directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "Select installation profile:" -ForegroundColor Yellow
Write-Host "1. Minimal (Material UI + Toastr + Markdown)" -ForegroundColor Green
Write-Host "2. Standard (Minimal + State Management + Real-time)" -ForegroundColor Green
Write-Host "3. Full Enterprise (Everything + Auth + Logging + Testing)" -ForegroundColor Green
Write-Host "4. Custom (Choose individual packages)" -ForegroundColor Green
Write-Host ""

$choice = Read-Host "Enter choice (1-4)"

switch ($choice) {
    "1" {
        Write-Host "`n📦 Installing Minimal Stack..." -ForegroundColor Cyan
        
        Write-Host "`n1/4 Installing Angular Material..." -ForegroundColor Yellow
        ng add @angular/material --skip-confirmation
        
        Write-Host "`n2/4 Installing Toastr..." -ForegroundColor Yellow
        npm install ngx-toastr @angular/animations
        
        Write-Host "`n3/4 Installing Better Markdown..." -ForegroundColor Yellow
        npm install ngx-markdown
        
        Write-Host "`n4/4 Installing Error Tracking..." -ForegroundColor Yellow
        npm install @sentry/angular
        
        Write-Host "`n✅ Minimal stack installed!" -ForegroundColor Green
    }
    
    "2" {
        Write-Host "`n📦 Installing Standard Stack..." -ForegroundColor Cyan
        
        Write-Host "`n1/7 Installing Angular Material..." -ForegroundColor Yellow
        ng add @angular/material --skip-confirmation
        
        Write-Host "`n2/7 Installing Toastr..." -ForegroundColor Yellow
        npm install ngx-toastr @angular/animations
        
        Write-Host "`n3/7 Installing Better Markdown..." -ForegroundColor Yellow
        npm install ngx-markdown
        
        Write-Host "`n4/7 Installing State Management (NgRx)..." -ForegroundColor Yellow
        npm install @ngrx/store @ngrx/effects @ngrx/store-devtools
        
        Write-Host "`n5/7 Installing Real-time (Socket.io)..." -ForegroundColor Yellow
        npm install socket.io-client @types/socket.io-client
        
        Write-Host "`n6/7 Installing Error Tracking..." -ForegroundColor Yellow
        npm install @sentry/angular
        
        Write-Host "`n7/7 Installing Logger..." -ForegroundColor Yellow
        npm install ngx-logger
        
        Write-Host "`n✅ Standard stack installed!" -ForegroundColor Green
    }
    
    "3" {
        Write-Host "`n📦 Installing Full Enterprise Stack..." -ForegroundColor Cyan
        Write-Host "⏱️  This will take 5-10 minutes..." -ForegroundColor Yellow
        
        Write-Host "`n1/11 Installing Angular Material..." -ForegroundColor Yellow
        ng add @angular/material --skip-confirmation
        
        Write-Host "`n2/11 Installing Toastr..." -ForegroundColor Yellow
        npm install ngx-toastr @angular/animations
        
        Write-Host "`n3/11 Installing Better Markdown..." -ForegroundColor Yellow
        npm install ngx-markdown
        
        Write-Host "`n4/11 Installing State Management (NgRx)..." -ForegroundColor Yellow
        npm install @ngrx/store @ngrx/effects @ngrx/store-devtools @ngrx/entity
        
        Write-Host "`n5/11 Installing Real-time (Socket.io)..." -ForegroundColor Yellow
        npm install socket.io-client @types/socket.io-client
        
        Write-Host "`n6/11 Installing Authentication (Auth0)..." -ForegroundColor Yellow
        npm install @auth0/auth0-angular
        
        Write-Host "`n7/11 Installing Internationalization..." -ForegroundColor Yellow
        npm install @ngx-translate/core @ngx-translate/http-loader
        
        Write-Host "`n8/11 Installing Error Tracking..." -ForegroundColor Yellow
        npm install @sentry/angular
        
        Write-Host "`n9/11 Installing Logger..." -ForegroundColor Yellow
        npm install ngx-logger
        
        Write-Host "`n10/11 Installing Advanced Forms..." -ForegroundColor Yellow
        npm install @ngx-formly/core @ngx-formly/material
        
        Write-Host "`n11/11 Installing Testing (Cypress)..." -ForegroundColor Yellow
        npm install --save-dev cypress
        
        Write-Host "`n✅ Full enterprise stack installed!" -ForegroundColor Green
    }
    
    "4" {
        Write-Host "`n📦 Custom Installation..." -ForegroundColor Cyan
        Write-Host ""
        
        $packages = @()
        
        # UI Framework
        Write-Host "Install Angular Material? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            Write-Host "Installing Angular Material..." -ForegroundColor Green
            ng add @angular/material --skip-confirmation
        }
        
        # State Management
        Write-Host "Install NgRx (State Management)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "@ngrx/store @ngrx/effects @ngrx/store-devtools"
        }
        
        # Real-time
        Write-Host "Install Socket.io (Real-time)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "socket.io-client @types/socket.io-client"
        }
        
        # Notifications
        Write-Host "Install Toastr (Notifications)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "ngx-toastr @angular/animations"
        }
        
        # Markdown
        Write-Host "Install Better Markdown? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "ngx-markdown"
        }
        
        # Auth
        Write-Host "Install Auth0 (Authentication)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "@auth0/auth0-angular"
        }
        
        # i18n
        Write-Host "Install NGX-Translate (Internationalization)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "@ngx-translate/core @ngx-translate/http-loader"
        }
        
        # Logging
        Write-Host "Install NGX-Logger? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "ngx-logger"
        }
        
        # Error Tracking
        Write-Host "Install Sentry (Error Tracking)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "@sentry/angular"
        }
        
        # Forms
        Write-Host "Install NGX-Formly (Advanced Forms)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "@ngx-formly/core @ngx-formly/material"
        }
        
        # Testing
        Write-Host "Install Cypress (E2E Testing)? (y/n)" -ForegroundColor Yellow
        if ((Read-Host) -eq "y") { 
            $packages += "cypress"
        }
        
        if ($packages.Count -gt 0) {
            Write-Host "`nInstalling selected packages..." -ForegroundColor Cyan
            $packageString = $packages -join " "
            npm install $packageString
            Write-Host "`n✅ Custom packages installed!" -ForegroundColor Green
        } else {
            Write-Host "`n❌ No packages selected" -ForegroundColor Red
        }
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "🎉 Installation Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Read ENTERPRISE_LIBRARIES.md for configuration" -ForegroundColor White
Write-Host "2. Update app.config.ts with providers" -ForegroundColor White
Write-Host "3. Start using the new libraries!" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Run 'npm start' to test your app" -ForegroundColor Cyan

