# 🐛 ANGULAR CHATBOT - DEBUGGING GUIDE

## Quick Reference

### 🚀 Start Debugging
```powershell
cd C:\Users\uppin\OneDrive\Desktop\internship\Internship
npm start
```
Press **F12** in browser → Sources tab → Set breakpoints

---

## VS Code Debugging (Professional Method)

### Setup (One-Time)
✅ Already configured! File created: `.vscode/launch.json`

### How to Use:
1. **Start the app**: `npm start` in terminal
2. **Set breakpoints**: Click left of line numbers in `.ts` files
3. **Start debugging**: Press **F5**
4. **Select**: "Debug Angular in Chrome"

### Debug Controls:
- **F5** - Start/Continue
- **F10** - Step Over (next line)
- **F11** - Step Into (enter function)
- **Shift+F11** - Step Out
- **Ctrl+Shift+F5** - Restart
- **Shift+F5** - Stop

---

## Adding Console Logs (Quick Method)

### Example 1: Debug sendMessage Flow

Add to `src/app/services/chat.service.ts`:

```typescript
async sendMessage(content: string): Promise<void> {
  console.log('🚀 [CHAT] sendMessage called with:', content);
  
  const current = this.currentConversationSignal();
  console.log('📊 [CHAT] Current conversation:', current?.id);
  
  if (!current) {
    console.error('❌ [CHAT] No current conversation!');
    return;
  }

  // Add user message
  const userMessage: Message = {
    id: this.generateId(),
    content,
    role: 'user',
    timestamp: new Date()
  };
  console.log('✅ [CHAT] Created user message:', userMessage);

  this.addMessageToConversation(current.id, userMessage);
  console.log('💾 [CHAT] Added message to conversation');

  // ... rest of code
}
```

### Example 2: Debug Authentication

Add to `src/app/services/auth.service.ts`:

```typescript
login(email: string, password: string): boolean {
  console.group('🔐 LOGIN ATTEMPT');
  console.log('Email:', email);
  console.log('Password length:', password.length);
  
  const isValid = this.validateCredentials(email, password);
  console.log('Validation result:', isValid);
  
  if (isValid) {
    console.log('✅ Login successful - saving to localStorage');
    localStorage.setItem('currentUser', JSON.stringify({ email }));
  } else {
    console.error('❌ Login failed - invalid credentials');
  }
  
  console.groupEnd();
  return isValid;
}
```

### Example 3: Debug Component Lifecycle

Add to any component (e.g., `chat-area.component.ts`):

```typescript
ngOnInit() {
  console.log('🎬 [COMPONENT] Chat Area initialized');
  console.log('📦 [COMPONENT] Initial messages:', this.messages());
}

ngAfterViewChecked() {
  console.log('👁️ [COMPONENT] View checked');
}

ngOnDestroy() {
  console.log('💀 [COMPONENT] Chat Area destroyed');
}
```

---

## Common Debugging Scenarios

### 🔍 Problem: Messages Not Appearing

**Add these logs:**
```typescript
// In sendMessage()
console.log('Current conversation before add:', this.currentConversationSignal());
console.log('Messages count:', current.messages.length);

// After adding
console.log('Messages count after add:', updated.messages.length);
```

**Check:**
1. Is `currentConversation` null?
2. Are messages being added to the array?
3. Is localStorage saving correctly?

### 🔍 Problem: Login Not Working

**Add these logs:**
```typescript
// In AuthService
console.log('Attempting login...');
console.log('Email format valid:', this.isValidEmail(email));
console.log('Password length:', password.length);
console.log('LocalStorage after login:', localStorage.getItem('currentUser'));
```

**Check:**
1. Is email validation passing?
2. Is password meeting requirements?
3. Is data saved to localStorage?

### 🔍 Problem: Router Not Navigating

**Add these logs:**
```typescript
// In component
constructor(private router: Router) {
  console.log('Router instance:', this.router);
}

navigateToChat() {
  console.log('Attempting to navigate to /chat');
  this.router.navigate(['/chat']).then(success => {
    console.log('Navigation success:', success);
  });
}
```

---

## Browser DevTools Features

### 1. Network Tab
- See all HTTP requests
- Check if API calls are failing
- View request/response data

**How to use:**
1. Open DevTools (F12) → Network tab
2. Clear (🚫 icon)
3. Interact with app
4. Click requests to see details

### 2. Application Tab
- View localStorage data
- Check cookies
- Inspect IndexedDB

**Check localStorage:**
1. DevTools → Application tab
2. Left sidebar → Local Storage → http://localhost:4200
3. See `conversations` and `currentUser` data

### 3. Console Tab
- View all console.log() output
- Filter by level (Info, Warnings, Errors)
- Run JavaScript commands

**Useful commands:**
```javascript
// In browser console
localStorage.getItem('conversations')  // View stored conversations
localStorage.clear()                    // Clear all data
angular.getComponent($0)                // Get Angular component (when element selected)
```

### 4. Sources Tab
- Set breakpoints in TypeScript
- Step through code execution
- Watch variables

**How to set breakpoints:**
1. Sources tab → webpack:// → src/app/
2. Open any .ts file
3. Click line number to set breakpoint (blue marker)
4. Interact with app → execution pauses

---

## Angular DevTools (Install Extension)

### Installation:
1. Chrome Web Store → Search "Angular DevTools"
2. Click "Add to Chrome"
3. Restart browser

### Features:
- **Component Explorer**: See component tree
- **Profiler**: Find performance issues
- **Injector Tree**: Debug dependency injection
- **Change Detection**: Track updates

**How to use:**
1. Open your app
2. F12 → Click "Angular" tab
3. Explore components and their properties

---

## Debugging TypeScript Errors

### In Terminal:
When running `npm start`, watch for errors:

```
ERROR in src/app/services/chat.service.ts:65:5
  Property 'someMethod' does not exist on type 'ChatService'
```

### In VS Code:
1. Open Problems panel: **Ctrl+Shift+M**
2. See all TypeScript errors
3. Click to jump to error location

---

## Advanced Debugging Techniques

### 1. Conditional Breakpoints
- Right-click line number → "Add conditional breakpoint"
- Only breaks when condition is true
- Example: `message.role === 'assistant'`

### 2. Logpoints
- Right-click line number → "Add logpoint"
- Logs message without stopping execution
- Example: `"Message sent:", message`

### 3. Watch Expressions
- In Debug panel, add expressions to watch
- See their values update in real-time
- Example: `this.conversations().length`

### 4. Call Stack
- See the path of function calls that led to current line
- Click entries to jump to that function
- Helps understand flow of execution

---

## Performance Debugging

### Check Change Detection:
```typescript
// In component
ngDoCheck() {
  console.count('Change detection ran');
}
```

### Measure Execution Time:
```typescript
console.time('sendMessage');
await this.chatService.sendMessage(content);
console.timeEnd('sendMessage');
// Output: sendMessage: 1542.3ms
```

### Profile Memory:
1. DevTools → Memory tab
2. Take heap snapshot
3. Compare snapshots to find memory leaks

---

## Common Issues & Solutions

### Issue: "Cannot read property of undefined"
**Debug:**
```typescript
console.log('Variable:', myVar);  // Check if it's undefined
console.log('Type:', typeof myVar);
```

### Issue: "Expression has changed after it was checked"
**Debug:**
```typescript
// Use setTimeout to defer update
setTimeout(() => {
  this.updateValue();
}, 0);
```

### Issue: Router not working
**Check:**
1. Is route defined in `app.routes.ts`?
2. Is RouterModule imported?
3. Console: `this.router.config` to see all routes

---

## Quick Debug Checklist

✅ **Before debugging:**
- [ ] Clear browser cache (Ctrl+Shift+Del)
- [ ] Check browser console for errors
- [ ] Verify `npm start` is running without errors
- [ ] Check Network tab for failed requests

✅ **While debugging:**
- [ ] Add console.logs at key points
- [ ] Use breakpoints to pause execution
- [ ] Check localStorage for data persistence
- [ ] Verify component lifecycle hooks are firing

✅ **After fixing:**
- [ ] Remove debug console.logs
- [ ] Test in different scenarios
- [ ] Clear localStorage and test fresh state
- [ ] Check for console warnings

---

## Keyboard Shortcuts Summary

### VS Code:
- **F5** - Start debugging
- **F9** - Toggle breakpoint
- **F10** - Step over
- **F11** - Step into
- **Ctrl+Shift+M** - Problems panel
- **Ctrl+`** - Toggle terminal

### Browser DevTools:
- **F12** - Open/close DevTools
- **Ctrl+Shift+C** - Inspect element
- **Ctrl+Shift+J** - Open Console
- **F8** - Resume/pause
- **F10** - Step over
- **F11** - Step into

---

## Need More Help?

### Check These Files:
- `SETUP_GUIDE.md` - Setup instructions
- `FEATURES.md` - Feature documentation
- `README.md` - General overview

### Look at Console:
- Red text = Errors
- Yellow text = Warnings
- Blue text = Info

### Test in Clean State:
```javascript
// In browser console
localStorage.clear();
location.reload();
```

---

**Happy Debugging! 🐛🔧**

