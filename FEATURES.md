# 🌟 Features Documentation

Comprehensive guide to all features in the AI Shopping Assistant.

## Table of Contents
1. [User Interface](#user-interface)
2. [Conversation Management](#conversation-management)
3. [Chat Features](#chat-features)
4. [Product Discovery](#product-discovery)
5. [Website Recommendations](#website-recommendations)
6. [Theming](#theming)
7. [Data Persistence](#data-persistence)
8. [Advanced Features](#advanced-features)

---

## 1. User Interface

### ChatGPT-Inspired Design
- **Clean Layout**: Minimalist, distraction-free interface
- **Professional Look**: Modern design matching industry standards
- **Intuitive Navigation**: Easy to understand and use
- **Responsive**: Works perfectly on all devices

### Sidebar Navigation
- **Width**: 280px (collapsible to 60px)
- **Sections**: Header, conversation list, footer
- **Quick Actions**: New chat, theme toggle, clear all
- **Visual Feedback**: Active state highlighting

### Main Chat Area
- **Welcome Screen**: Displayed on first visit
- **Suggested Prompts**: 4 quick-start cards
- **Message Display**: Alternating user/assistant bubbles
- **Input Box**: Fixed at bottom with send button

### Color Scheme

#### Light Theme
```css
Background Primary: #ffffff
Background Secondary: #f7f7f8
Text Primary: #2e3338
Accent: #10a37f
```

#### Dark Theme
```css
Background Primary: #212121
Background Secondary: #2f2f2f
Text Primary: #ececf1
Accent: #19c37d
```

---

## 2. Conversation Management

### Creating Conversations
- **Auto-Create**: First conversation created automatically
- **New Button**: Click "New chat" to start fresh
- **Welcome Message**: Each conversation starts with greeting
- **Title Generation**: Auto-generated from first user message

### Managing Conversations
- **Switch**: Click any conversation to view
- **Delete**: Hover and click trash icon
- **Clear All**: Remove all conversations at once
- **Reorder**: Newest conversations appear first

### Conversation List
- **Display**: Shows title and last update time
- **Active Indicator**: Highlighted current conversation
- **Date Format**: "Today", "Yesterday", "X days ago"
- **Icons**: Chat bubble icon for each conversation

### Data Structure
```typescript
interface Conversation {
  id: string;
  title: string;
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}
```

---

## 3. Chat Features

### Message Types

#### User Messages
- **Styling**: Light background, right-aligned
- **Avatar**: User icon (👤)
- **Format**: Plain text, pre-wrap
- **Width**: Auto-adjusts to content

#### Assistant Messages
- **Styling**: Slightly darker background, left-aligned
- **Avatar**: Robot icon (🤖)
- **Format**: Full markdown support
- **Width**: Full width available

### Markdown Support

#### Headers
```markdown
# H1 Header
## H2 Header
### H3 Header
```

#### Text Formatting
```markdown
**Bold text**
*Italic text*
~~Strikethrough~~
```

#### Lists
```markdown
- Bullet point 1
- Bullet point 2

1. Numbered item 1
2. Numbered item 2
```

#### Links
```markdown
[Link text](https://url.com)
```

#### Code

Inline code: `code here`

Code blocks:
```python
def function():
    return "value"
```

#### Blockquotes
```markdown
> This is a quote
```

#### Tables
```markdown
| Column 1 | Column 2 |
|----------|----------|
| Value 1  | Value 2  |
```

### Code Syntax Highlighting

Supported languages (180+):
- JavaScript/TypeScript
- Python
- Java
- C/C++/C#
- PHP
- Ruby
- Go
- Rust
- Swift
- Kotlin
- HTML/CSS
- SQL
- Shell/Bash
- And many more...

### Message Actions

#### Copy Message
- **Button**: Copy icon with text
- **Feedback**: Changes to checkmark when copied
- **Duration**: 2 seconds before reverting
- **Clipboard**: Uses native Clipboard API

#### Timestamp
- **Format**: 12-hour format (e.g., "2:30 PM")
- **Position**: Bottom right of message
- **Color**: Muted tertiary text

### Input Features

#### Textarea
- **Auto-resize**: Grows with content
- **Max Height**: 200px
- **Placeholder**: "Message AI Assistant..."
- **Disabled State**: When loading

#### Send Button
- **States**: Enabled, disabled, loading
- **Shortcut**: Enter key (Shift+Enter for new line)
- **Icon**: Paper airplane
- **Color**: Accent color when active

### Loading States

#### Typing Indicator
- **Display**: Three animated dots
- **Avatar**: Bot icon
- **Animation**: Sequential pulse effect
- **Position**: At bottom of messages

#### Streaming Cursor
- **Display**: Blinking cursor at end of text
- **Animation**: 1s blink interval
- **Purpose**: Shows message is being typed

---

## 4. Product Discovery

### Product Database

#### Current Products (10)
1. **MacBook Pro 16"** - $2,499 ⭐4.8
2. **iPhone 15 Pro** - $999 ⭐4.7
3. **Sony WH-1000XM5** - $399 ⭐4.9
4. **Nike Air Zoom Pegasus 40** - $130 ⭐4.6
5. **Breville Barista Express** - $699 ⭐4.7
6. **Kindle Paperwhite** - $139 ⭐4.6
7. **PlayStation 5** - $499 ⭐4.8
8. **Apple Watch Series 9** - $399 ⭐4.7
9. **Samsung 65" OLED TV** - $2,299 ⭐4.8
10. **Dyson V15 Detect** - $649 ⭐4.7

### Product Information

Each product includes:
- **Name**: Full product name
- **Category**: Hierarchical category (e.g., "Electronics > Computers")
- **Description**: Detailed product information
- **Price**: Current price
- **Rating**: Star rating out of 5
- **URL**: Direct link to product page
- **Keywords**: Search terms for matching

### Search Algorithm

#### Keyword Matching
```typescript
// Searches through:
1. Product keywords array
2. Product name (case-insensitive)
3. Product category
```

#### Ranking
- Exact matches ranked higher
- Multiple keyword matches boost ranking
- Returns top 5 results

### Product Display

#### Format
```markdown
## 🛍️ Product Recommendations

### 1. Product Name
**Category:** Electronics > Computers
**Price:** $2,499
**Rating:** ⭐⭐⭐⭐⭐ 4.8/5

Product description here...

🔗 [View Product Name](url)
```

---

## 5. Website Recommendations

### Website Database

#### Current Websites (12)
1. **Amazon** - E-commerce
2. **YouTube** - Entertainment
3. **GitHub** - Development
4. **Stack Overflow** - Development
5. **Netflix** - Entertainment
6. **LinkedIn** - Professional
7. **Udemy** - Education
8. **Reddit** - Social
9. **Figma** - Design
10. **Notion** - Productivity
11. **Coursera** - Education
12. **Medium** - Content

### Website Information

Each website includes:
- **Name**: Website name
- **URL**: Direct link
- **Description**: What the site offers
- **Category**: Type of website
- **Features**: Key features (array)
- **Keywords**: Search terms

### Website Display

#### Format
```markdown
## 🌐 Recommended Websites

### 1. Website Name
**Category:** Education

Description of what the website offers...

**Key Features:**
- ✓ Feature 1
- ✓ Feature 2
- ✓ Feature 3

🔗 [Visit Website Name](url)
```

---

## 6. Theming

### Theme Options

#### Light Mode
- Default theme
- High contrast
- Easy to read
- Professional appearance

#### Dark Mode
- Reduced eye strain
- Better for low-light
- Popular preference
- Energy-efficient on OLED

### Theme Detection

#### System Preference
```typescript
const prefersDark = window.matchMedia(
  '(prefers-color-scheme: dark)'
).matches;
```

#### Storage
```typescript
localStorage.setItem('theme', 'dark' | 'light');
```

### Theme Toggle

#### Location
- Sidebar footer
- Icon changes (sun/moon)
- Text label

#### Behavior
- Instant application
- Smooth transition
- Persisted across sessions

### CSS Variables

All colors defined as variables:
```css
:root {
  --bg-primary: #ffffff;
  --text-primary: #2e3338;
  /* ... */
}

[data-theme="dark"] {
  --bg-primary: #212121;
  --text-primary: #ececf1;
  /* ... */
}
```

---

## 7. Data Persistence

### LocalStorage

#### What's Saved
- All conversations
- Messages in each conversation
- Theme preference
- Timestamps

#### Storage Key
```typescript
'conversations' // Array of Conversation objects
'theme' // 'light' | 'dark'
```

### Automatic Saving

#### When Data Saves
- After each message
- On conversation create
- On conversation delete
- On theme change

### Data Loading

#### On App Start
1. Load conversations from storage
2. Parse JSON and convert dates
3. Set active conversation (first one)
4. Apply saved theme

### Data Management

#### Clear Data
- "Clear conversations" button
- Removes all from storage
- Creates new default conversation

#### Export (Future)
- JSON export functionality
- Backup conversations
- Import from backup

---

## 8. Advanced Features

### Responsive Design

#### Breakpoints
```css
Mobile: max-width 768px
Tablet: 769px - 1024px
Desktop: > 1024px
```

#### Mobile Adaptations
- Collapsible sidebar
- Smaller fonts
- Touch-friendly buttons
- Simplified layout

### Accessibility

#### Keyboard Navigation
- Tab through elements
- Enter to send message
- Escape to close modals

#### Screen Readers
- ARIA labels on buttons
- Semantic HTML
- Alt text for icons

#### Focus Indicators
- Visible focus states
- High contrast borders
- Skip to content links

### Performance Optimizations

#### Lazy Loading
- Components load on demand
- Reduced initial bundle size

#### Change Detection
- OnPush strategy where possible
- Reduced unnecessary renders

#### Virtual Scrolling (Future)
- For very long conversations
- Improved performance

### Error Handling

#### API Errors
- Graceful fallbacks
- User-friendly messages
- Retry mechanisms

#### Storage Errors
- Quota exceeded handling
- Corrupt data recovery
- Fallback to memory

### Security

#### XSS Protection
- DomSanitizer for HTML
- Escaped user input
- Safe link handling

#### Data Privacy
- All data client-side
- No tracking
- No external requests

---

## Feature Comparison

| Feature | Basic Version | ChatGPT Style |
|---------|---------------|---------------|
| **UI** |
| Interface | Simple | Professional |
| Sidebar | ❌ | ✅ |
| Welcome Screen | ❌ | ✅ |
| Suggested Prompts | Basic | Rich Cards |
| **Chat** |
| Markdown | ❌ | ✅ |
| Code Highlighting | ❌ | ✅ |
| Copy Messages | ❌ | ✅ |
| Streaming Effect | ❌ | ✅ |
| **Data** |
| Conversations | 1 | Unlimited |
| History | ❌ | ✅ |
| Persistence | ❌ | ✅ |
| Products | 8 | 10 |
| Websites | 8 | 12 |
| **Theme** |
| Light Mode | ✅ | ✅ |
| Dark Mode | ❌ | ✅ |
| Auto-detect | ❌ | ✅ |

---

## Usage Examples

### Example 1: Finding a Laptop
```
User: "I need a laptop for programming"

