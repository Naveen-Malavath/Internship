# 🚀 Complete Setup Guide

Step-by-step guide to get your AI Shopping Assistant up and running.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

### Required Software

1. **Node.js** (v18 or higher)
   ```bash
   # Check your version
   node --version
   
   # Should output: v18.x.x or higher
   ```
   
   **Download**: https://nodejs.org/

2. **npm** (v9 or higher)
   ```bash
   # Check your version
   npm --version
   
   # Should output: 9.x.x or higher
   ```
   
   **Note**: npm comes with Node.js

3. **Angular CLI** (optional but recommended)
   ```bash
   # Install globally
   npm install -g @angular/cli
   
   # Check version
   ng version
   ```

### Optional Software

- **VS Code**: Recommended IDE
- **Git**: For version control
- **Chrome/Firefox**: For development

---

## 🔧 Installation

### Step 1: Navigate to Project Directory

```bash
cd /path/to/project
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install:
- Angular framework (v17)
- TypeScript (v5.2)
- RxJS (v7.8)
- Marked.js (markdown parser)
- Highlight.js (code highlighting)
- All other dependencies

**Expected output:**
```
added 1234 packages in 45s
```

**Troubleshooting:**
- If you get errors, try: `npm install --legacy-peer-deps`
- If node_modules exists: `rm -rf node_modules package-lock.json && npm install`

### Step 3: Verify Installation

Check that everything is installed correctly:

```bash
# List installed packages
npm list --depth=0

# Should show Angular, TypeScript, etc.
```

---

## 🎯 Running the Application

### Development Server

```bash
npm start
```

Or:

```bash
ng serve
```

**What happens:**
1. Angular compiles the application
2. Development server starts
3. Opens on http://localhost:4200
4. Auto-reloads on file changes

**Expected output:**
```
✔ Browser application bundle generation complete.
✔ Compiled successfully.
** Angular Live Development Server is listening on localhost:4200 **
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:4200
```

You should see the welcome screen with:
- "How can I help you today?" heading
- 4 suggested prompt cards
- Input box at the bottom

---

## 🎨 Using the Application

### First Steps

1. **Start a Conversation**
   - Click any suggested prompt card, OR
   - Type your own question in the input box
   - Press Enter or click send button

2. **Example Queries**
   ```
   "Show me the best laptops for programming"
   "I need wireless headphones under $400"
   "Where can I learn web development?"
   "What are the best streaming platforms?"
   ```

3. **Explore Features**
   - Create new chat (New chat button)
   - Switch between conversations (sidebar)
   - Copy responses (copy button)
   - Toggle dark mode (theme button)

### Understanding the Interface

#### Sidebar (Left)
- **New chat button**: Start fresh conversation
- **Conversation list**: All your chats
- **Clear conversations**: Delete all
- **Theme toggle**: Light/Dark mode

#### Main Area (Right)
- **Welcome screen**: Shows on first visit
- **Messages**: User and assistant bubbles
- **Input box**: Type your queries here
- **Send button**: Submit your message

---

## 🛠️ Customization

### Adding Your Own Products

1. **Open** `src/app/services/ai.service.ts`

2. **Find** the `products` array (around line 20)

3. **Add** your product:
```typescript
{
  id: '11',
  name: 'Your Product Name',
  category: 'Category > Subcategory',
  url: 'https://your-product-url.com',
  description: 'Detailed description of your product...',
  price: '$999',
  rating: 4.5,
  keywords: ['keyword1', 'keyword2', 'keyword3']
}
```

4. **Save** the file (app will auto-reload)

### Adding Your Own Websites

1. **Open** `src/app/services/ai.service.ts`

2. **Find** the `websites` array (around line 80)

3. **Add** your website:
```typescript
{
  id: '13',
  name: 'Your Website Name',
  url: 'https://your-website.com',
  description: 'What your website offers...',
  category: 'Category',
  features: ['Feature 1', 'Feature 2', 'Feature 3'],
  keywords: ['keyword1', 'keyword2', 'keyword3']
}
```

4. **Save** the file

### Changing Colors

1. **Open** `src/styles.css`

2. **Find** the `:root` section (light theme)

3. **Modify** colors:
```css
:root {
  --bg-primary: #your-color;
  --accent-primary: #your-accent;
  /* ... more variables */
}
```

4. **For dark theme**, modify `[data-theme="dark"]` section

### Changing Suggested Prompts

1. **Open** `src/app/components/chat-area/chat-area.component.ts`

2. **Find** `suggestedPrompts` array

3. **Modify** or add prompts:
```typescript
{
  icon: '🎯',
  title: 'Your Title',
  prompt: 'The full question that will be sent'
}
```

---

## 📦 Building for Production

### Create Production Build

```bash
npm run build
```

Or:

```bash
ng build --configuration production
```

**What happens:**
- Creates optimized bundle
- Minifies code
- Removes development code
- Outputs to `dist/` directory

**Expected output:**
```
✔ Browser application bundle generation complete.
✔ Copying assets complete.
✔ Index html generation complete.

Initial Chunk Files   | Names         |  Raw Size
main.js              | main          | 250.42 kB | 
polyfills.js         | polyfills     |  33.08 kB | 
styles.css           | styles        |  15.23 kB | 

Build at: 2025-11-04T10:30:00.000Z - Hash: 1234567890abcdef
```

### Test Production Build Locally

```bash
# Install http-server (if not already installed)
npm install -g http-server

# Serve the production build
cd dist/chatbot-framework
http-server

# Open http://localhost:8080 in your browser
```

---

## 🚀 Deployment

### Option 1: Netlify (Easiest)

1. **Build the app**:
   ```bash
   npm run build
   ```

2. **Go to** https://app.netlify.com/

3. **Drag and drop** the `dist/chatbot-framework` folder

4. **Done!** Your site is live

### Option 2: Vercel

1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```

2. **Deploy**:
   ```bash
   npm run build
   cd dist/chatbot-framework
   vercel --prod
   ```

3. **Follow prompts** to complete deployment

### Option 3: GitHub Pages

1. **Install gh-pages**:
   ```bash
   npm install -g angular-cli-ghpages
   ```

2. **Build and deploy**:
   ```bash
   ng build --configuration production --base-href /repo-name/
   npx angular-cli-ghpages --dir=dist/chatbot-framework
   ```

### Option 4: Firebase Hosting

1. **Install Firebase CLI**:
   ```bash
   npm install -g firebase-tools
   ```

2. **Login**:
   ```bash
   firebase login
   ```

3. **Initialize**:
   ```bash
   firebase init hosting
   ```

4. **Deploy**:
   ```bash
   npm run build
   firebase deploy
   ```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Error**: `Port 4200 is already in use`

**Solution**:
```bash
# Use a different port
ng serve --port 4300

# Or kill the process using port 4200
# Windows
netstat -ano | findstr :4200
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:4200 | xargs kill
```

#### 2. Module Not Found

**Error**: `Cannot find module '@angular/core'`

**Solution**:
```bash
# Delete and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### 3. TypeScript Errors

**Error**: `TS2304: Cannot find name...`

**Solution**:
```bash
# Check TypeScript version
npm list typescript

# Reinstall if needed
npm install typescript@~5.2.2
```

#### 4. Build Fails

**Error**: Various build errors

**Solution**:
```bash
# Clear Angular cache
rm -rf .angular

# Clear node modules
rm -rf node_modules package-lock.json

# Reinstall
npm install

# Try building again
npm run build
```

#### 5. Slow Performance

**Problem**: App runs slowly

**Solutions**:
- Clear browser cache
- Disable browser extensions
- Use production build
- Check for console errors
- Clear LocalStorage: `localStorage.clear()`

#### 6. Dark Mode Not Working

**Problem**: Theme doesn't change

**Solutions**:
- Check browser console for errors
- Clear LocalStorage
- Hard refresh (Ctrl+Shift+R)
- Check CSS is loading

---

## 🔍 Verification Checklist

After setup, verify these work:

### Basic Functionality
- [ ] App loads without errors
- [ ] Welcome screen displays
- [ ] Can send messages
- [ ] Bot responds to messages
- [ ] Messages display correctly

### Features
- [ ] Sidebar opens/closes
- [ ] New chat creates conversation
- [ ] Can switch between chats
- [ ] Can delete conversations
- [ ] Dark mode toggle works
- [ ] Copy button works
- [ ] Links are clickable

### UI/UX
- [ ] Responsive on mobile
- [ ] Smooth animations
- [ ] Proper spacing
- [ ] Readable fonts
- [ ] Icons display correctly

### Data
- [ ] Conversations persist on reload
- [ ] Theme persists on reload
- [ ] LocalStorage works
- [ ] Clear all works

---

## 📊 Performance Tips

### Development

```bash
# Disable source maps for faster builds
ng serve --source-map=false

# Use Ahead-of-Time compilation
ng serve --aot

# Optimize with production config
ng serve --configuration production
```

### Production

```bash
# Enable all optimizations
ng build --configuration production

# Analyze bundle size
npm install -g webpack-bundle-analyzer
ng build --stats-json
webpack-bundle-analyzer dist/chatbot-framework/stats.json
```

---

## 🔐 Security Checklist

Before deploying:

- [ ] No API keys in code
- [ ] All user input sanitized
- [ ] External links open in new tabs
- [ ] HTTPS enabled on production
- [ ] Content Security Policy configured
- [ ] No console.log in production

---

## 📱 Browser Compatibility

Tested and working on:

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+

Mobile browsers:
- ✅ Chrome Mobile
- ✅ Safari iOS
- ✅ Samsung Internet
- ✅ Firefox Mobile

---

## 💾 Backup & Restore

### Backup Conversations

**Manual** (Browser):
1. Open browser console (F12)
2. Run: `JSON.stringify(localStorage.getItem('conversations'))`
3. Copy output and save to file

**Restore**:
1. Open console
2. Run: `localStorage.setItem('conversations', 'paste-your-data-here')`
3. Refresh page

### Export Feature (Future)

Coming soon:
- Export to JSON
- Export to PDF
- Import from backup
- Cloud sync

---

## 🆘 Getting Help

### Resources

- **Documentation**: README.md, FEATURES.md
- **Issues**: Check existing issues
- **Updates**: See CHANGELOG.md

### Support Channels

1. **GitHub Issues**: Open an issue with:
   - Error message
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable

2. **Community**: Discussion forum (if available)

3. **Email**: support@example.com (if provided)

---

## ✅ Next Steps

After successful setup:

1. **Explore** all features
2. **Customize** with your data
3. **Test** thoroughly
4. **Deploy** to production
5. **Share** with users
6. **Collect** feedback
7. **Iterate** and improve

---

## 🎓 Learning Resources

### Angular
- Official Docs: https://angular.io/docs
- Angular University: https://angular-university.io/
- YouTube: Angular Tutorials

### TypeScript
- Official Docs: https://www.typescriptlang.org/docs/
- TypeScript Deep Dive: https://basarat.gitbook.io/typescript/

### RxJS
- Official Docs: https://rxjs.dev/
- Learn RxJS: https://www.learnrxjs.io/

---

**Congratulations! Your AI Shopping Assistant is ready to use! 🎉**

For any questions, refer to README.md or open an issue.

Happy coding! 🚀


